"""Reads status.json (written by daily.py) and reports how many source errors the run hit.

Prints each error as a GitHub annotation and sets the step output `errors=N`, so the
workflow can still deploy the site and then fail the run (which notifies the repo owner).
"""
import json
import os
from pathlib import Path

STATUS = Path(__file__).parent / "status.json"


def main() -> None:
    try:
        errors = json.loads(STATUS.read_text(encoding="utf-8")).get("errors", [])
    except (OSError, json.JSONDecodeError) as e:
        errors = [f"status.json missing or unreadable: {e}"]
    for e in errors:
        print(f"::warning::{e}")
    print(f"{len(errors)} source error(s)")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"errors={len(errors)}\n")


if __name__ == "__main__":
    main()
