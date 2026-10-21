"""Fetch workouts from Hevy (read-only) and summarise them per day (Asia/Riyadh)."""
from collections import defaultdict
from datetime import datetime, timedelta

import requests

from common import TZ, load_env, require

BASE = "https://api.hevyapp.com/v1"


def fetch_workouts(since: datetime) -> list[dict]:
    headers = {"api-key": require("HEVY_API_KEY")}
    out, page = [], 1
    while True:
        r = requests.get(f"{BASE}/workouts", headers=headers,
                         params={"page": page, "pageSize": 10}, timeout=30)
        r.raise_for_status()
        data = r.json()
        for w in data.get("workouts", []):
            if datetime.fromisoformat(w["start_time"]) < since:
                return out  # newest first, so we can stop
            out.append(w)
        if page >= data.get("page_count", 1):
            return out
        page += 1


def per_day(workouts: list[dict]) -> dict[str, dict]:
    days: dict[str, dict] = defaultdict(lambda: {"workouts": 0, "minutes": 0, "volume_kg": 0.0, "titles": []})
    for w in workouts:
        start = datetime.fromisoformat(w["start_time"]).astimezone(TZ)
        end = datetime.fromisoformat(w["end_time"]).astimezone(TZ)
        d = days[start.date().isoformat()]
        d["workouts"] += 1
        d["minutes"] += round((end - start).total_seconds() / 60)
        d["titles"].append(w.get("title", ""))
        for ex in w.get("exercises", []):
            for s in ex.get("sets", []):
                d["volume_kg"] += (s.get("weight_kg") or 0) * (s.get("reps") or 0)
    return {k: {**v, "volume_kg": round(v["volume_kg"])} for k, v in days.items()}


def exercise_history(workouts: list[dict]) -> dict[str, list]:
    """Per exercise, per day: [date, best e1RM (Epley, reps<=12), weight, reps, volume_kg].

    Warm-ups and unweighted sets are ignored. Sorted oldest first.
    """
    out: dict[str, dict[str, list]] = defaultdict(dict)
    for w in workouts:
        date = datetime.fromisoformat(w["start_time"]).astimezone(TZ).date().isoformat()
        for ex in w.get("exercises", []):
            best, volume = None, 0.0
            for s in ex.get("sets", []):
                wt, reps = s.get("weight_kg"), s.get("reps")
                if s.get("type") == "warmup" or not wt or not reps:
                    continue
                volume += wt * reps
                if reps <= 12:
                    e1rm = wt * (1 + reps / 30)
                    if best is None or e1rm > best[0]:
                        best = (e1rm, wt, reps)
            if best is None:
                continue
            prev = out[ex["title"]].get(date)
            if prev:  # same exercise twice in one day: keep best, add volume
                if best[0] <= prev[1]:
                    best = (prev[1], prev[2], prev[3])
                volume += prev[4]
            out[ex["title"]][date] = [date, round(best[0], 1), best[1], best[2], round(volume)]
    return {t: [days[d] for d in sorted(days)] for t, days in out.items()}


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    load_env()
    since = datetime.now(TZ) - timedelta(days=30)
    ws = fetch_workouts(since)
    print(f"{len(ws)} workouts in the last 30 days")
    for day, info in sorted(per_day(ws).items()):
        print(day, info)
