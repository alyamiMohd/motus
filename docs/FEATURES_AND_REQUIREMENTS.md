# Features and requirements

Status: **planned · in progress · implemented · verified**. "Verified" means tested/observed (see PROJECT_CONTEXT → Testing status). Dates are 2026.

## Data and pipeline
| # | Item | Status | Files | Acceptance criteria · outstanding |
|---|---|---|---|---|
| D1 | Daily record per date merged from all sources; full history kept | verified | `daily.py`, `data.json` | One record per date, no duplicates, history never overwritten; no-op run leaves file identical (tests). |
| D2 | Hevy workouts (count, minutes, volume, titles) + per-exercise e1RM history, read-only | verified | `fetch_hevy.py`, `workouts.json` | Only `GET`; all history each run; Riyadh day grouping. |
| D3 | Apple Health ingestion from phone uploads (steps, sleep, weight, calories, active kcal) | implemented | `daily.py`, `inbox/` | Newest upload wins per date; 0 = no data. **Phone automation unverified.** |
| D4 | iPhone Shortcut uploads export to the repo via GitHub API | implemented | (outside repo) | File appears in `inbox/` and triggers a run. Needs token renewal reminder; see KNOWN_ISSUES. |
| D5 | MyFitnessPal backfills (calories Sep 1–Oct 21, weight Sep 22–Oct 21) as gap-fill | implemented | `history/*.json`, `daily.py` | Health values always win. Weight values are chart estimates ±0.1 kg. |
| D6 | Refresh automatically (originally "every morning at 06:00 Riyadh") | in progress | `daily.yml` | **Cron has never been observed firing.** Now every 3 hours at :17 so late-synced Hevy workouts/uploads appear within hours; confirm a `schedule` run appears. |
| D7 | Reliability signals: `status.json`, failure alert, staleness banner | implemented | `daily.py`, `check_status.py`, `daily.yml`, `index.html` | Source error → run fails after deploy; banner on no upload by 11:00 / run >36 h old. Banner logic verified with synthetic statuses. |
| D8 | Strava cardio | planned (dropped) | — | Blocked: API needs paid subscription. |

