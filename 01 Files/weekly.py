"""Weekly stats: one row per *completed* week (Sunday to Saturday, Riyadh time), derived from data.json.

A week is added automatically once it has finished (the first run after Saturday). The history is recomputed
from data.json on every run, so it can never drift, late data or corrections flow into old weeks, and nothing is
lost. Written to weeks.json (the site reads it) and WEEKLY_STATS.md (a table to read on GitHub). Files are only
rewritten when their content changes, so quiet runs commit nothing.
"""
import json
from datetime import date, timedelta
from pathlib import Path

AVG = ("sleep_hours", "steps", "calories", "weight_kg")     # averaged over the days that have data
DECIMALS = {"sleep_hours": 2, "steps": 0, "calories": 0, "weight_kg": 2}


def week_start(d: date) -> date:
    """The Sunday on or before d (Python: Monday=0 ... Sunday=6)."""
    return d - timedelta(days=(d.weekday() + 1) % 7)


def _mean(values: list[float], decimals: int):
    if not values:
        return None
    m = sum(values) / len(values)
    return int(round(m)) if decimals == 0 else round(m, decimals)


def build_weeks(days: dict, today: date) -> list[dict]:
    """Completed weeks, oldest first. Weeks with no data at all are skipped."""
    dates = sorted(date.fromisoformat(k) for k in days)
    if not dates:
        return []
    out = []
    start = week_start(dates[0])
    this_week = week_start(today)
    while start < this_week:                                  # only weeks that have fully ended
        end = start + timedelta(days=6)
        recs = [days.get((start + timedelta(days=i)).isoformat()) or {} for i in range(7)]
        row = {"start": start.isoformat(), "end": end.isoformat()}
        counts = {}
        for k in AVG:
            vals = [r[k] for r in recs if r.get(k) is not None]
            row[k] = _mean(vals, DECIMALS[k])
            counts[k] = len(vals)
        row["workouts"] = sum(r.get("workout_count") or 0 for r in recs)
        row["workout_minutes"] = sum(r.get("workout_minutes") or 0 for r in recs)
        row["workout_volume_kg"] = sum(r.get("workout_volume_kg") or 0 for r in recs)
        row["days_with_data"] = counts
        if any(row[k] is not None for k in AVG) or row["workouts"]:
            out.append(row)
        start += timedelta(days=7)
    return out


def to_markdown(weeks: list[dict]) -> str:
    f = lambda v, fmt: "–" if v is None else format(v, fmt)
    lines = [
        "# Weekly stats",
        "",
        "Generated automatically by `daily.py` (see `weekly.py`); do not edit by hand. One row per completed week,",
        "Sunday to Saturday (Riyadh time), newest first. Averages use the days that have data (the counts are in `weeks.json`).",
        "A week appears here the first time the job runs after it ends.",
        "",
        "| Week | Sleep (h) | Steps | Calories | Weight (kg) | Workouts | Lift (min) | Volume (kg) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for w in reversed(weeks):
        a, b = date.fromisoformat(w["start"]), date.fromisoformat(w["end"])
        label = f"{a.day} {a:%b} – {b.day} {b:%b} {b.year}"
        lines.append(f"| {label} | {f(w['sleep_hours'], '.1f')} | {f(w['steps'], ',')} | {f(w['calories'], ',')} | "
                     f"{f(w['weight_kg'], '.1f')} | {w['workouts']} | {w['workout_minutes'] or '–'} | "
                     f"{f(w['workout_volume_kg'] or None, ',')} |")
    return "\n".join(lines) + "\n"


def _write_if_changed(path: Path, text: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def write(days: dict, root: Path, today: date) -> list[dict]:
    weeks = build_weeks(days, today)
    _write_if_changed(root / "weeks.json", json.dumps({"weeks": weeks}, indent=1, ensure_ascii=False) + "\n")
    _write_if_changed(root / "WEEKLY_STATS.md", to_markdown(weeks))
    return weeks
