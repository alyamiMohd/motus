# Known issues

Close an issue only after verification; move it to "Closed" with the date and how it was verified.

## Open
| ID | Issue | Evidence / status |
|---|---|---|
| K1 | **Scheduled (cron) runs have never been observed.** The 06:00 UTC+3 schedule did not fire on 2026-10-22 (cause: cron on `:00`, which GitHub often delays/drops). Schedule moved to every 3 hours at :17 on 2026-10-22. | Unverified fix. Check `gh run list --event schedule`; confirm one appears. |
| K2 | **Phone upload is not guaranteed daily.** No upload arrived by the morning of 2026-10-22; the first came at 10:20 after the user ran the shortcut by hand. Whether the *Wake Up* automation exists/fires is Unknown. | The dashboard banner appears after 11:00 Riyadh if no upload yet today. |
| K3 | **Today's sleep arrives late in the export.** Seen on 2026-10-21 (missing at 14:43, present at 15:35) and 2026-10-22 (missing at 10:20). Cause unknown (the export app, or watch→phone sync). | Open. Idea: run the automation (or a second one) in the afternoon. |
| K4 | **Implausibly long sleep values** (12–16 h): 2026-09-24, 09-26, 10-16 (13.3), 10-20 (12.15). Suspected double counting or naps merged into one day. | Unverified; the user was asked to compare with the Health app. Corrections can be made via the edit page. |
| K5 | **Two definitions of weight change.** Top card = latest reading vs previous reading per week (noisy: flipped −0.2 → +0.3 kg when only the date rolled over); Last Week line = average vs previous week's average. | Proposal pending the user's answer: base the top card on weekly averages. |
| K6 | **Overall rating scale vs per-workout scale mismatch.** Overall Progress uses flat = 5/10 (`clamp(5 + pct%, 0, 10)`), per-workout uses normal session = 7. | Not yet aligned; the user has not asked. Overall rating currently 6.7. |
| K7 | **Today's partial steps** are included in the week-to-date steps average, which reads low early in the week (very low on Sunday morning). | Decision pending (offered to exclude today for steps). |
| K8 | **Admin edit flow not exercised from the browser with a real token.** The admin token has not been created. Server side was verified via `gh workflow run`; UI verified with a stubbed fetch. | Needs the user to create a fine-grained token (Actions: read/write, this repo) and try `site/edit.html`. |
| K9 | **Workout corrections don't affect the Workouts page ratings** (per-exercise history comes from Hevy). | By design/limitation; documented. |
| K10 | **Real iPhone rendering unverified.** The user reported a bad display of the week strip on 2026-10-21; the layout was rebuilt (7-column grid, tested at 390/320 px emulated) but not confirmed on the device. Safari caches CSS aggressively. | Ask the user to confirm after a hard refresh. |
| K11 | **Backfill data quality.** `history/mfp-calories.json` contains extreme days (Sep 7: 5077, Sep 10: 6861, Sep 11: 5370, Sep 22: 7636, Sep 23: 6066, mostly "Quick Add" entries) and likely incomplete days (Oct 10: 957, Oct 14: 1146, Oct 20: 500). `history/mfp-weight.json` is read from a chart (±0.1 kg). | Left as logged; no decision yet. |
| K12 | **Standards can be changed by any visitor on their own device.** The "lock the panel" option was offered 2026-10-21 and not answered. | Open question (no security impact: changes are local to the visitor). |
| K13 | **Phone upload token expires** (user-chosen lifetime, up to 1 year; date Unknown); uploads then fail silently and only the stale-data banner reveals it. Also the Hevy key was pasted into a chat once (rotation recommended; Unknown if done). | Set a calendar reminder. |
| K14 | **Weekly goal (4) vs planned training days (5)**; the caption/colors use the goal. | The user has not decided to change it. |
| K15 | Workflow push step resolves rebase conflicts with `-X theirs` (my side wins). Generated files are regenerated next run, so the worst case is a briefly stale file, but two simultaneous correction runs could drop one correction. | Low risk; not reproduced. |
| K17 | **A workout done today does not appear until Hevy has it.** On 2026-10-22 (about 10:40 Riyadh) Hevy's API listed 331 workouts, the newest being Wed 2026-10-21 19:04–20:04, and its events feed showed nothing newer, so Thu 22 had no Lift value although the user believed a workout existed. The fetcher was checked for ordering/pagination bugs and is correct. Likely cause: workout not finished/synced in the Hevy app. | Open until the user confirms in the Hevy app. Mitigation shipped: runs every 3 hours; footer shows "Hevy: last workout …". |
| K16 | No automated tests for the frontend or the Hevy client; `tests/test_pipeline.py` covers `daily.py`/`edit.py`/`overrides.py` only. | Technical debt. |

## Closed
| ID | Issue | Closed | Verification |
|---|---|---|---|
| C1 | Dashboard showed "no data" for Oct 20–21 sleep although Health had it | 2026-10-21 | A fresh export contained both nights and they appeared on the live site (timing issue, see K3 for the recurring pattern). |
| C2 | Workout rating 0.0 for the 2026-10-21 Pull session | 2026-10-22 | Cause: harsh scale (anything below −5% = 0) with only two rated exercises. Scale changed (see DECISIONS); the session now rates 6.1. |
| C3 | Seated Incline Curl compared against months-old sessions | 2026-10-22 | Baselines limited to the previous 90 days; shows "not rated (new)". |
| C4 | Local preview hung | 2026-10-21 | `serve.py` made threaded and uncached. |
| C5 | Rename left the old repo address in place for the phone | 2026-10-22 | Probe: old API URL returns a 307 redirect (method preserved); end-to-end on the phone still Unverified (K2). |
