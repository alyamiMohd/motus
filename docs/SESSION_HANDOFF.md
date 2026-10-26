# Session handoff

Last updated: **2026-10-24**. Read `CLAUDE.md` first. Update this file at the end of every meaningful session.

## Current state
- The dashboard, Workouts page and admin Edit page are **live** at https://alyamimohd.github.io/motus/ (repo `alyamiMohd/motus`, branch `main`, public). The last deploy succeeded.
- Data flows: phone Shortcut → `inbox/` → Actions → `data.json` → Pages; Hevy is fetched every run (read-only). One-off MyFitnessPal backfills fill old calories/weight gaps.
- Today (2026-10-22) after the 10:20 manual upload: steps 391, weight 63.9; **sleep and calories for today not yet in the export; no Hevy workout for today yet** (Hevy's API newest = Wed 21 19:04, 331 total; see K17).

## Most recent completed work (2026-10-22)
1. Diagnosed the missing morning update: no scheduled run ever fired; no phone upload. Reworked scheduling/alerting (3 off-peak crons, `status.json`, failing run on source errors, staleness banner).
2. Added admin corrections (workflow-based, validated, revertable) and tested them live; wrote `tests/test_pipeline.py`.
3. Workouts page: exercises sorted by recency; per-workout rating rescaled (7 = normal, floor 3) after the user objected to a 0.0 score.
3b. Investigated "no Lift on Thu 22": Hevy has no workout for today. Added every-3-hours schedule, Hevy fields in `status.json`, and a footer showing last Hevy workout / Health upload / check time; tests now 49 (incl. Hevy retry logic).
4. Created this memory system (`CLAUDE.md`, `docs/`).
5b. Weekly history: `weekly.py` → `weeks.json` + `WEEKLY_STATS.md` (committed each run when changed), `site/weeks.html`, "Weeks" in the nav; 78 weeks backfilled. Watch for the first live Sunday append on 2026-10-25.
5. Averages rule changed at the user's request: steps/calories Sunday → yesterday, sleep/weight Sunday → today; weight card now average-based (K5, K7 closed). Rule is `weekAvg` in `site/shared.js` with `tests/test_week_logic.mjs`.

## Added 2026-10-26
Streaks section at the very end of the dashboard (flame tile: calorie-logging streak + 4-week calendar; dumbbell tile: Hevy lifetime workouts + 12-week chart). The weight card is back to showing only how much was lost (the average weight was added then removed at the owner's request). MyFitnessPal's own streak cannot be imported (K19): ask the owner to read it in the app if they want the real number as a baseline. `node tests/test_week_logic.mjs` -> 35 passed.

## Audit (2026-10-22, end of day)
Re-checked every issue from today against code, tests and live state; see KNOWN_ISSUES for what can still recur (K1 cron unverified, K2/K3 phone upload and late sleep, K13 token expiry, K18 alert path unverified). A transient DNS failure on the dev laptop mid-Hevy-fetch was handled correctly (1 error reported, no data lost).

## Next priority
1. ~~**Sunday 2026-10-25**: confirm the first live weekly append~~ Verified 2026-10-26: the row for 18–24 Oct is in `weeks.json` / `WEEKLY_STATS.md`. (A public version of Motus now lives in `alyamiMohd/motusapp`.)
2. **Late sleep (K3)**: does today's sleep show up in the afternoon exports? Scheduled runs (K1) and the 06:00 phone upload (K2) were verified on 2026-10-24.
3. Open user decisions (ask, don't assume): lock or leave the Standards panel (K12); align the overall rating scale with the per-workout scale (K6); weekly goal 4 vs 5 planned days (K14); whether to add other Health metrics (see FEATURES "ideas").
4. The user needs to create the **admin token** (fine-grained, Actions: read/write, repo `motus` only) and try `site/edit.html` once (K8). Also check the 12–13 h sleep nights (K4).

## Files to inspect first
`CLAUDE.md`, this file, `daily.py`, `.github/workflows/daily.yml`, `site/index.html`, `site/workouts.html`, `site/shared.js`, `overrides.py`, `docs/KNOWN_ISSUES.md`.

## Tests run / not run
- Run and passing (2026-10-22): `python tests/test_pipeline.py` → 67 passed; `node tests/test_week_logic.mjs` → 16 passed. Live checks: owner edit → sync → revert; invalid input rejected by the workflow; unauthenticated/fake-token API calls → 401; dashboard averages match an independent calculation.
- Not run / unverified: a real cron-triggered run; the phone's automation; the edit page with a real token; real iPhone Safari rendering; any frontend automated tests (none exist).

## Warnings
- The Goal page is a demo with a fixed goal (`site/goal.json`: 60 kg by 15 Dec 2026, start 64.0 kg on 26 Oct). It is in the top nav as "Goal". Ask before changing the goal or removing it.
- If you add something to `site/shared.js` that a page uses, it is safe to ship together: the deploy stamps `?v=<commit>` on the asset links (C11). Do not remove or rename existing shared functions casually, an older cached HTML could still call them.
- The repo and site are public; never commit `.env`, tokens or API keys. Do not paste secrets into docs.
- The bot commits `data.json`/`workouts.json` daily: always `git pull --rebase` before committing; on conflicts in generated files re-run `python daily.py`.
- Do not reverse recorded decisions silently; add a new row to `docs/DECISIONS.md`.
- The `edit.html` page calls GitHub with the admin's token; no secret may ever be embedded in `site/`.
- Windows/bash escaping and encoding pitfalls are listed in `CLAUDE.md` ("Tooling gotchas").
