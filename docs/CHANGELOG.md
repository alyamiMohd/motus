# Changelog

Newest first. Dates are 2026. Hashes are short commit IDs on `main` (daily bot commits named "Update data" are omitted).

## 2026-10-22
- **Weekly stats**: `weekly.py` builds `weeks.json` and `WEEKLY_STATS.md` (one row per completed Sunday-Saturday week, 78 weeks backfilled from `data.json`), committed by the workflow; new `site/weeks.html` page and "Weeks" nav link; Edit link moved into the Standards panel and nav tightened for 320 px; month names always three letters ("Sep"); 18 new tests (67 total) (this commit).
- Heading now reads "Weekly avg (Since Sun, 18 Oct)" (Sunday's date, updates every week) (this commit).
- **Data correction (owner request)**: calories for 2026-10-20 and 2026-10-21 set to 1250 through the correction workflow (`overrides.json`; originals 500 and 629 kept and revertable). Applied by two sequential `workflow_dispatch` runs (bot commits on `main`).
- **Averages rule**: steps and calories now average Sunday → yesterday (today is partial), sleep and weight Sunday → today; weight card is this week's average minus last week's; heading says "steps and calories to yesterday"; one tested function `weekAvg` (`site/shared.js`), 16 new tests (this commit).
- Hevy client now retries transient failures (network errors, timeouts, 429, 5xx; 4 attempts, backoff) after a DNS failure made a whole sync fail; tests extended to 49.
- Audit pass: footer no longer says "no workouts" when the Hevy check failed (shows last known workout + "check failed"); test counts corrected in docs; K18 added.
- Hevy visibility and refresh rate (this commit): schedule is now every 3 hours; `status.json` records Hevy's newest workout time and total; the dashboard footer shows last Hevy workout / last Health upload / last check; tests extended to 43 (Hevy stub, failure path, `check_status` output).
- Investigated "nothing in Lift on Thu 22": Hevy's API had no workout for today (KNOWN_ISSUES K17).
- **Docs/memory system**: `CLAUDE.md`, `docs/*`, `tests/test_pipeline.py` in the repo; README corrected; `.claude/launch.json` now runs `serve.py` (this commit; see `git log`).
- Per-workout rating scale made gentler: 7 = normal session, floor 3 (`64b30b4`).
- Workouts page: exercises sorted by most recently trained; rating baselines limited to 90 days; unrated exercises shown (`8838907`).
- **Reliability + admin corrections** (`ca23ea5`): schedule moved to 06:17/09:17/12:17 Riyadh; `status.json`; run fails on source errors (after deploying); dashboard staleness banner; `data.json` only changes when data changes;
  manual corrections via validated `workflow_dispatch` (`overrides.json`, `overrides.py`, `edit.py`, `site/edit.html`) with originals preserved and revert; security tests run live.
- Investigated the missing morning update: no cron run had ever fired; no phone upload that morning (see KNOWN_ISSUES K1/K2).

## 2026-10-21
- Project renamed Stotis → **Motus** (repo `alyamiMohd/motus`, folder, titles) (`0554b05`; earlier name step `d028778`).
- Calories standard 1500; weekly workout chart green at goal else white; Progress/Consistency lines removed from the Workouts page (`f88ff52`).
- Last Week line: pipes, simpler header, comparison only for steps and weight (`c4ffef7`, `569fc3b`, `78ef983`, `f121e1e`); calories "less than" standard (`4101bc9`).
- Backfills: weight Sep 22–Oct 21 from a chart (`cf63b48`); calories Sep 1–Oct 21 from the MyFitnessPal diary (`188cf0e`); workflow also reacts to `history/` and `*.py` changes (`fddb540`).
- Dashboard weekly logic: averages Sunday→today, one-line last-week summary, Sunday date in the heading (`2cb99f4`, `4c42118`, `5125629`).
- Week strip with green workout days, 7-column phone-safe grid, gray planned days, editable training days (`23928c4`, `70f7052`, `e54168f`); 12-week workouts chart colored by count (`d248acf`).
- Workouts page with ratings (`316bcbb`), per-workout and last-workout ratings with this/last-week toggle (`82f8c72`).
- Standards navbar (`082b6c7`) with shared nav/styles; workflow redeploys on site changes.
- Stage 3+4: `daily.py` merge into `data.json`, minimal static site (`ab241e6`); daily workflow, local server, load-error message (`9a9dca0`).
- Stage 1: Hevy fetcher with per-day summary (`5b892c1`).
- Repository created (private), later made **public** with GitHub Pages enabled (`1fc1065`); secret audit of history found nothing; `HEVY_API_KEY` stored as an Actions secret.
- iPhone Shortcut set up by the user to upload exports to `inbox/` through the GitHub API.
