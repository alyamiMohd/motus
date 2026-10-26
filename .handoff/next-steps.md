# Next steps (as of 2026-10-24)

## Prioritized
- [x] **Done 2026-10-26** (row for 18–24 Oct present; runs green). **Sunday 2026-10-25: verify the first live weekly rollover.** After the run following Saturday, `weeks.json` and `WEEKLY_STATS.md` must gain a row for 18–24 Oct (check `gh run list`, the repo file, and https://alyamimohd.github.io/motus/weeks.html). Covered by tests but never seen live. Also confirm that on that Sunday the dashboard shows "no data" for steps/calories (by design) and the Last Week line switches to 18–24 Oct.
- [ ] **Late sleep (K3):** check whether today's sleep appears in the afternoon exports. If it only ever arrives late, consider moving or adding a phone automation in the afternoon (owner's phone, not code).
- [ ] **Admin token (K8):** the owner creates a fine-grained token (Actions: read/write, repository `motus` only, short expiry) and tries `site/edit.html` once with a real browser; fix anything that breaks. Server side is already verified.
- [ ] **Check the long sleep nights (K4):** 2026-09-24, 09-26, 10-16 (13.3 h), 10-20 (12.15 h). If Health shows ~7 h, find where the export double counts and correct via the edit page or the script.
- [ ] **Real iPhone check (K10):** ask the owner to confirm the week strip, nav and tables look right on the phone after a hard refresh.
- [ ] **Failure-alert path (K18):** verify live that a source error fails the run after deploying and that GitHub e-mails (owner must have Actions notifications on). Needs the owner's OK to briefly break the Hevy secret, or wait for a real failure.

## Waiting on the owner (ask, do not assume; state the default taken)
- [ ] Lock or leave the Standards panel (K12)? Default: left as is.
- [ ] Weekly workout goal: 4 or 5 (training days are Mon/Tue/Wed/Fri/Sat)? Default: 4.
- [ ] Add other Health metrics already in the export (resting heart rate, HRV, macros, sleep stages…)? Default: none.
- [ ] Align the overall rating scale with the per-workout scale (K6)? Default: not aligned.
- [ ] Show last week's average on Sundays when steps/calories have nothing yet? Default: "no data".
- [ ] Revisit privacy (data/handoff are public) if the owner changes their mind: options are Cloudflare Pages + Access (free login) or a second private repo for the handoff.
- [ ] MyFitnessPal's own logging streak: if the owner wants the app's real number, they read it in the app and tell Claude; add it as a manual baseline (K19). Default: the streak computed from our data, counted from 1 Sep.
- [ ] Goal demo: does the owner want it kept, changed (target/date/start weight in `site/goal.json`), or promoted into the nav? Default: stays a demo behind the Standards panel link.
- [ ] Rotate the Hevy API key (it was pasted into a chat once) and renew the phone upload token before it expires (date unknown).

## Blocked
- Strava: blocked by the paid API requirement (dropped).
- Changing anything on the phone: only the owner can; give exact taps.

## Parked ideas
- Workout corrections that also affect per-exercise ratings (K9).
- Frontend automated tests (K16).
- More weekly stats columns (sleep stages, resting heart rate) once such metrics are added.
- A cap or flag for implausible MyFitnessPal days (K11).
