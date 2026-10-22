# Session handoff

Last updated: **2026-10-22**. Read `CLAUDE.md` first. Update this file at the end of every meaningful session.

## Current state
- The dashboard, Workouts page and admin Edit page are **live** at https://alyamimohd.github.io/motus/ (repo `alyamiMohd/motus`, branch `main`, public). The last deploy succeeded.
- Data flows: phone Shortcut → `inbox/` → Actions → `data.json` → Pages; Hevy is fetched every run (read-only). One-off MyFitnessPal backfills fill old calories/weight gaps.
- Today (2026-10-22) after the 10:20 manual upload: steps 391, weight 63.9; **sleep and calories for today not yet in the export; no Hevy workout for today yet** (Hevy's API newest = Wed 21 19:04, 331 total; see K17).

## Most recent completed work (2026-10-22)
1. Diagnosed the missing morning update: no scheduled run ever fired; no phone upload. Reworked scheduling/alerting (3 off-peak crons, `status.json`, failing run on source errors, staleness banner).
2. Added admin corrections (workflow-based, validated, revertable) and tested them live; wrote `tests/test_pipeline.py`.
3. Workouts page: exercises sorted by recency; per-workout rating rescaled (7 = normal, floor 3) after the user objected to a 0.0 score.
3b. Investigated "no Lift on Thu 22": Hevy has no workout for today. Added every-3-hours schedule, Hevy fields in `status.json`, and a footer showing last Hevy workout / Health upload / check time; tests now 43.
4. Created this memory system (`CLAUDE.md`, `docs/`).

## Next priority
1. **Confirm a scheduled run fires**: `gh run list --repo alyamiMohd/motus --event schedule` (now every 3 hours at :17 UTC). If none appears over a day, investigate Actions settings / consider a different trigger.
   Also ask the user whether today's workout is finished and synced in the Hevy app (K17); the footer's "Hevy: last workout" shows what the site has.
2. **Confirm the phone side**: does the Wake Up automation exist and upload? Does today's sleep show up after an afternoon export? (K2, K3).
3. Open user decisions (ask, don't assume): lock or leave the Standards panel (K12); include today in the steps average (K7); base the weight card on averages (K5); align the overall rating scale with the per-workout scale (K6); weekly goal 4 vs 5 planned days (K14); whether to add other Health metrics (see FEATURES "ideas").
4. The user needs to create the **admin token** (fine-grained, Actions: read/write, repo `motus` only) and try `site/edit.html` once (K8). Also check the 12–13 h sleep nights (K4).

## Files to inspect first
`CLAUDE.md`, this file, `daily.py`, `.github/workflows/daily.yml`, `site/index.html`, `site/workouts.html`, `site/shared.js`, `overrides.py`, `docs/KNOWN_ISSUES.md`.

## Tests run / not run
- Run and passing (2026-10-22): `python tests/test_pipeline.py` → 43 passed. Live checks: owner edit → sync → revert; invalid input rejected by the workflow; unauthenticated/fake-token API calls → 401; dashboard averages match an independent calculation.
- Not run / unverified: a real cron-triggered run; the phone's automation; the edit page with a real token; real iPhone Safari rendering; any frontend automated tests (none exist).

## Warnings
- The repo and site are public; never commit `.env`, tokens or API keys. Do not paste secrets into docs.
- The bot commits `data.json`/`workouts.json` daily: always `git pull --rebase` before committing; on conflicts in generated files re-run `python daily.py`.
- Do not reverse recorded decisions silently; add a new row to `docs/DECISIONS.md`.
- The `edit.html` page calls GitHub with the admin's token; no secret may ever be embedded in `site/`.
- Windows/bash escaping and encoding pitfalls are listed in `CLAUDE.md` ("Tooling gotchas").
