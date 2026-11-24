# User profile: how to work with this owner

Only things the owner said or clearly showed are recorded here; anything inferred is marked `(inferred)`.

## Communication
- Language: English. Messages are short and informal, with occasional typos; read for intent. Sometimes pastes a long structured task (a spec or a checklist), which is their own instruction.
- Wants plain, short answers. "This is such a lot of stuff, I want you to redo it" (on a busy first dashboard); "simple and concise, like nothing much" (on the weeks page).
- Wants **step-by-step phone instructions** when something must be done on the iPhone (Shortcuts, Health, Files): give exact taps and say what the screen should show; they report back with screenshots.
- Wants the maths shown when a number looks odd: "Show me the maths u did for this".
- Wants honesty about what is verified. Their own task spec: "Do not claim an issue is fixed unless you have verified it."
- Tone: neutral and practical; no need for enthusiasm. They use they/them in all text about them (no pronouns known).

## Working style
- **Do the work for me**: "you create the github repo, after that we proceed". Prefers Claude to run commands, create things and verify, and to say what it needs from them. Never ask them to paste secrets in chat (they did paste one API key once; it was used and must not be repeated anywhere; rotation recommended).
- Wants **staged work with real-data testing**, handling missing days with "no data".
- Wants changes **committed, pushed and documented by default**: "Do not wait for me to explicitly request a commit or push."
- Reacts quickly with follow-ups mid-task; incorporate them without restarting.
- They answer questions selectively; several open questions were never answered (see `next-steps.md`). Do not block on them; state the default taken.

## Design preferences (quoted)
- "Minimalism is the main point of this website."
- Green means a standard is met. For the Last Week line: "make it a dark green, don't make it as light as other so that it doesn't take all the attention, but just make it noticable."
- Week strip like a row of numbered circles; workout days "marked green if its done, not white"; planned days grayed.
- Dislikes clutter: removed per-count colours legend text, the Progress/Consistency lines ("I don't know what it means"), the "Workouts this week" caption, repeated "avg since Sunday" labels.
- Wants things to work on an iPhone (they report layout problems from the phone).

## Corrections and strong opinions (quoted, with date)
- 2026-10-21 "no everything we doing is average, so it's not 1.3kg lost, count the average, compare it to the week before it average" (weekly comparisons are average-vs-average).
- 2026-10-21 "For the last week ... for the workout don't compare it with week before it, also calories same thing, and sleep" (only steps and weight show a change vs the week before).
- 2026-10-22 "How is it 0, i performed only 8% down lat pulldown... 0 means I didn't even train." (0 must never mean a trained workout.)
- 2026-10-22 "If there's new exercises, don't count them, and have the average of the workouts you have data for, and then base the score based on it."
- 2026-10-22 "For the steps don't count today's steps as it will usually show only the first few steps in the day" (steps and calories average Sunday to yesterday; sleep and weight Sunday to today).
- 2026-10-21 "you can make the data public no worries, just make sure my api keys are safe."
- 2026-10-22 "Not everything is a bug": checked and confirmed "there's no workout today, i was just checking".

## Environment
- Windows 11 laptop (Claude Code desktop app, Git Bash + PowerShell), iPhone with Shortcuts and Apple Health; Apple Watch likely (inferred from staged sleep data). Timezone **Asia/Riyadh (UTC+3, no DST)**, weeks start **Sunday**.
- Accounts/services (names only): GitHub (owner `alyamiMohd`, `gh` CLI signed in), Hevy (PRO, API key), MyFitnessPal (syncs calories to Apple Health), Strava (dropped, API needs a paid plan).
- Third-party iPhone app used: "Health Exporter & Shortcuts" (not Health Auto Export; the owner declined that app).

## Things that frustrated them
- Data not updating without any sign why; a workout rating of 0.0; the week strip looking wrong on iPhone; being asked to do work Claude could do.
