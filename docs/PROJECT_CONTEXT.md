# Project context

Status legend used across these docs: **Verified** = tested and observed working; **Implemented** = built, not fully verified;
**Unverified / Unknown** = not confirmed. Last full audit: 2026-10-22. History before this file was written is reconstructed from the
git log and the working session; earlier conversation text is not otherwise available.

## Purpose
A personal fitness dashboard for one user (owner/admin: GitHub `alyamiMohd`). It shows the user's sleep, steps, calories, weight and
workouts, with weekly averages at the top, a 7-day table, 30-day charts, and a separate Workouts page that rates training. It updates itself
every morning without a server. Project name: **Motus** (previously "Stotis"; renamed 2026-10-21; see DECISIONS).

## Architecture (all Verified unless noted)
```
iPhone: Shortcut "Health to Drive" ──PUT (GitHub API)──► repo inbox/health-YYYY-MM-DD-HHMM.json
Hevy REST API ──GET (read-only)──► fetched by daily.py
history/*.json (one-off backfills)        overrides.json (manual corrections)
        └────────────► GitHub Actions: daily.yml ──► daily.py ──► data.json, workouts.json, status.json
                                                    └─► GitHub Pages (site/ + data files)  https://alyamimohd.github.io/motus/
```
- **No server and no database.** State is JSON files in the repo; GitHub Pages serves static files; GitHub Actions is the only compute.
- Languages: Python 3.10+ (stdlib + `requests`), plain HTML/CSS/JS (no framework, no build, no CDN).

### Repository layout
| Path | Role |
|---|---|
| `daily.py` | Merges all sources into `data.json`; applies overrides; writes `status.json` and (if changed) `workouts.json` |
| `fetch_hevy.py` | Read-only Hevy client; per-day workout summary; per-exercise best estimated 1RM history |
| `overrides.py` / `edit.py` | Validation of manual corrections / the CLI the workflow runs to set or revert one |
| `check_status.py` | Reads `status.json`, emits `errors=N` so the workflow can fail loudly after deploying |
| `common.py` | `.env` loader, fixed `TZ` (UTC+3) |
| `serve.py` | Local preview server (port 8099) |
| `site/streaks.json` | The owner's MyFitnessPal streak baseline (days + the day it counts through) |
| `site/goal.html` + `site/goal.json` | Goal Visualized (demo): plan vs actual weight chart; the goal (target, dates, start weight) lives in `goal.json` |
| `site/index.html` | Dashboard · `site/workouts.html` Workouts page · `site/weeks.html` weekly history · `site/edit.html` admin edit page · `site/shared.js` nav, standards, helpers · `site/style.css` |
| `data.json` | Daily records (generated, committed) · `workouts.json` per-exercise history (generated, committed) |
| `overrides.json` | Manual corrections (admin-written via workflow) · `history/*.json` one-off backfills |
| `inbox/` | Raw uploads from the phone (public) |
| `weekly.py` | Builds the weekly history from `data.json`; writes `weeks.json` and `WEEKLY_STATS.md` |
| `weeks.json` / `WEEKLY_STATS.md` | Generated weekly stats: one row per completed Sunday-Saturday week (JSON for the site, a Markdown table to read on GitHub). Never edit by hand |
| `tests/test_week_logic.mjs` | Node tests for the week-to-date averaging rule and the calorie-logging streak (35 checks) |
| `tests/test_pipeline.py` | Synthetic pipeline tests (67 checks; Hevy client stubbed, retry logic with a faked `requests.get`, weekly stats) |
| `.github/workflows/daily.yml` | The only workflow |

## Data sources
1. **Hevy** (workouts). `GET https://api.hevyapp.com/v1/workouts` with header `api-key` (env `HEVY_API_KEY`; requires Hevy PRO). Full history fetched every run
   (331 workouts on 2026-10-22, 10 per page). **Hevy returns only finished and synced workouts**: a workout that was not finished in the app, or has not synced, is absent from the API (and therefore from the site) until it syncs. Days are grouped by workout *start time* in Riyadh time. Read-only: no other HTTP method appears in the code. Requests retry up to 4 times with 2/4/8 s backoff on network errors, timeouts, 429 and 5xx; client errors such as a bad key (401) fail at once.
