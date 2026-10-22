"""Pipeline tests: daily.py / edit.py / overrides.py in a throwaway copy of the repo.

Fully synthetic (no network, no real data, no Hevy key). Run from the repo root:
    python tests/test_pipeline.py
Exit code 0 = all passed.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
work = Path(tempfile.mkdtemp(prefix="motus_test_"))
for name in ("daily.py", "edit.py", "overrides.py", "common.py", "check_status.py", "fetch_hevy.py", "weekly.py"):
    shutil.copy(ROOT / name, work / name)
(work / "inbox").mkdir()
(work / "history").mkdir()
(work / "overrides.json").write_text("{}\n", encoding="utf-8")

ENV = {**os.environ, "HEVY_API_KEY": "", "PYTHONUTF8": "1"}
fails, passes = [], 0
today = (datetime.utcnow() + timedelta(hours=3)).date()          # Riyadh date
D0, D1, D2 = (str(today - timedelta(days=n)) for n in (2, 1, 0))  # two days ago, yesterday, today


def check(name, cond, extra=""):
    global passes
    if cond:
        passes += 1
        print(f"  PASS  {name}")
    else:
        fails.append(name)
        print(f"  FAIL  {name} {extra}")


def run(script, **env):
    p = subprocess.run([sys.executable, script], cwd=work, env={**ENV, **env}, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def read(name):
    return json.loads((work / name).read_text(encoding="utf-8"))


def daily():
    rc, out = run("daily.py")
    assert rc == 0, out
    return read("data.json"), read("status.json")


def edit(action, date, metric, value="", note="", actor="owner", owner="owner"):
    return run("edit.py", EDIT_ACTION=action, EDIT_DATE=date, EDIT_METRIC=metric, EDIT_VALUE=value,
               EDIT_NOTE=note, EDIT_ACTOR=actor, REPO_OWNER=owner)


def health(name, steps=None, sleep_min=None):
    raw = {"stepCount": [{"date": d, "value": v} for d, v in (steps or {}).items()],
           "sleepTime": [{"date": d, "value": v, "stages": {}} for d, v in (sleep_min or {}).items()]}
    (work / "inbox" / name).write_text(json.dumps(raw), encoding="utf-8")


days = lambda d: d["days"]

print("setup: two days of history from an earlier upload")
health("health-2000-01-01-0000.json", steps={D0: 5000, D1: 6000}, sleep_min={D0: 420, D1: 480})
d0, _ = daily()
base = json.loads(json.dumps(days(d0)))
check("history loaded", base[D1]["steps"] == 6000 and base[D1]["sleep_hours"] == 8.0)

print("1. today's data arrives; history intact; no duplicates; quiet no-op runs")
health("health-2000-01-01-0800.json", steps={D2: 1234}, sleep_min={D2: 420})
d1, s1 = daily()
check("today has steps and sleep", days(d1)[D2]["steps"] == 1234 and days(d1)[D2]["sleep_hours"] == 7.0)
check("history unchanged", all(days(d1)[k] == base[k] for k in base))
check("exactly one new day", len(days(d1)) == len(base) + 1)
check("status records the upload time", s1["health"]["latest_upload"] == "2000-01-01T08:00:00+03:00", s1["health"])
text = (work / "data.json").read_text(encoding="utf-8")
daily()
check("a run with nothing new leaves data.json byte-identical", (work / "data.json").read_text(encoding="utf-8") == text)

print("2. edit and revert")
check("edit accepted", edit("set", D1, "sleep_hours", "7.0", "double counted")[0] == 0)
d2, s2 = daily()
r = days(d2)[D1]
check("corrected value shown, original kept", r["sleep_hours"] == 7.0 and r["orig"]["sleep_hours"] == 8.0)
check("other metrics and days untouched", r["steps"] == 6000 and days(d2)[D0] == base[D0])
check("status counts the correction", s2["corrections"] == 1)

print("3. correction survives sync; original keeps refreshing; revert restores latest automatic value")
health("health-2000-01-01-0900.json", sleep_min={D1: 540})                         # automatic value becomes 9.0 h
d3, _ = daily()
r = days(d3)[D1]
check("manual value still wins", r["sleep_hours"] == 7.0)
check("original refreshed underneath", r["orig"]["sleep_hours"] == 9.0, r)
check("repeat sync is stable", days(daily()[0]) == days(d3))
check("revert accepted", edit("revert", D1, "sleep_hours")[0] == 0)
d4, _ = daily()
check("revert restores 9.0 and removes the marker", days(d4)[D1]["sleep_hours"] == 9.0 and "orig" not in days(d4)[D1])
check("overrides.json empty again", read("overrides.json") == {})
check("reverting a non-corrected value is harmless", edit("revert", D1, "sleep_hours")[0] == 0)
edit("set", D0, "steps", "", "false positive")
d5, _ = daily()
check("empty value clears to no data, original kept", days(d5)[D0]["steps"] is None and days(d5)[D0]["orig"]["steps"] == 5000)
edit("revert", D0, "steps")
daily()

print("4. unauthorized / invalid requests are rejected")
before = (work / "overrides.json").read_text(encoding="utf-8")
cases = [
    ("someone else", dict(actor="mallory"), ("set", D1, "steps", "5")),
    ("no actor", dict(actor=""), ("set", D1, "steps", "5")),
    ("owner unset", dict(owner=""), ("set", D1, "steps", "5")),
    ("sleep 99 h", {}, ("set", D1, "sleep_hours", "99")),
    ("negative steps", {}, ("set", D1, "steps", "-5")),
    ("fractional steps", {}, ("set", D1, "steps", "1.5")),
    ("non-numeric", {}, ("set", D1, "steps", "abc")),
    ("infinity", {}, ("set", D1, "steps", "1e999")),
    ("NaN", {}, ("set", D1, "steps", "nan")),
    ("unknown metric", {}, ("set", D1, "api_key", "5")),
    ("future date", {}, ("set", str(today + timedelta(days=30)), "steps", "5")),
    ("garbage date", {}, ("set", "../../etc/passwd", "steps", "5")),
    ("ancient date", {}, ("set", "1999-01-01", "steps", "5")),
    ("unknown action", {}, ("delete", D1, "steps", "5")),
]
for name, kw, args in cases:
    check(f"rejected: {name}", edit(*args, **kw)[0] != 0)
check("rejected requests changed nothing", (work / "overrides.json").read_text(encoding="utf-8") == before)

(work / "overrides.json").write_text(json.dumps({
    D1: {"steps": {"value": 5}, "sleep_hours": {"value": 99}, "evil": {"value": 1}}, "not-a-date": {"steps": {"value": 3}}}))
d6, s6 = daily()
check("pipeline survives an invalid overrides.json", days(d6)[D1]["steps"] == 5)
check("invalid entries ignored and reported", days(d6)[D1]["sleep_hours"] == 9.0 and len(s6["errors"]) >= 3, s6["errors"])
(work / "overrides.json").write_text("{not json")
check("corrupt overrides.json reported, not fatal", any("not valid JSON" in e for e in daily()[1]["errors"]))

print("5. Hevy: today's workout appears, status exposes what Hevy last delivered, failures are reported and non-fatal")
(work / "overrides.json").write_text("{}", encoding="utf-8")        # clear the deliberately corrupt file from section 4
STUB = """
def fetch_workouts(since):
    return [{"start_time": "__D__T06:00:00+00:00", "end_time": "__D__T07:00:00+00:00", "title": "Test", "exercises": []}]
