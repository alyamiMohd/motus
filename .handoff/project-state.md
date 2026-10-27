# Project state (as of 2026-10-24, code at commit `19ddd00`)

Full detail lives in `docs/PROJECT_CONTEXT.md`; this is the cold-start summary. When the code and any document disagree, trust the code.

## Stack
Python 3.10+ (stdlib + `requests`; no tzdata dependency: Riyadh is a fixed UTC+3), plain HTML/CSS/JS (no framework, build or CDN), GitHub Actions (Ubuntu, Python 3.12), GitHub Pages (workflow deployment), Node 18 only for `tests/test_week_logic.mjs`. No server, no database.

## Architecture
```
iPhone Shortcut ──PUT (GitHub API)──► inbox/health-YYYY-MM-DD-HHMM.json
Hevy REST API ──GET only──► daily.py
history/*.json (one-off backfills)   overrides.json (manual corrections)
        └──► .github/workflows/daily.yml ──► daily.py ──► data.json, workouts.json, status.json
                                              ├─► weekly.py ──► weeks.json, WEEKLY_STATS.md
                                              └─► GitHub Pages (site/ + data files)
```
Workflow: schedule `17 */3 * * *` (UTC), pushes touching `inbox/ site/ history/ overrides.json *.py`, and `workflow_dispatch` (optionally with correction inputs). Jobs: `build` → `deploy` → `report` (fails the run after deploying if a source errored, so GitHub notifies the owner). Corrections run in their own concurrency group.

## File map
| Path | Purpose |
|---|---|
| `daily.py` | merge all sources; apply overrides; write `data.json`, `workouts.json`, `status.json`; call `weekly.write` |
| `fetch_hevy.py` | read-only Hevy client with retries; per-day summary; per-exercise best estimated 1RM history |
| `weekly.py` | completed Sunday–Saturday weeks → `weeks.json`, `WEEKLY_STATS.md` (derived from `data.json`) |
| `overrides.py`, `edit.py` | validation and the CLI the workflow runs for a correction (owner-only, server-side) |
| `check_status.py` | emits `errors=N` for the workflow |
| `common.py`, `serve.py` | `.env` loader and `TZ`; local preview server on :8099 |
| `site/index.html`, `workouts.html`, `weeks.html`, `goal.html` (+ `goal.json`), `edit.html`, `shared.js`, `style.css` | the UI; `shared.js` holds nav, standards, `weekStart`, `weekAvg`, `loggingStreak`, `dayMonth`, admin token helper |
| `data.json`, `workouts.json`, `weeks.json`, `WEEKLY_STATS.md` | generated and committed (never hand-edit) |
| `overrides.json`, `history/*.json`, `inbox/` | corrections, backfills, raw phone uploads |
| `tests/test_pipeline.py`, `tests/test_week_logic.mjs` | 67 + 64 checks |
| `CLAUDE.md`, `docs/*`, `.handoff/*` | instructions and project memory |

## Commands
```
pip install -r requirements.txt          # requests only
python daily.py                          # rebuild everything locally (needs .env with HEVY_API_KEY)
python serve.py                          # preview at http://localhost:8099 (serves site/ + generated JSON)
python tests/test_pipeline.py            # must print "0 failed"
node tests/test_week_logic.mjs           # must print "0 failed"
gh workflow run daily.yml --repo alyamiMohd/motus                                  # manual run
gh workflow run daily.yml --repo alyamiMohd/motus -f action=set -f date=YYYY-MM-DD -f metric=calories -f value=1250 -f note="why"   # correction (owner only)
gh workflow run daily.yml --repo alyamiMohd/motus -f action=revert -f date=YYYY-MM-DD -f metric=calories
git pull --rebase                         # always first: a bot commits data daily
```
Run correction dispatches **one at a time** (K15: simultaneous ones can race on `overrides.json`).

## Environment and secrets (names only; never write values)
- `HEVY_API_KEY`: GitHub Actions secret + local `.env` (Hevy → Settings → Developer; needs Hevy PRO). `.env` is git-ignored.
- iPhone upload token: a fine-grained GitHub PAT (Contents read/write, this repo only) stored **inside the Shortcut** only. It expires (date unknown); uploads fail silently after expiry (the dashboard banner/footer would reveal it).
- Admin edit token: fine-grained PAT, **Actions read/write only**, pasted into `site/edit.html` (kept in `sessionStorage`, key `motus-admin-token`). **Not created yet.**
- `STRAVA_*` in `.env.example` are unused.

## External services
GitHub (repo, Actions, Pages), Hevy API, Apple Health + MyFitnessPal (via the phone), the third-party iPhone app *Health Exporter & Shortcuts* (action "Export Health Data").

## Data semantics worth knowing
- Zero from Health for steps/sleep/calories/active kcal/weight means "no data". Sleep = minutes asleep (core+deep+rem; unstaged sleep is not counted by the export app), dated by wake-up day. Today's sleep often arrives late in the export.
- Hevy returns only finished and synced workouts; days are grouped by start time in Riyadh time.
- Precedence: Health files (newest wins per date) → Hevy → history gap-fill (calories/weight only where empty) → manual corrections (always win; automatic value kept in `orig`; revert restores the latest automatic value).
- Weekly averages: steps and calories Sunday→yesterday, sleep and weight Sunday→today; on a Sunday steps/calories show "no data". Weeks start Sunday.
- Rating: Epley e1RM; per-workout scale 7 = normal, floor 3, new exercises skipped; overall = 0.7 progress + 0.3 consistency.

## What works now (verified)
Dashboard, Workouts page, Weeks page, footer source times, stale/error banner, Hevy retries, corrections (owner edit → sync → revert, invalid input rejected, unauthenticated calls 401) tested live on 2026-10-22, cron runs firing, daily phone upload at ~06:00, weekly files generated and published (78 weeks).

## Known bugs and limitations (see `docs/KNOWN_ISSUES.md`)
Late/missing sleep in the export (K3); suspected double-counted long sleeps (K4); overall vs per-workout rating scale mismatch (K6); admin edit page never driven by a real token (K8); workout corrections do not change per-exercise ratings (K9); real iPhone Safari unverified (K10); MFP backfill has extreme/incomplete days and weight values estimated from a chart (K11); Standards panel changeable per visitor device (K12); upload token expiry (K13); goal 4 vs 5 planned days (K14); correction race on simultaneous dispatches (K15); no frontend tests (K16); failure-alert path never exercised live (K18); a workout done today appears only after Hevy syncs it (K17).

## Workarounds and why
- Cron is off `:00` because GitHub delays/drops runs on the hour.
- The admin Edit link lives in the Standards panel. The nav has five items (Dashboard, Workouts, Weeks, Goal, Standards); type and spacing tighten at <= 440/380/350 px so they fit down to 320 px.
- `localStorage` keys stay `stotis-*` after the rename so saved settings survive.
- Weekly history is recomputed each run (not sealed) so late Saturday data and corrections reach old weeks.
- Windows/bash: avoid backslash escapes in heredocs (a `\n` was turned into a real newline); use the Write/Edit tools or `chr(92)`; use `encoding="utf-8"` (emoji in workout titles).
