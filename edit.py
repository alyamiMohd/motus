"""Apply one manual correction (set / revert) to overrides.json. Runs only inside GitHub Actions.

Inputs arrive through environment variables (never interpolated into a shell):
EDIT_ACTION (set|revert), EDIT_DATE, EDIT_METRIC, EDIT_VALUE, EDIT_NOTE,
plus EDIT_ACTOR / REPO_OWNER for the authorization check.
"""
import os
import sys
from datetime import datetime
from pathlib import Path

import overrides
from common import TZ

PATH = Path(__file__).parent / "overrides.json"


def fail(message: str) -> None:
    print(f"::error::{message}")
    sys.exit(1)


def main() -> None:
    env = os.environ.get
    actor, owner = env("EDIT_ACTOR", ""), env("REPO_OWNER", "")
    if not owner or actor != owner:                      # server-side authorization
        fail(f"'{actor}' is not allowed to edit data")

    action = env("EDIT_ACTION", "")
    if action not in ("set", "revert"):
        fail(f"unknown action '{action}'")
    metric = (env("EDIT_METRIC", "") or "").strip()
    try:
        date = overrides.parse_date(env("EDIT_DATE", ""))
        if metric not in overrides.EDITABLE:
            raise ValueError(f"metric '{metric}' cannot be edited")
        value = overrides.parse_value(metric, env("EDIT_VALUE")) if action == "set" else None
    except ValueError as e:
        fail(str(e))

    data, errors = overrides.load(PATH)
    for e in errors:
        print(f"::warning::dropping invalid existing entry: {e}")

    if action == "set":
        if sum(len(m) for m in data.values()) >= overrides.MAX_ENTRIES and metric not in data.get(date, {}):
            fail("too many corrections stored")
        data.setdefault(date, {})[metric] = {
            "value": value,
            "note": overrides.clean_note(env("EDIT_NOTE")),
            "at": datetime.now(TZ).isoformat(timespec="seconds"),
        }
        print(f"set {date} {metric} = {value}")
    else:
        if metric in data.get(date, {}):
            del data[date][metric]
            if not data[date]:
                del data[date]
            print(f"reverted {date} {metric}")
        else:
            print(f"nothing to revert for {date} {metric}")
    overrides.save(PATH, data)


if __name__ == "__main__":
    main()
