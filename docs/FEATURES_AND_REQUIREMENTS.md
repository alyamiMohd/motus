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
| D6 | Run every morning at 06:00 Riyadh | in progress | `daily.yml` | **Cron has never been observed firing.** Now 3 off-peak schedules (06:17/09:17/12:17 Riyadh); confirm a `schedule` run appears. |
| D7 | Reliability signals: `status.json`, failure alert, staleness banner | implemented | `daily.py`, `check_status.py`, `daily.yml`, `index.html` | Source error → run fails after deploy; banner on no upload by 11:00 / run >36 h old. Banner logic verified with synthetic statuses. |
| D8 | Strava cardio | planned (dropped) | — | Blocked: API needs paid subscription. |

## Dashboard (`site/index.html`)
| # | Item | Status | Acceptance · notes |
|---|---|---|---|
| U1 | Averages for sleep, steps, calories from **Sunday to today**, resetting each Sunday; heading "Avg since Sunday, <date>" | verified | Matches independent calculation. Includes today's partial steps (decision pending, see KNOWN_ISSUES). |
| U2 | Weight per week card (kg lost/gained) | implemented | Green when loss ≥ goal. Based on single readings → noisy (smoothing proposed, not approved). |
| U3 | Week strip Sun→Sat: green = trained, gray = planned training day, ring = today | verified (emulated phone) | Fits at 390/320 px. Real iPhone unverified. |
| U4 | One-line **Last Week:** Sunday–Saturday averages; steps and weight show change vs week before; values dark green when standard met; pipe separators | verified | Calories, sleep, workouts show no comparison (user request). |
| U5 | Daily table (7 days) with Lift minutes; "no data" for missing | verified | `*` marks corrected values (original in tooltip). |
| U6 | 30-day charts (sleep, steps, calories, weight) | verified | Bars green when standard met; weight is a line. |
| U7 | Standards panel (steps, sleep, calories *less than*, weight loss/week, workouts/week, training days) | verified | Per-device (`localStorage`); changes recolor live. Lock/visitor-proofing question unanswered. |
| U8 | Staleness/error banner | implemented | See D7. |
| U9 | Minimalist look, black/white + green, works on phones | verified (emulated) | |

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