2. **Apple Health via iPhone Shortcut** (steps, sleep, weight, calories, active calories). A shortcut named `Health to Drive` (legacy name) runs the action
   **Export Health Data** from the third-party app *Health Exporter & Shortcuts* (daily aggregated JSON), Base64-encodes it, and PUTs it to
   `https://api.github.com/repos/alyamiMohd/motus/contents/inbox/health-<yyyy-MM-dd-HHmm>.json` using a fine-grained GitHub token (Contents: read/write on this repo only,
   stored only inside the shortcut). Intended trigger: Shortcuts automation *Sleep → Wake Up → Run Immediately* (**Unverified** that it exists/fires). The phone must be unlocked.
   - Export JSON keys used: `stepCount`, `sleepTime` (minutes asleep = core+deep+rem; `stages`), `dietaryEnergy`, `weight`, `activeCalories`. Other exported keys
     (heart rate, HRV, VO2 max, exercise minutes, flights, distance, etc.) are present but unused (see FEATURES, "ideas").
   - Date semantics (inferred from observed data, not documented by the app): sleep is dated by wake-up date. Today's sleep tends to arrive in the export only later in the day (see KNOWN_ISSUES).
   - Old API address `.../repos/alyamiMohd/stotis/...` answers `307` (method-preserving redirect), so an un-updated shortcut should still work (Verified with a probe; end-to-end on the phone Unverified).
3. **MyFitnessPal → Apple Health** supplies calories into the export (`dietaryEnergy`). MFP only syncs entries logged after connecting (2026-10-21).
4. **One-off backfills** (gap-fill only; Health values always win): `history/mfp-calories.json` (daily totals Sep 1 – Oct 21 2026, copied from the user's pasted MFP printable diary;
   some days look incomplete or extreme) and `history/mfp-weight.json` (Sep 22 – Oct 21 2026, **read from a chart screenshot, accurate to about ±0.1 kg**).
5. **Strava**: dropped (API needs a paid subscription). `STRAVA_*` names remain in `.env.example` but nothing uses them.

## Pipeline (`daily.py`) — merge order and rules
1. Load `data.json`; undo last run's manual corrections (restore each `orig` value) so automatic values can refresh underneath.
2. Merge Health files (`inbox/health-*.json`, oldest first so newer files win per date), then Hevy day summaries. Only non-null values overwrite.
3. Gap-fill calories/weight from `history/`. 4. Apply `overrides.json` (validated; invalid entries ignored and reported). 5. Ensure every record has every field.
6. Write `data.json` (the `updated` stamp only moves when content changed, so no-op runs commit nothing), `workouts.json` (only when changed), `status.json` (always, not committed).
- Zero from Health for steps/sleep/calories/active calories/weight is treated as `null` (no data).

### Data model
`data.json`: `{"updated": ISO, "days": {"YYYY-MM-DD": {steps, sleep_hours, calories, weight_kg, active_kcal, workout_count, workout_minutes, workout_volume_kg, workout_titles, orig?}}}`.
`orig` exists only for corrected metrics and holds the automatic value (`{metric: value|null}`). `active_kcal` is stored but not displayed.
`workouts.json`: `{"updated", "exercises": {title: [[date, best_e1RM, weight_kg, reps, volume_kg], ...]}}` — best set per exercise per day (Epley e1RM, reps ≤ 12, warm-ups and
unweighted sets ignored).
`overrides.json`: `{"date": {"metric": {"value": number|null, "note": str, "at": ISO}}}`; `null` means "no data".
`status.json` (generated each run, uploaded to Pages, not committed): `run`, `health.latest_upload`, `health.latest_day`, `hevy.ok`, `hevy.latest_workout` (date), `hevy.latest_workout_start` (ISO, Riyadh), `hevy.total_workouts`, `corrections`, `errors[]`. The dashboard footer prints "Hevy: last workout …· Health: last upload …· checked …" from it.
Editable metrics and server-side limits (`overrides.py`): steps 0–100000 (int), sleep_hours 0–24, calories 0–20000 (int), weight_kg 20–400, active_kcal 0–20000, workout_count 0–10,
workout_minutes 0–1440, workout_volume_kg 0–500000; dates must be ≤ today (Riyadh) and ≤ 800 days old; ≤ 500 corrections; notes ≤ 200 chars.

