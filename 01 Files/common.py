"""Shared helpers: .env loading for local runs (GitHub Actions uses real env vars)."""
import os
from pathlib import Path


def load_env(path: Path = Path(__file__).parent / ".env") -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def require(name: str) -> str:
    value = os.environ.get(name, "")
    if not value:
        raise SystemExit(f"Missing environment variable: {name}")
    return value


from datetime import timedelta, timezone

# Riyadh is a fixed UTC+3 (no DST), so no tzdata dependency is needed.
TZ = timezone(timedelta(hours=3), "Asia/Riyadh")
