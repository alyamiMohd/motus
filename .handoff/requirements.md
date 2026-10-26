# Requirements (master list)

Status: `open` · `in progress` · `done` · `changed` · `dropped`. Dates are 2026. "Where" points to files/commits. Quotes are the owner's words.

## Original brief (2026-10-21, pasted spec)
| ID | Owner's words | Interpretation | Status | Where / notes |
|---|---|---|---|---|
| R-001 | "a personal fitness dashboard website that updates itself every morning" showing "my averages for the last 7 days: sleep (hours), steps, calories, and weight change (lost/gained). Below that, a simple daily table and a small chart for each metric." | Static site, auto-updating | done (evolved, see R-020…) | `site/index.html` |
| R-002 | Sources: "Hevy (workouts): REST API"; "Strava (cardio): official API with OAuth refresh token"; "iPhone sleep, steps and weight, plus MyFitnessPal calories (synced into Apple Health)" via an app dropping JSON in a cloud location | Hevy read-only; Strava; phone data via cloud | Hevy done; **Strava dropped** (API app needs a paid subscription); phone data **changed** (see R-003) | `fetch_hevy.py` |
| R-003 | Owner first wanted Google Drive: "I would rather export everything to google drive ... after sharing it from ios as shortcut"; then "let's not do google drive, I will upload the health export to the ios files"; then accepted GitHub | Phone data reaches the repo through an iPhone Shortcut that PUTs the export JSON to `inbox/` via the GitHub API | done | Shortcut (outside repo), `inbox/`, `daily.py` |
| R-004 | "A Python script (daily.py) fetches all sources, merges them into one record per day, and saves them to data.json (keep full history)." | | done | `daily.py`, `data.json` |
| R-005 | "A GitHub Actions workflow runs the script every day at 6:00 AM Riyadh time (03:00 UTC)" | | **changed**: now every 3 hours at :17 UTC (cron never fired at `:00`) | `.github/workflows/daily.yml` |
| R-006 | Security: "Never put API keys in code. ... GitHub Actions Secrets and environment variables only", `.gitignore` for `.env`, "Use read-only API scopes wherever possible" | | done | `.gitignore`, secret `HEVY_API_KEY` |
| R-007 | "Private GitHub repo. My health data must NOT be public." | | **changed 2026-10-21**: "you can make the data public no worries, just make sure my api keys are safe." Repo and site are public (free GitHub Pages). | D-005 |
| R-008 | "Build in stages ... Test each stage with real data ... handle missing days without crashing (show 'no data')." Final checklist of manual steps | | done | tests, README/docs |

## Setup guidance asked for
| R-009 | "tell me what to do to setup everything for you before I start" | Checklist of accounts/keys/phone steps | done | answered in chat |
| R-010 | "No I don't want to use an app, how do I make it natively" (then later accepted *Health Exporter & Shortcuts*) | | **changed** | D-003 |

## Dashboard
| R-011 | "Minimalism is the main point of this website"; "If the weight is dropping change it to green, If steps over 8k change to green" | One accent colour (green = standard met) | done | `site/style.css`, `index.html` |
| R-012 | Navbar with "the standards (for steps, weight loss avg per week, sleep) so that changing it would reflect in the main dashboard (changing it to green if it passed that standard)"; later "add in the standards (less than) for the calories"; "make the standard calories 1500" | Per-device settings; defaults steps 8000, sleep 7, calories < 1500, weight loss any, workouts/week 4, training days Mon/Tue/Wed/Fri/Sat | done | `site/shared.js` |
| R-013 | "can anyone with access to the url change the standards? I don't want that" | They only change their own view (localStorage). Offered a locked config option | open question (unanswered) | `next-steps.md` |
| R-014 | "make it start always from sunday ... resets every sunday"; "Weekly avg (Since Sun, 21 Oct)" (owner's example date; Sunday's actual date is used, e.g. 18 Oct) | Week-to-date averages; heading shows the Sunday date | done | `weekAvg` in `site/shared.js` |
| R-015 | "For the steps don't count today's steps ... same thing for the calories ... from sunday to yesterday, for steps and calories. But for weight and sleep make it from sunday to today as well. and add that in script as well" | One tested function + docs + tests | done | `tests/test_week_logic.mjs` |
| R-016 | Weight card as an average ("everything we doing is average") | This week's average minus last week's average | done | `weightPerWeek()` |
| R-017 | Last Week line: "summary of last week averages in a single line, simple minimalist"; Sunday–Saturday; separated by "|"; header "Last Week:"; weight "(-0.7 kg)"; no comparison for workouts, calories, sleep; dark green when standard met | | done | `lastWeekLine()` |
| R-018 | Hevy on the dashboard: "workouts/week count where the week starts at sunday" | Week strip + Lift column | done | |
| R-019 | Week strip "something like this" (row of numbered circles), "start from sunday", green when done, "gray out the days I should be working out: monday tuesday wednesday friday and saturday" | Editable training days in Standards | done | `weekStrip()` |
| R-020 | Source/footer visibility and no silent failures (from the "investigate why today's data hasn't updated" task) | Footer shows last Hevy workout / last upload / last check; banner when stale | done | `status.json`, `showFooter` |