## Weekly stats (`weekly.py`)
- One row per **completed** week, **Sunday to Saturday (Riyadh)**. A week is added the first run after it ends (a Sunday run adds the week that just finished); the in-progress week never appears. Weeks with no data at all are skipped.
- Row = `start`, `end`, averages over the days that have data (`sleep_hours`, `steps`, `calories`, `weight_kg`), weekly totals (`workouts`, `workout_minutes`, `workout_volume_kg`) and `days_with_data` counts.
- **Derived, not frozen**: rebuilt from `data.json` (which keeps every day) on each run, so history cannot drift or be lost, and late syncs or manual corrections flow into the affected week. Files are rewritten only when their content changes, so quiet runs commit nothing. Weeks before Sep 2026 mostly have workouts only (Hevy history starts Apr 2025; Health data starts Sep 2026).
- The workflow commits `weeks.json` and `WEEKLY_STATS.md` to `main` and publishes `weeks.json` with the site.

## Workflow `.github/workflows/daily.yml`
- Triggers: `schedule` `17 */3 * * *` (every 3 hours at :17 UTC, i.e. 03:17, 06:17, 09:17 ... Riyadh; off the busy `:00` mark); `push` touching `inbox/**`, `site/**`, `history/**`, `overrides.json`, `*.py`; `workflow_dispatch`
  (optionally with correction inputs: `action` none|set|revert, `date`, `metric`, `value`, `note`).
- Jobs: `build` (checkout, Python 3.12, optional **Apply manual correction** via `edit.py`, `daily.py`, `check_status.py`, commit `data.json workouts.json overrides.json` with retry,
  copy data files into `site/`, **stamp the deploy's commit into each page's `style.css?v=` and `shared.js?v=` links** so a cached older script can never meet a newer page, upload Pages artifact) → `deploy` (Pages) → `report` (fails the run when `status.errors` is non-empty, so GitHub notifies the owner; the site is still deployed).
- Corrections run in their own concurrency group (`edit-<run id>`) so a queued normal run cannot replace them; normal runs share group `daily`.
- Permissions: `contents: write`, `pages: write`, `id-token: write`. Pages source is "GitHub Actions".

## Frontend
- **Dashboard** (`index.html`): notice banner (from `status.json`: no upload by 11:00 Riyadh, last run > 36 h ago, source errors); "Weekly avg (Since Sun, <Sunday date>)" cards for sleep, steps, calories
  (week-to-date: **steps and calories Sunday → yesterday**, **sleep and weight Sunday → today**, via `weekAvg` in `shared.js`) plus "Weight per week" (this week's average weight minus last week's average, shown as kg lost/gained); week strip Sunday→Saturday (green = trained, gray = planned
  training day not yet done, ring = today); one-line **Last Week** summary (Sunday–Saturday averages; steps and weight also show change vs the week before); 7-day table (Sleep, Steps, Cal, Kg, Lift minutes)
  with `*` marking corrected values; four 30-day charts.
