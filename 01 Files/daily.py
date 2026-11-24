"""Merge Apple Health exports (inbox/*.json) and Hevy workouts into data.json.

data.json keeps full history: {"updated": ISO time, "days": {"YYYY-MM-DD": {...}}}.
Missing values are null. Zero for steps/sleep/calories is treated as "no data".

Manual corrections (overrides.json) always win over automatic values. The automatic
value is kept in the day's "orig" map and keeps refreshing underneath, so reverting a
correction restores the latest automatic value. Every run also writes status.json
(last run, last phone upload, source errors) for the dashboard and for failure alerts.
"""
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import overrides
import weekly
from common import TZ, load_env

ROOT = Path(__file__).parent
INBOX = ROOT / "inbox"
DATA = ROOT / "data.json"
WORKOUTS = ROOT / "workouts.json"
STATUS = ROOT / "status.json"

FIELDS = ("steps", "sleep_hours", "calories", "weight_kg", "active_kcal",
          "workout_count", "workout_minutes", "workout_volume_kg", "workout_titles")


def num(v, ndigits=None):
    """Return a positive number or None (zero / missing means no data)."""
    if v is None or v <= 0:
        return None
    return round(v, ndigits) if ndigits is not None else round(v)


def parse_health(path: Path) -> dict[str, dict]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    days: dict[str, dict] = {}

    def put(metric, key, fn):
        for item in raw.get(metric, []):
            val = fn(item)
            if val is not None:
                days.setdefault(item["date"], {})[key] = val

    put("stepCount", "steps", lambda i: num(i["value"]))
    put("sleepTime", "sleep_hours", lambda i: num(i["value"] / 60, 2))  # minutes asleep
    put("dietaryEnergy", "calories", lambda i: num(i["value"]))
    put("weight", "weight_kg", lambda i: num(i["value"], 1))
    put("activeCalories", "active_kcal", lambda i: num(i["value"]))
    return days


def load_health(errors: list[str]) -> dict[str, dict]:
    merged: dict[str, dict] = {}
    for f in sorted(INBOX.glob("health-*.json")):  # oldest first, newer overrides
        try:
            for date, vals in parse_health(f).items():
                merged.setdefault(date, {}).update(vals)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"WARN: skipping {f.name}: {e}", file=sys.stderr)
            errors.append(f"could not read {f.name}: {e}")
    return merged


def latest_upload() -> str | None:
    """Time of the newest phone upload, from its file name health-YYYY-MM-DD-HHMM.json (Riyadh time)."""
    stamps = []
    for f in INBOX.glob("health-*.json"):
        m = re.match(r"health-(\d{4}-\d{2}-\d{2})-(\d{2})(\d{2})", f.name)
        if m:
            stamps.append(f"{m.group(1)}T{m.group(2)}:{m.group(3)}:00+03:00")
    return max(stamps) if stamps else None


def load_hevy() -> tuple[dict[str, dict], dict | None, str | None, dict]:
    """Returns (per-day workout summary, per-exercise history, error, meta). Full history every run.

    meta = {"latest_start": ISO time of Hevy's newest workout, "total": number of workouts} (empty on failure).
    Hevy only returns *finished and synced* workouts, so a workout missing here is missing in Hevy's cloud.
    """
    import os
    if not os.environ.get("HEVY_API_KEY"):
        print("WARN: HEVY_API_KEY not set, skipping Hevy", file=sys.stderr)
        return {}, None, "HEVY_API_KEY is not set", {}
    try:
        from fetch_hevy import exercise_history, fetch_workouts, per_day
        ws = fetch_workouts(datetime(2000, 1, 1, tzinfo=TZ))
        days = {d: {"workout_count": i["workouts"], "workout_minutes": i["minutes"],
                    "workout_volume_kg": i["volume_kg"], "workout_titles": i["titles"]}
                for d, i in per_day(ws).items()}
        newest = max(ws, key=lambda w: w["start_time"]) if ws else None
        meta = {"latest_start": datetime.fromisoformat(newest["start_time"]).astimezone(TZ).isoformat(timespec="seconds") if newest else None,
                "total": len(ws)}
        return days, exercise_history(ws), None, meta
    except Exception as e:  # a source failing must never break the daily run
        print(f"WARN: Hevy fetch failed: {e}", file=sys.stderr)
        return {}, None, f"Hevy fetch failed: {e}", {}