## Workouts page
| R-021 | "a dedicated page where it shows how I'm progressing in my workouts, and a final rating of 10 for the workout based on the 1 rep max for the workouts" | Estimated 1RM (Epley) computed by us, not Hevy | done | `site/workouts.html` |
| R-022 | Workouts per week chart: first "a legend for 2, 3, 4, 5 (colors) instead of adding your numbers"; later "either green if its 4+ or white if its below 4" | | **changed** to green/white | |
| R-023 | "Always sort them by most recent" (1RM charts list) | | done | |
| R-024 | "remove the progress and consistency under overall rating as I don't know what it means" | Hidden in UI, still used internally | done | |
| R-025 | Last workout rating shown before the overall one; per-workout ratings; this/last week toggle | | done | |
| R-026 | "0 means I didn't even train"; "If there's new exercises, don't count them" | New scale: 7 = normal session, floor 3; new exercises skipped | done | `sessionScore` |

## Data and corrections
| R-027 | MyFitnessPal history: owner pasted the printable diary and a weight chart image | One-off gap-fill backfills | done | `history/*.json` |
| R-028 | "update cals of 20, and 21 to be 1250 calories" | Applied via the correction system (originals kept) | done 2026-10-22 | `overrides.json` |
| R-029 | Pasted task: investigate why today's data didn't update; add secure per-entry editing (admin only, server-side enforced, validated, revertable, survives sync) | | done | `overrides.py`, `edit.py`, `site/edit.html`; live-verified |
| R-030 | "include a file that keeps track of my weekly stats ... A new week comes in, pushes the old week stats ... all pushed to github ... Also make an interface to be able to see these weeks stats, simple and concise" | `weeks.json` + `WEEKLY_STATS.md`, Weeks page | done | `weekly.py`, `site/weeks.html` |

## Process
| R-031 | Pasted task: GitHub as source of truth, `CLAUDE.md` + `docs/*`, mandatory commit/push workflow for every change, recovery from a fresh session | | done | `CLAUDE.md`, `docs/` |
| R-032 | `/handoff` (this system) | | done 2026-10-22 | `.handoff/` |
| R-033 | Rename: "Change the name to Motus instead of Stotis, also change repo name from github" | | done | |
| R-034 | Hevy access strictly read-only ("MAKE SURE its only read only") | Verified in code (single GET) | done | `fetch_hevy.py` |

## Added 2026-10-26
| R-035 | "add the average weight as well next to the total lost in the average dashboards" | The weight card shows the week's average weight under the change (the Last Week line already shows average and change) | done | `site/index.html` |
| R-036 | "Import the streaks (from hevy add the total workouts done till now, and from myfitnesspal tell me how to get the total daily count streak)" | Hevy total from its API (332 at the time); logging streak computed from our calories data because MyFitnessPal's own streak cannot be imported; instructions for the app's number | done (limit: K19) | `loggingStreak` in `site/shared.js`, streaks line |

## Non-functional
Phone-first and working on an iPhone (390 and 320 px tested in emulation); free hosting; no framework; reliable and detectable failures; data never overwritten or duplicated; weeks start Sunday; timezone Riyadh.
