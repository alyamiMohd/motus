# Motus

Personal fitness dashboard (live: https://alyamimohd.github.io/motus/). A GitHub Actions job merges Apple Health
uploads (from an iPhone Shortcut) and Hevy workouts into `data.json`; a static site shows weekly averages, a daily table,
charts and a workout-rating page. The repo and site are **public**; secrets live only in `.env` (local, git-ignored) and GitHub Actions Secrets.

**Start here:** [`CLAUDE.md`](CLAUDE.md) (instructions, setup, workflow) and [`docs/SESSION_HANDOFF.md`](docs/SESSION_HANDOFF.md) (current state).
More: [`docs/PROJECT_CONTEXT.md`](docs/PROJECT_CONTEXT.md), [`docs/FEATURES_AND_REQUIREMENTS.md`](docs/FEATURES_AND_REQUIREMENTS.md),
[`docs/DECISIONS.md`](docs/DECISIONS.md), [`docs/KNOWN_ISSUES.md`](docs/KNOWN_ISSUES.md), [`docs/CHANGELOG.md`](docs/CHANGELOG.md).

Quick start: `pip install -r requirements.txt`, copy `.env.example` to `.env` (set `HEVY_API_KEY`), `python daily.py`, `python serve.py`, `python tests/test_pipeline.py`.
