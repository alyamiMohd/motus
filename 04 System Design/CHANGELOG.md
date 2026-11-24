# Changelog

Newest first. Dates are 2026. Hashes are short commit IDs on `main` (daily bot commits named "Update data" are omitted).

## 2026-10-28
- **Goal pace = average difference, clearly labelled**: "Your pace" is again this 7-day average minus the previous 7-day average (22-28 Oct 63.74 vs 15-21 Oct 64.63 = -0.89 kg/week), with both averages printed on the row, both weeks named in the header and shaded on the chart, and the ETA derived from it (27 Nov); the fitted-line pace (`weightTrend`, "no clear trend") is removed because it said +0.38 on a flat week; 76 Node checks (this commit).
- **Goal pace honest about noise**: "Your pace" showed +0.38 kg/week from 22-28 Oct although the 7-day average was flat; the fitted line was tilted by an early dip (63.1 on the 24th) and later 64.0 readings, and its own noise (+-0.46) was bigger. The row now shows "no clear trend" (with the explanation) and no ETA whenever |pace| < its standard error; clear trends show the number with its +-. `weightTrend` returns `se`; 4 new tests (79 Node checks) (this commit).

## 2026-10-27
- **Goal chart tidied**: the gold is now a soft glow close around the target flag only (the full-height block to the right edge is gone); every number sits next to what it labels ("Plan 63.9" and "You 63.8" beside their dots, heavier on top, in the dots' colours; "60 kg goal" under the flag; the stray left "60 kg" is gone) (this commit).
- **Goal page: the end of the graph is golden**, to make reaching it motivating: gold glow toward the target date, gold target line, flag and "Goal" label, a gold key entry; your dot and the headline turn gold ("Goal reached") once the 7-day average is at or below the target (this commit).
- **Goal page: "Your pace" is one window, no comparison**: the trend (kg/week) of the weigh-ins inside the 7-day window ending today (21-27 Oct), labelled "how fast your weight moved across 21-27 Oct (7 weigh-ins)"; the previous-week window, its chart band and the "vs" text are gone; `weightTrend` in `site/shared.js`; tests updated (75 Node checks) (this commit).
- **Goal page shows its data window**: "Based on the last 7 days: 21-27 Oct (compared with 14-20 Oct)", both windows shaded on the chart, dates on every row, rolling one day forward at both ends every day; `dayRange` and window fields in `goalStatus`; 9 new tests (73 total) (this commit).
- **MyFitnessPal streak baseline**: the streak tile shows the owner's 568 days (through 26 Oct) plus one per further logged day, "since 7 Apr 2025 · MyFitnessPal"; `site/streaks.json`, `loggingStreak(days, today, baseline)`, 11 new tests (64 total) (this commit).

## 2026-10-26
- **Goal in the top nav** (five items), panel link removed; responsive nav type and spacing for 320-440 px; the goal stats values no longer wrap (this commit).
- **Goal Visualized (demo)**: new `site/goal.html` + `site/goal.json` (60 kg by 15 Dec 2026): plan line, dot 1 (plan today), dot 2 (7-day average), gap, pace and projected date; `goalPlan`/`goalStatus`/`daysBetween`/`avgOver` in `site/shared.js`; 18 new tests (53 total); linked from the Standards panel (this commit).
- **Deploy cache fix**: pages now load `shared.js?v=<commit>` / `style.css?v=<commit>` (stamped by the workflow), and the streak section is isolated with try/catch, after the new page met a cached older `shared.js` and the charts failed (KNOWN_ISSUES C11) (this commit).
- Streaks moved to a tile section at the very end of the dashboard (flame + 4-week calendar, dumbbell + 12-week chart); the average weight was removed from the weight card again at the owner's request; `streakGrid` and `weeklyWorkouts` added with 8 more tests (35 total) (this commit).
- **Streaks and weight average** (first version, superseded above): the weight card now shows the week's average weight under the change; a streaks line under "Last Week" shows Hevy's total workouts and a calorie-logging streak (`loggingStreak` in `site/shared.js`, 11 new tests, 27 total in `tests/test_week_logic.mjs`) (this commit).

## 2026-10-24
- Resumed on a new session. Verified and closed K1 (scheduled runs fire) and K2 (the phone uploads at 06:00 on its own); closed K17 (the owner had confirmed there was no workout on 22 Oct); docs only.

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