def per_day(ws):
    return {"__D__": {"workouts": 1, "minutes": 45, "volume_kg": 1000, "titles": ["Test"]}}
def exercise_history(ws):
    return {}
"""
(work / "fetch_hevy.py").write_text(STUB.replace("__D__", D2), encoding="utf-8")
rc, out = run("daily.py", HEVY_API_KEY="x")
d7, s7 = read("data.json"), read("status.json")
check("today's Hevy workout lands in today's row", rc == 0 and days(d7)[D2]["workout_count"] == 1 and days(d7)[D2]["workout_minutes"] == 45, out)
check("status shows Hevy's newest workout time (Riyadh)", s7["hevy"]["latest_workout_start"] == f"{D2}T09:00:00+03:00", s7["hevy"])
check("status shows ok / total / latest day", s7["hevy"]["ok"] is True and s7["hevy"]["total_workouts"] == 1 and s7["hevy"]["latest_workout"] == D2)
(work / "fetch_hevy.py").write_text("def fetch_workouts(since):\n    raise RuntimeError('boom')\n", encoding="utf-8")
rc, out = run("daily.py", HEVY_API_KEY="x")
d8, s8 = read("data.json"), read("status.json")
check("a failing Hevy does not crash the run", rc == 0, out)
check("the failure is reported in status.errors", any("Hevy fetch failed" in e for e in s8["errors"]) and s8["hevy"]["ok"] is False, s8["errors"])
check("history from the earlier good run is kept", days(d8)[D2]["workout_count"] == 1)
gh_out = work / "gh_output.txt"
rc, out = run("check_status.py", GITHUB_OUTPUT=str(gh_out))
check("check_status reports the error count for the workflow", rc == 0 and "errors=1" in gh_out.read_text(encoding="utf-8"), out)

print("6. Hevy client retries transient failures but not client errors")
sys.path.insert(0, str(ROOT))
import fetch_hevy                                    # the real client (not the stub), requests.get faked below
import requests as _rq

class _Resp:
    def __init__(self, code, body=None):
        self.status_code, self._b = code, body or {}
    def raise_for_status(self):
        if self.status_code >= 400:
            raise _rq.HTTPError(f"HTTP {self.status_code}")
    def json(self):
        return self._b

def run_get(script):
    calls = {"n": 0, "sleeps": []}
    fetch_hevy._sleep = lambda t: calls["sleeps"].append(t)
    def fake(url, headers=None, params=None, timeout=None):
        calls["n"] += 1
        item = script[min(calls["n"], len(script)) - 1]
        if isinstance(item, Exception):
            raise item
        return item
    real = _rq.get
    _rq.get = fake
    try:
        try:
            out = fetch_hevy._get("u", {}, {})
        except Exception as e:
            out = e
    finally:
        _rq.get = real
    return out, calls

out, c = run_get([_rq.ConnectionError("dns"), _rq.Timeout("slow"), _Resp(200, {"ok": 1})])
check("network error then timeout then success -> succeeds on attempt 3", getattr(out, "status_code", None) == 200 and c["n"] == 3, (out, c))
check("backs off between attempts (2 s, 4 s)", c["sleeps"] == [2, 4], c)
out, c = run_get([_Resp(503), _Resp(502), _Resp(200)])
check("temporary server errors are retried", getattr(out, "status_code", None) == 200 and c["n"] == 3, (out, c))
out, c = run_get([_rq.ConnectionError("down")] * 4)
check("gives up after 4 attempts and raises", isinstance(out, _rq.ConnectionError) and c["n"] == 4, (out, c))
out, c = run_get([_Resp(401)])
check("a bad key (401) fails immediately, no retry", isinstance(out, _rq.HTTPError) and c["n"] == 1, (out, c))
out, c = run_get([_Resp(429), _Resp(200)])
check("rate limiting (429) is retried", getattr(out, "status_code", None) == 200 and c["n"] == 2, (out, c))

print("7. Weekly stats: completed Sunday-Saturday weeks only, appended when a week ends, frozen to data, quiet when unchanged")
import tempfile as _tf
import weekly
from datetime import date as _date

def _wk(a, b, **kw):
    out = {}
    d = _date.fromisoformat(a)
    while d <= _date.fromisoformat(b):
        out[d.isoformat()] = dict(kw)
        d += timedelta(days=1)
    return out

wdays = {}
wdays["2026-09-22"] = {"steps": 500}                                           # week of Sun 20 Sep (one day of data)
# Sun 27 Sep - Sat 3 Oct: no data at all (a gap week)
wdays["2026-10-05"] = {"steps": 1000}; wdays["2026-10-06"] = {"steps": 3000, "workout_count": 1, "workout_minutes": 40, "workout_volume_kg": 1000}
for i, st in enumerate((1000, 2000, 3000, 4000, 5000, 6000, 7000)):             # Sun 11 - Sat 17 Oct
    wdays[str(_date(2026, 10, 11) + timedelta(days=i))] = {"steps": st}
wdays["2026-10-12"].update(sleep_hours=6.0, workout_count=1, workout_minutes=30, workout_volume_kg=500, weight_kg=65.0)
wdays["2026-10-14"].update(sleep_hours=8.0, workout_count=1, workout_minutes=45, workout_volume_kg=700, weight_kg=64.0)
wdays.update(_wk("2026-10-18", "2026-10-21", steps=99999, sleep_hours=1, calories=9999))   # the current week must stay out

W = weekly.build_weeks(wdays, _date(2026, 10, 22))                              # Thursday
check("only completed weeks, oldest first, gap week skipped", [w["start"] for w in W] == ["2026-09-20", "2026-10-04", "2026-10-11"], [w["start"] for w in W])
w11 = W[-1]
check("steps average over the days with data (1000..7000 -> 4000)", w11["steps"] == 4000 and isinstance(w11["steps"], int), w11)
check("sleep average over the 2 nights with data, 2 decimals", w11["sleep_hours"] == 7.0 and w11["days_with_data"]["sleep_hours"] == 2, w11)
check("weight average; calories null when never recorded", w11["weight_kg"] == 64.5 and w11["calories"] is None, w11)
check("workouts, minutes and volume are weekly totals", (w11["workouts"], w11["workout_minutes"], w11["workout_volume_kg"]) == (2, 75, 1200), w11)
check("a partly empty week averages only what exists", W[1]["steps"] == 2000 and W[1]["workouts"] == 1, W[1])
check("the in-progress week never appears", all(w["end"] < "2026-10-18" for w in W))
check("Saturday: this week is still in progress", "2026-10-18" not in [w["start"] for w in weekly.build_weeks(wdays, _date(2026, 10, 24))])
check("Sunday: the week that just ended is added", weekly.build_weeks(wdays, _date(2026, 10, 25))[-1]["start"] == "2026-10-18")
check("weeks start on Sunday", weekly.week_start(_date(2026, 10, 18)) == _date(2026, 10, 18) and weekly.week_start(_date(2026, 10, 24)) == _date(2026, 10, 18) and weekly.week_start(_date(2026, 10, 19)) == _date(2026, 10, 18))
check("no data at all -> no weeks", weekly.build_weeks({}, _date(2026, 10, 22)) == [])
md = weekly.to_markdown(W)
check("markdown lists newest first", md.index("11 Oct") < md.index("4 Oct") < md.index("20 Sep"), md)
tmp = Path(_tf.mkdtemp(prefix="motus_weekly_"))
first = weekly.write(wdays, tmp, _date(2026, 10, 22))
before = ((tmp / "weeks.json").read_text(encoding="utf-8"), (tmp / "WEEKLY_STATS.md").read_text(encoding="utf-8"))
check("files are written", len(first) == 3 and json.loads(before[0])["weeks"][-1]["start"] == "2026-10-11")
check("rewriting identical content reports no change", weekly._write_if_changed(tmp / "weeks.json", before[0]) is False and weekly._write_if_changed(tmp / "WEEKLY_STATS.md", before[1]) is False)
wdays2 = {**wdays, "2026-10-17": {"steps": 7000, "calories": 1800}}
weekly.write(wdays2, tmp, _date(2026, 10, 22))
check("late data for a finished week flows into that week", json.loads((tmp / "weeks.json").read_text(encoding="utf-8"))["weeks"][-1]["calories"] == 1800)
shutil.rmtree(tmp, ignore_errors=True)

run("daily.py")                                                              # integration: the real script in the sandbox
wk1 = (work / "weeks.json").read_text(encoding="utf-8"); md1 = (work / "WEEKLY_STATS.md").read_text(encoding="utf-8")
wj = json.loads(wk1)["weeks"]
check("daily.py writes weeks.json and WEEKLY_STATS.md", bool(md1) and isinstance(wj, list))
check("every week in the file has ended, in order", all(w["end"] < str(today) for w in wj) and [w["start"] for w in wj] == sorted(w["start"] for w in wj))
run("daily.py")
check("a second run leaves both weekly files byte-identical", (work / "weeks.json").read_text(encoding="utf-8") == wk1 and (work / "WEEKLY_STATS.md").read_text(encoding="utf-8") == md1)

print(f"\n{passes} passed, {len(fails)} failed")
if fails:
    print("FAILED:", fails)
shutil.rmtree(work, ignore_errors=True)
sys.exit(1 if fails else 0)
