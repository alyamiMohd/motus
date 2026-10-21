"""Merge Apple Health exports (inbox/*.json) and Hevy workouts into data.json.

data.json keeps full history: {"updated": ISO time, "days": {"YYYY-MM-DD": {...}}}.
Missing values are null. Zero for steps/sleep/calories is treated as "no data".
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from common import TZ, load_env

ROOT = Path(__file__).parent
INBOX = ROOT / "inbox"
DATA = ROOT / "data.json"
WORKOUTS = ROOT / "workouts.json"

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


def load_health() -> dict[str, dict]:
    merged: dict[str, dict] = {}
    for f in sorted(INBOX.glob("health-*.json")):  # oldest first, newer overrides
        try:
            for date, vals in parse_health(f).items():
                merged.setdefault(date, {}).update(vals)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"WARN: skipping {f.name}: {e}", file=sys.stderr)
    return merged


def load_hevy() -> tuple[dict[str, dict], dict | None]:
    """Returns (per-day workout summary, per-exercise history). Full history every run."""
    import os
    if not os.environ.get("HEVY_API_KEY"):
        print("WARN: HEVY_API_KEY not set, skipping Hevy", file=sys.stderr)
        return {}, None
    try:
        from fetch_hevy import exercise_history, fetch_workouts, per_day
        ws = fetch_workouts(datetime(2000, 1, 1, tzinfo=TZ))
        days = {d: {"workout_count": i["workouts"], "workout_minutes": i["minutes"],
                    "workout_volume_kg": i["volume_kg"], "workout_titles": i["titles"]}
                for d, i in per_day(ws).items()}
        return days, exercise_history(ws)
    except Exception as e:  # a source failing must never break the daily run
        print(f"WARN: Hevy fetch failed: {e}", file=sys.stderr)
        return {}, None


def main() -> None:
    load_env()
    existing = json.loads(DATA.read_text(encoding="utf-8")) if DATA.exists() else {"days": {}}
    days = existing["days"]

    hevy_days, exercises = load_hevy()
    for source in (load_health(), hevy_days):
        for date, vals in source.items():
            days.setdefault(date, {}).update(vals)  # only non-null values reach here
    if exercises is not None:  # keep the previous file if Hevy failed
        stamp = datetime.now(TZ).isoformat(timespec="seconds")
        WORKOUTS.write_text(json.dumps({"updated": stamp, "exercises": exercises},
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

    # make every record have every field, null when missing
    for date, rec in days.items():
        for f in FIELDS:
            rec.setdefault(f, None)

    out = {"updated": datetime.now(TZ).isoformat(timespec="seconds"),
           "days": dict(sorted(days.items()))}
    DATA.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"data.json: {len(days)} days, latest {max(days) if days else 'none'}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