def main() -> None:
    load_env()
    now = datetime.now(TZ).isoformat(timespec="seconds")
    errors: list[str] = []
    existing = json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else {"days": {}}
    days = existing["days"]
    before = json.dumps(days, sort_keys=True)

    # undo last run's manual corrections so the automatic values can refresh underneath them
    for rec in days.values():
        for metric, auto in (rec.pop("orig", None) or {}).items():
            rec[metric] = auto

    hevy_days, exercises, hevy_error, hevy_meta = load_hevy()
    if hevy_error:
        errors.append(hevy_error)
    for source in (load_health(errors), hevy_days):
        for date, vals in source.items():
            days.setdefault(date, {}).update(vals)  # only non-null values reach here
    if exercises is not None:  # keep the previous file if Hevy failed; only rewrite when it changed
        old = json.loads(WORKOUTS.read_text(encoding="utf-8")).get("exercises") if WORKOUTS.exists() else None
        if old != exercises:
            WORKOUTS.write_text(json.dumps({"updated": now, "exercises": exercises},
                                           separators=(",", ":"), ensure_ascii=False) + "\n", encoding="utf-8")

    # one-off MyFitnessPal history: only fills days Apple Health has no calories for
    hist = ROOT / "history" / "mfp-calories.json"
    if hist.exists():
        for date, kcal in json.loads(hist.read_text(encoding="utf-8")).get("calories", {}).items():
            rec = days.setdefault(date, {})
            if rec.get("calories") is None:
                rec["calories"] = kcal

    wh = ROOT / "history" / "mfp-weight.json"
    if wh.exists():
        for date, kg in json.loads(wh.read_text(encoding="utf-8")).get("weight_kg", {}).items():
            rec = days.setdefault(date, {})
            if rec.get("weight_kg") is None:
                rec["weight_kg"] = kg

    # manual corrections win; remember the automatic value so it can be shown and restored
    fixes, override_errors = overrides.load(ROOT / "overrides.json")
    errors += override_errors
    for date, metrics in fixes.items():
        rec = days.setdefault(date, {})
        for metric, entry in metrics.items():
            rec.setdefault("orig", {})[metric] = rec.get(metric)
            rec[metric] = entry["value"]

    # make every record have every field, null when missing
    for date, rec in days.items():
        for f in FIELDS:
            rec.setdefault(f, None)

    days = dict(sorted(days.items()))
    changed = json.dumps(days, sort_keys=True) != before
    stamp = now if changed or "updated" not in existing else existing["updated"]
    DATA.write_text(json.dumps({"updated": stamp, "days": days}, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    weekly.write(days, ROOT, datetime.now(TZ).date())     # one row per completed Sunday-Saturday week

    STATUS.write_text(json.dumps({
        "run": now,
        "health": {"latest_upload": latest_upload(),
                   "latest_day": max((d for d, r in days.items() if r.get("steps")), default=None)},
        "hevy": {"ok": hevy_error is None,
                 "latest_workout": max((d for d, r in days.items() if r.get("workout_count")), default=None),
                 "latest_workout_start": hevy_meta.get("latest_start"),
                 "total_workouts": hevy_meta.get("total")},
        "corrections": sum(len(m) for m in fixes.values()),
        "errors": errors,
    }, indent=1) + "\n", encoding="utf-8")
    print(f"data.json: {len(days)} days, latest {max(days) if days else 'none'}"
          f"{' (unchanged)' if not changed else ''}; {len(errors)} error(s)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