## Dashboard (`site/index.html`)
| # | Item | Status | Acceptance · notes |
|---|---|---|---|
| U1 | Week-to-date averages (weeks start Sunday), resetting each Sunday; heading "Weekly avg (Since Sun, <Sunday date, e.g. 18 Oct>)" (it does not mention that steps/calories stop at yesterday; the rule is documented here and in DECISIONS). **Steps and calories: Sunday → yesterday** (today is a partial day); **sleep and weight: Sunday → today** | verified | Rule lives in `weekAvg` (`site/shared.js`), 16 unit tests; matches an independent calculation. On a Sunday steps/calories show "no data" (nothing complete yet). |
| U2 | Weight card: this week's average (Sunday → today) minus last week's average (kg lost/gained) (the average weight is deliberately not shown on this card; it was added and removed on 2026-10-26 at the owner's request) | verified | Green when loss ≥ goal. Needs readings in both weeks, else "no data". |
| U3 | Week strip Sun→Sat: green = trained, gray = planned training day, ring = today | verified (emulated phone) | Fits at 390/320 px. Real iPhone unverified. |
| U4 | One-line **Last Week:** Sunday–Saturday averages; steps and weight show change vs week before; values dark green when standard met; pipe separators | verified | Calories, sleep, workouts show no comparison (user request). |
| U5 | Daily table (7 days) with Lift minutes; "no data" for missing | verified | `*` marks corrected values (original in tooltip). |
| U6 | 30-day charts (sleep, steps, calories, weight) | verified | Bars green when standard met; weight is a line. |
| U7 | Standards panel (steps, sleep, calories *less than*, weight loss/week, workouts/week, training days) | verified | Per-device (`localStorage`); changes recolor live. Lock/visitor-proofing question unanswered. |
| U8 | Staleness/error banner | implemented | See D7. |
| U9 | Minimalist look, black/white + green, works on phones | verified (emulated) | |
| U11 | **Weeks page**: simple table of every completed Sunday-Saturday week (sleep, steps, calories, weight, lifts), newest first, green when a standard is met | verified (emulated phone) | Fits at 390/320 px; links to `WEEKLY_STATS.md`. |
| U12 | **Streaks section at the very end of the dashboard**: a flame tile (calorie-logging streak, with a 4-week calendar of logged days) and a dumbbell tile (Hevy lifetime workouts, with a 12-week mini chart; green weeks reached the workouts goal) | verified (35 Node tests, live data 55-day streak, 332 workouts; fits 390 and 320 px) | The streak is computed from our data, not MyFitnessPal's own number (K19). |
| U10 | Footer shows what each source last delivered ("Hevy: last workout …· Health: last upload …· checked …") | verified | Lets a missing workout/upload be diagnosed from the page. |

## Weekly history
| # | Item | Status | Files | Acceptance criteria · notes |
|---|---|---|---|---|
| H1 | A file that keeps the weekly stats: new week finishes → its row is added, pushed to GitHub; readable later | verified | `weekly.py`, `weeks.json`, `WEEKLY_STATS.md`, `daily.yml` | Completed Sunday-Saturday weeks only; the first run after a week ends adds it; derived from `data.json`, so late data/corrections update that week; quiet runs commit nothing (67 tests incl. Sunday/Saturday edges). **The Sunday-rollover append itself has not yet been seen live** (first chance: Sunday 2026-10-25 run). |
| H2 | Interface for browsing the weekly stats | verified | `site/weeks.html` | Simple, concise, phone-safe; "Show all". |

## Workouts page (`site/workouts.html`)
| # | Item | Status | Acceptance · notes |
|---|---|---|---|
| W1 | Last workout rating (/10) shown first, then Overall rating (last 4 weeks) | verified | Overall's Progress/Consistency lines hidden by request. |
| W2 | Per-workout rating from own e1RM; new exercises skipped; 7 = normal session, up to 10, floor 3; 0 never shown for a trained workout | verified (numbers checked) | Wed Oct 21 workout = 6.1 (user expected 6–7). |
| W3 | Workouts-per-week chart, 12 weeks, green ≥ goal else white, legend, current week fainter | verified | |
| W4 | Exercises sorted by most recently trained, with est. 1RM, change vs previous 4 weeks, sparkline; Show all | verified | New exercises marked "new". |
| W5 | This week / Last week per-workout ratings with per-exercise breakdown | verified | Weeks start Sunday. |

## Manual corrections (admin)
| # | Item | Status | Acceptance · notes |
|---|---|---|---|
| E1 | Edit/clear a value for a date+metric from the site, revert to original | implemented / server path verified | Owner-only via workflow; validated server-side; original preserved; survives syncs; revert restores latest automatic value (tests + live). **Browser flow with a real admin token not yet exercised; token not created.** |
| E2 | Public visitors cannot modify anything | verified | Unauthenticated/fake-token dispatch and writes → 401; no write endpoint on site. |
| E3 | Corrected values visible/distinguishable | verified | `*` marker; edit page shows original and note. |
| E4 | Workout corrections affect rating page | planned/not supported | Count/minutes/volume corrections change dashboard and week strips; per-exercise history (Hevy) is not editable. |

## Requirements stated by the user (carry forward)
- Health data may be public; **API keys must never be exposed**; read-only access to Hevy.
- Minimalism is the main design goal; green = met standard; clear "no data" instead of crashes.
- Weeks start Sunday; planned training days Mon/Tue/Wed/Fri/Sat; weekly workout goal currently 4 (training plan has 5 days — user has not confirmed changing the goal).
- Calories standard is an upper limit (default 1500).
- Rating out of 10 based on 1RM; 0 must mean "did not train".
- Data must never be silently overwritten; manual corrections must not be overwritten by sync and must be revertable.
- Every change is committed and pushed with its documentation (see `CLAUDE.md`).

## Ideas not requested yet (data already in the export, unused)
Resting heart rate, HRV, exercise minutes, flights climbed, walking distance, VO2 max, body fat/BMI, blood oxygen, respiratory rate, wrist temperature, macros (protein/carbs/fat), sleep stages (deep/REM). Status: **planned (unscheduled)**; none implemented.