- **Streaks section** (very end of the dashboard, below the charts): a flame tile with the calorie-logging streak and a 4-week calendar (`streakGrid`; green = calories recorded, ring = today, outlined = still to come), and a dumbbell tile with Hevy's lifetime workout count (`status.json` `hevy.total_workouts`) and a 12-week mini chart (`weeklyWorkouts`; green = reached the workouts goal). The streak (`loggingStreak` in `shared.js`) = consecutive days with calories in `data.json`; today does not break it until the day ends; the note says "counted from <date>" when the run reaches the first day we hold data for (the real streak may be longer), else "best N days". With the owner's baseline in `site/streaks.json` (MyFitnessPal's own number, read by hand: 568 days counted through 2026-10-26) the tile shows that number plus one per further logged day ("since 7 Apr 2025 · MyFitnessPal") whenever our unbroken run covers the baseline day; if a day is missed it falls back to our own count (K19).
- **Goal** (`goal.html`, a demo, in the top nav as "Goal"): headline (On track / Ahead of plan / Behind plan, amber when behind), a chart of the last 14 days of weigh-ins plus the dashed plan line to the target flag, **dot 1** (ring) = the planned weight today, **dot 2** (filled) = your 7-day average weight, a connector showing the gap, and a list: to go, plan pace, your pace, and the date you would hit the target at your current pace (days early/late). `goalStatus` rules: you = 7-day average ending today; gap = you minus plan; within 0.3 kg = on track; there is ONE rolling window that moves forward one day at both ends every day (`nowFrom..nowTo` = the 7 days ending today; shown on the page and shaded on the chart; `dayRange` formats it); pace = `weightTrend(days, nowFrom, nowTo)`, the least-squares slope of the weigh-ins inside that window in kg per week (needs at least 3 weigh-ins, uses the real day of each one, does not look at any other week; `se` = standard error of the slope in kg/week; `unclear` when |pace| < se, shown as "no clear trend" with no ETA); ETA = today + (to go / pace) weeks, only when pace is negative (losing). The goal is the fixed file `site/goal.json` (target 60 kg, 15 Dec 2026, start 64.0 kg on 26 Oct 2026).
- **Workouts** (`workouts.html`): Last workout rating, Overall rating (last 4 weeks), workouts-per-week chart (12 weeks, green ≥ goal, white below, fainter = current week), exercise list sorted by most
  recently trained with est. 1RM, change and sparkline, per-workout ratings with This week / Last week toggle (tap a workout for per-exercise changes).
- **Weeks** (`weeks.html`): a plain table of completed weeks, newest first (12 shown, "Show all N"): Sleep, Steps, Cal, Kg, Lifts; green when a standard is met (weight green when the average dropped by the goal vs the previous week); links to `WEEKLY_STATS.md` on GitHub.
- **Edit** (`edit.html`): admin sign-in with a pasted token (kept in `sessionStorage` key `motus-admin-token`, cleared when the tab closes); form to correct/clear a value or revert; corrections list.
  The table's day links and an "Edit data →" link inside the Standards panel appear only inside an admin session (the nav has five items: Dashboard, Workouts, Weeks, Goal, Standards; type and spacing tighten at <= 440, 380 and 350 px so all five fit down to 320 px, and the links row scrolls inside itself as a last resort so the page never widens).
- **Standards** (navbar panel, per device in `localStorage` key `stotis-goals`): steps/day (default 8000), sleep h/night (7), calories/day *less than* (1500), weight loss kg/week (0 = any loss), workouts/week (4),
  training days (Mon, Tue, Wed, Fri, Sat). Green when met. A one-time migration moves a saved calories value of 2000 to 1500 (flag `stotis-cal1500`).

### Rating algorithm (Workouts page; computed in the browser from `workouts.json` + `data.json`)
- **Estimated 1RM is computed by this project, not taken from Hevy** (Hevy's API has none): Epley `weight × (1 + reps/30)` per set; best set per exercise per day.
- **Per-exercise session score** (`sessionScore`): compare today's e1RM to the mean of that exercise's previous up to 4 sessions within the last 90 days (need ≥ 2). `pct ≥ 0` → `min(10, 7 + 0.3·pct%)`;
  `-5% ≤ pct < 0` → 7 (normal noise); below −5% → `max(3, 7 + 0.08·(pct% + 5))`. Exercises without enough recent history ("new") are skipped, not penalised. **Workout score** = mean over rated exercises; no rated exercise → "no data".
- **Overall rating (last 4 weeks)** = 0.7 × Progress + 0.3 × Consistency (if Progress has no data, Consistency alone). Progress: per exercise, mean e1RM over the last 28 days vs the 28 before (needs ≥ 2 sessions in each),
  score `clamp(5 + pct%, 0, 10)` (flat = 5), weighted by session count. Consistency: `min(10, 10 × avg workouts/week over 28 days ÷ goal)`. The Progress/Consistency breakdown lines were removed from the UI at the user's request but still drive the number.
  Note the scale mismatch with the per-workout score (see KNOWN_ISSUES).

## Authentication, authorization, security
- **Viewing is public** (no login). The repo, `data.json`, `inbox/` raw exports and the site are public by the user's decision (free GitHub Pages needs a public repo; see DECISIONS).
- **Writing**: only via GitHub. Pushes need repo write access. The phone uses a fine-grained token (Contents RW, this repo). Manual corrections use `workflow_dispatch` on `daily.yml`, which GitHub only allows for users with write access;
  `edit.py` additionally requires `github.actor == github.repository_owner`, validates every field, and receives inputs through environment variables (no shell interpolation). The admin token should be fine-grained with only **Actions: Read and write** on this repo
  (it cannot modify files directly). Verified live 2026-10-22: edit/sync/revert by the owner succeed; invalid input fails on the server; unauthenticated or fake-token dispatch and direct file writes return 401.
- The site contains no secrets; no write endpoint exists on the site itself (the edit page calls the GitHub API from the admin's browser with the admin's own token).
- `.gitignore` excludes `.env*` (except `.env.example`), keys/credentials patterns, generated copies in `site/`, `status.json`. A scan of the full git history found no secrets (2026-10-21).
- The Hevy key was once pasted into a chat; regenerating it is recommended (**Unknown** whether done).

## Secrets, tokens and configuration (names only — never put values in this repo)
| Name | Where | Purpose |
|---|---|---|
| `HEVY_API_KEY` | GitHub Actions secret + local `.env` | Hevy read access |
| iPhone upload token | Inside the Shortcut only | Fine-grained PAT, Contents RW on `alyamiMohd/motus`; expires (user chose up to 1 year; expiry date **Unknown**) — uploads fail silently after expiry |
| Admin edit token | Pasted into `edit.html`, `sessionStorage` only | Fine-grained PAT, Actions RW on this repo; **not yet created** (Unknown) |
| `STRAVA_CLIENT_ID/_SECRET/_REFRESH_TOKEN` | `.env.example` only | Unused |

## Deployment environment
GitHub Pages (workflow deployment) at https://alyamimohd.github.io/motus/. Free tier: Actions minutes are unlimited for public repos; Hevy PRO is the only recurring paid dependency (plus the Health Exporter app).
Scheduled runs can be delayed/dropped by GitHub; mitigated by an every-3-hours off-peak schedule, the staleness banner, the footer source times and failure alerts.

## Testing status
- `tests/test_pipeline.py`: 67 checks, all passing on 2026-10-22 (today's data arrives, history intact, no duplicates, no-op runs identical, edit/revert, correction survives sync, revert restores latest automatic value, 14 invalid/unauthorized requests rejected, corrupt overrides tolerated).
- `tests/test_week_logic.mjs`: 79 checks for `weekAvg`/`weekStart`/`loggingStreak`/`streakGrid`/`weeklyWorkouts`/`goalPlan`/`goalStatus` (steps/calories stop at yesterday, sleep/weight include today, Sunday/Saturday edges, no leakage across weeks), all passing on 2026-10-22.
- Live end-to-end on 2026-10-22: owner edit → normal sync → revert on a real date; invalid value rejected by the workflow; unauthenticated API calls rejected.
- Frontend: verified manually in the browser pane at 390px/320px widths with the console checked; no automated UI tests. Real iPhone Safari rendering is **Unverified**.
- **Unverified**: that a scheduled (cron) run has ever fired; the phone's Wake Up automation; the edit page driven by a real admin token from a browser (only a stubbed-fetch UI test and `gh workflow run` were done).
