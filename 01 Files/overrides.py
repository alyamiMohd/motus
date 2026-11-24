"""Manual corrections (overrides.json): one validator shared by edit.py and daily.py.

overrides.json: {"YYYY-MM-DD": {"metric": {"value": number|null, "note": str, "at": ISO time}}}
A null value means "no data" (use it to clear a false positive).
"""
import json
import math
from datetime import date, datetime, timedelta
from pathlib import Path

from common import TZ

# metric -> (min, max, kind, decimals)
EDITABLE = {
    "steps": (0, 100_000, int, 0),
    "sleep_hours": (0, 24, float, 2),
    "calories": (0, 20_000, int, 0),
    "weight_kg": (20, 400, float, 1),
    "active_kcal": (0, 20_000, int, 0),
    "workout_count": (0, 10, int, 0),
    "workout_minutes": (0, 1_440, int, 0),
    "workout_volume_kg": (0, 500_000, int, 0),
}
MAX_ENTRIES = 500
MAX_NOTE = 200
MAX_AGE_DAYS = 800


def today_riyadh() -> date:
    return datetime.now(TZ).date()


def parse_value(metric: str, raw):
    """Normalise a submitted value; '' / 'null' mean 'no data'. Raises ValueError if invalid."""
    if metric not in EDITABLE:
        raise ValueError(f"metric '{metric}' cannot be edited")
    lo, hi, kind, dec = EDITABLE[metric]
    if raw is None or (isinstance(raw, str) and raw.strip().lower() in ("", "null", "none")):
        return None
    if isinstance(raw, bool):
        raise ValueError("value must be a number")
    try:
        value = float(raw)
    except (TypeError, ValueError):
        raise ValueError(f"'{raw}' is not a number") from None
    if not math.isfinite(value):
        raise ValueError("value must be finite")
    if not lo <= value <= hi:
        raise ValueError(f"{metric} must be between {lo} and {hi}")
    if kind is int:
        if value != int(value):
            raise ValueError(f"{metric} must be a whole number")
        return int(value)
    return round(value, dec)


def parse_date(raw: str, today: date | None = None) -> str:
    today = today or today_riyadh()
    try:
        d = date.fromisoformat(str(raw))
    except ValueError:
        raise ValueError(f"'{raw}' is not a valid date (YYYY-MM-DD)") from None
    if d > today:
        raise ValueError("date is in the future")
    if d < today - timedelta(days=MAX_AGE_DAYS):
        raise ValueError("date is too far in the past")
    return d.isoformat()


def clean_note(raw) -> str:
    text = "".join(ch for ch in str(raw or "") if ch.isprintable())
    return text.strip()[:MAX_NOTE]


def load(path: Path, today: date | None = None) -> tuple[dict, list[str]]:
    """Read overrides.json, keeping only valid entries. Returns (clean, error messages)."""
    errors: list[str] = []
    if not path.exists():
        return {}, errors
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {}, [f"overrides.json is not valid JSON: {e}"]
    if not isinstance(raw, dict):
        return {}, ["overrides.json must be an object"]
    clean: dict = {}
    count = 0
    for d, metrics in raw.items():
        if not isinstance(metrics, dict):
            errors.append(f"overrides.json {d}: expected an object")
            continue
        for metric, entry in metrics.items():
            try:
                day = parse_date(d, today)
                if not isinstance(entry, dict) or "value" not in entry:
                    raise ValueError("entry needs a 'value'")
                value = parse_value(metric, entry["value"])
                count += 1
                if count > MAX_ENTRIES:
                    raise ValueError("too many corrections")
            except ValueError as e:
                errors.append(f"overrides.json {d}/{metric}: {e}")
                continue
            clean.setdefault(day, {})[metric] = {
                "value": value,
                "note": clean_note(entry.get("note")),
                "at": str(entry.get("at", ""))[:40],
            }
    return clean, errors


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(dict(sorted(data.items())), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
