# RESUME: read this first

**Project:** Motus, a personal fitness dashboard (sleep, steps, calories, weight, Hevy workouts) that rebuilds itself on GitHub Actions and is served as a static site.
**Repo:** https://github.com/alyamiMohd/motus (public, branch `main`) · **Live site:** https://alyamimohd.github.io/motus/
**Last updated:** 2026-10-27 12:30 (UTC+03, Riyadh) · **Code state:** commit `09e4dbb` (bot data commits are omitted from this record). Work happened 2026-10-21/22/26/27; the handoff was first saved on 2026-10-24 and has been used by a second session on another computer.

## Instructions for Claude
1. Read in this order: `CLAUDE.md` → this file → `user-profile.md` → `requirements.md` → `decisions.md` → `project-state.md` → `next-steps.md` → the last 3 entries of `conversation-log.md` → `skills/`.
   The repo also has its own project memory: `docs/SESSION_HANDOFF.md`, `docs/PROJECT_CONTEXT.md`, `docs/FEATURES_AND_REQUIREMENTS.md`, `docs/DECISIONS.md`, `docs/KNOWN_ISSUES.md`, `docs/CHANGELOG.md`. Both systems are kept current.
2. Adopt `user-profile.md` from your first reply (plain, short, honest; do the work yourself; verify before claiming).
3. Do not re-ask what `requirements.md` / `decisions.md` already settle. Do not reverse a recorded decision silently.
4. Before anything: `git pull --rebase` (a bot commits `data.json` daily), check `git status`, compare code against the docs (trust the code and the live site when they disagree).
5. Give a 3–6 line "where we left off", then continue with the next action below.
6. Workflow for every change (from `CLAUDE.md`): implement → update docs → run `python tests/test_pipeline.py` and `node tests/test_week_logic.mjs` → verify UI in a browser at 390px and 320px → secret scan → commit + push → verify the remote commit and the Actions run → report. Also update `.handoff/` when you push (see `skills/github-session-handoff/SKILL.md`).

## Current status
- Live and working: dashboard (week-to-date averages, the weight card (only how much was lost), a streaks section at the very end with tiles for the MyFitnessPal logging streak (568 days, a manual baseline) and Hevy's total workouts, a **Goal Visualized (demo)** page (60 kg by 15 Dec 2026, in the top nav as "Goal": one rolling 7-day window ending today, "Your pace" = the kg/week trend inside that window only with no comparison, plan dot and 7-day-average dot labelled beside themselves, a gold glow and flag at the target labelled "Worth it", dot and headline turn gold when reached), week strip, Last Week line, 7-day table, 30-day charts, standards panel, source-times footer), Workouts page (ratings out of 10 from estimated 1RM, exercises newest first, weekly chart), Weeks page (history of completed weeks), admin Edit page (validated manual corrections via a GitHub workflow), staleness/error banner.
- Pipeline: iPhone Shortcut uploads Apple Health exports into `inbox/` (verified 2026-10-24: an upload arrives about 06:00 daily, plus extra uploads later in the day); Hevy is read-only; `daily.py` merges into `data.json`; `weekly.py` writes `weeks.json` + `WEEKLY_STATS.md`; the workflow runs every 3 hours at :17 UTC and on pushes. **Scheduled (cron) runs are confirmed firing** (9 seen, newest 2026-10-24 11:01 UTC); the earlier worry that they never ran is closed (docs C8, C9).
- Tests: 67 pipeline checks + 75 Node checks (averaging rule, streaks, calendar, weekly workouts, goal plan/status) all passing. Frontend verified manually in the browser pane (emulated phone widths); real iPhone Safari unverified.
- Data corrections applied by the owner: calories for 2026-10-20 and 2026-10-21 set to 1250 (originals kept in `data.json` `orig`).
- Repo and site are **public** by the owner's decision (see D-005). This handoff is public too.

## Next action
The first live Sunday rollover was **verified on 2026-10-26**: the week 18–24 Oct is in `weeks.json` / `WEEKLY_STATS.md`. Work through `next-steps.md`.
**Note (2026-10-26):** a public version for anyone to use now lives in a separate repo, `alyamiMohd/motusapp` (https://alyamimohd.github.io/motusapp/), with its own `.handoff/`. This repo stays the owner's personal dashboard.

## Open questions waiting on the owner
- Lock the Standards panel (visitors can change their own view only) or leave it? (asked, unanswered)
- Weekly workout goal is 4 but 5 training days are planned; change the goal to 5?
- Add other Health metrics already in the export (resting heart rate, HRV, macros, sleep stages…)?
- Did the 12–13 h sleep nights (e.g. 2026-10-16, 10-20) match the Health app? (suspected double counting)
- Does today's sleep show up in the afternoon exports? (it has arrived late in the export; cause unknown)
- Has the admin edit token been created (fine-grained, Actions read/write, this repo only)? Not yet.
- Show last week's average on Sundays instead of "no data" for steps/calories? (side effect of the averaging rule)

## Last thing in progress
Goal page polish for the owner, all shipped and verified live (last commit `09e4dbb`): pace as a single window (R-042), golden end of the graph and tidy number placement (R-043), the flag label "Worth it". The owner then typed `/handoff` (this save). Nothing is half-done.