// Tests for the week-to-date averaging rule in site/shared.js (weeks start Sunday).
// Steps and calories stop at YESTERDAY (today is a partial day); sleep and weight include TODAY.
// Run from the repo root:  node tests/test_week_logic.mjs   (exit code 0 = all passed)
import { readFileSync } from "node:fs";

const code = readFileSync(new URL("../site/shared.js", import.meta.url), "utf8");
const { weekStart, add, weekAvg, loggingStreak, streakGrid, weeklyWorkouts, daysBetween, goalPlan, goalStatus } = new Function(code + "\nreturn { weekStart, add, weekAvg, loggingStreak, streakGrid, weeklyWorkouts, daysBetween, goalPlan, goalStatus };")();

let passed = 0;
const failed = [];
const check = (name, ok, extra = "") => {
  if (ok) { passed++; console.log("  PASS ", name); }
  else { failed.push(name); console.log("  FAIL ", name, extra); }
};
const near = (a, b) => a !== null && Math.abs(a - b) < 1e-9;

// Sun 18 Oct 2026 .. Sat 24 Oct. Today's values are deliberately tiny ("first few steps of the day").
const days = {
  "2026-10-17": { steps: 99999, calories: 9999, sleep_hours: 9, weight_kg: 90 },   // last week: must never leak in
  "2026-10-18": { steps: 6000, calories: 1500, sleep_hours: 6.0, weight_kg: 65.0 },
  "2026-10-19": { steps: 10000, calories: 1400, sleep_hours: 8.0, weight_kg: 64.0 },
  "2026-10-20": { steps: null, calories: null, sleep_hours: null, weight_kg: null },  // a day with no data
  "2026-10-21": { steps: 8000, calories: 1600, sleep_hours: 7.0, weight_kg: 64.0 },
  "2026-10-22": { steps: 400, calories: 300, sleep_hours: 7.0, weight_kg: 63.0 },   // "today" in most tests
  "2026-10-23": { steps: 12000, calories: 2000, sleep_hours: 5.0, weight_kg: 70.0 }, // the future: must never leak in
};

console.log("weekStart");
check("Thursday -> its Sunday", weekStart("2026-10-22") === "2026-10-18");
check("Sunday -> itself", weekStart("2026-10-18") === "2026-10-18");
check("Saturday -> the Sunday before", weekStart("2026-10-24") === "2026-10-18");

console.log("Thursday 22 Oct (mid-week)");
let t = "2026-10-22";
check("steps skip today: mean(6000, 10000, 8000)", near(weekAvg(days, "steps", t), 8000), weekAvg(days, "steps", t));
check("calories skip today: mean(1500, 1400, 1600)", near(weekAvg(days, "calories", t), 1500), weekAvg(days, "calories", t));
check("sleep includes today: mean(6, 8, 7, 7)", near(weekAvg(days, "sleep_hours", t), 7), weekAvg(days, "sleep_hours", t));
check("weight includes today: mean(65, 64, 64, 63)", near(weekAvg(days, "weight_kg", t), 64), weekAvg(days, "weight_kg", t));
check("a no-data day is ignored, not counted as zero", weekAvg(days, "steps", t) > 7000);

console.log("Sunday 25 Oct (new week, nothing complete yet)");
t = "2026-10-25";
check("steps: nothing before today this week -> null", weekAvg({ ...days, "2026-10-25": { steps: 50 } }, "steps", t) === null);
check("calories: null too", weekAvg({ ...days, "2026-10-25": { calories: 80 } }, "calories", t) === null);
check("sleep counts today alone", near(weekAvg({ "2026-10-25": { sleep_hours: 6.5 } }, "sleep_hours", t), 6.5));
check("last week's days do not leak into the new week", weekAvg(days, "sleep_hours", t) === null);

console.log("Monday 19 Oct (second day of the week)");
t = "2026-10-19";
check("steps = Sunday only", near(weekAvg(days, "steps", t), 6000));
check("sleep = Sunday + Monday", near(weekAvg(days, "sleep_hours", t), 7));

console.log("Saturday 24 Oct (last day of the week)");
t = "2026-10-24";
check("steps = Sunday..Friday (the 23rd's 12000 counts, Saturday does not exist yet)", near(weekAvg(days, "steps", t), (6000 + 10000 + 8000 + 400 + 12000) / 5));
check("no data anywhere -> null", weekAvg({}, "steps", t) === null);

// ---- calorie-logging streak -------------------------------------------------------------------------------------------
const logDays = (from, to, kcal = 1500) => { const o = {}; for (let d = from; d <= to; d = add(d, 1)) o[d] = { calories: kcal }; return o; };

console.log("loggingStreak");
let st = loggingStreak(logDays("2026-10-01", "2026-10-22"), "2026-10-22");
check("22 consecutive days ending today", st.current === 22 && st.best === 22, st);
st = loggingStreak(logDays("2026-10-01", "2026-10-21"), "2026-10-22");
check("today not logged yet does NOT break the streak (counted to yesterday)", st.current === 21, st);
st = loggingStreak(logDays("2026-10-01", "2026-10-20"), "2026-10-22");
check("yesterday and today both missing -> streak is 0", st.current === 0 && st.start === null, st);
st = loggingStreak({ ...logDays("2026-10-01", "2026-10-10"), ...logDays("2026-10-12", "2026-10-22") }, "2026-10-22");
check("a gap day ends the old run; current is the run after it", st.current === 11, st);
check("best remembers the longest run in the data", loggingStreak({ ...logDays("2026-09-01", "2026-09-20"), ...logDays("2026-10-12", "2026-10-22") }, "2026-10-22").best === 20);
st = loggingStreak({ ...logDays("2026-10-01", "2026-10-20"), "2026-10-21": { calories: null }, "2026-10-22": { calories: 1400 } }, "2026-10-22");
check("a null day breaks the streak (only today counts: 1)", st.current === 1, st);
st = loggingStreak({ ...logDays("2026-10-01", "2026-10-20"), "2026-10-21": { calories: 1000 }, "2026-10-22": { steps: 5000 } }, "2026-10-22");
check("a day with other data but no calories is not logged; yesterday still counts", st.current === 21, st);
st = loggingStreak(logDays("2026-09-01", "2026-10-25"), "2026-10-26");
check("capped: the run reaches the first day we have data for", st.capped === true && st.start === "2026-09-01" && st.current === 55, st);
st = loggingStreak({ ...logDays("2026-09-01", "2026-09-05"), ...logDays("2026-10-01", "2026-10-22") }, "2026-10-22");
check("not capped when an earlier day exists before a gap", st.capped === false && st.current === 22, st);
check("no data at all -> zeros", JSON.stringify(loggingStreak({}, "2026-10-22")) === JSON.stringify({ current: 0, best: 0, start: null, capped: false, fromApp: false }));
check("month boundary is handled (28 Sep -> 3 Oct = 6 days)", loggingStreak(logDays("2026-09-28", "2026-10-03"), "2026-10-03").current === 6);

// ---- streak calendar and weekly workouts (the end-of-page tiles) -----------------------------------------------------
console.log("streakGrid / weeklyWorkouts");
const gdays = { ...logDays("2026-10-01", "2026-10-22"), "2026-10-23": { steps: 1 } };    // Thu 22 Oct 2026 is "today"
const grid = streakGrid(gdays, "2026-10-22");
check("4 weeks = 28 cells, oldest first, starting on a Sunday", grid.length === 28 && grid[0].date === "2026-09-27" && weekStart(grid[0].date) === grid[0].date, grid[0]);
check("the last cell is this week's Saturday", grid[27].date === "2026-10-24");
check("exactly one cell is today", grid.filter(c => c.today).length === 1 && grid.find(c => c.today).date === "2026-10-22");
check("days after today are flagged future (Fri, Sat)", grid.filter(c => c.future).map(c => c.date).join() === "2026-10-23,2026-10-24");
check("logged follows calories only (a day with other data is not logged)", grid.find(c => c.date === "2026-10-23").logged === false && grid.find(c => c.date === "2026-10-22").logged === true && grid.find(c => c.date === "2026-09-30").logged === false);
check("a Sunday 'today' still shows the whole current week", streakGrid({}, "2026-10-25")[27].date === "2026-10-31" && streakGrid({}, "2026-10-25")[21].date === "2026-10-25");

const wd = { "2026-10-12": { workout_count: 1 }, "2026-10-14": { workout_count: 1 }, "2026-10-19": { workout_count: 1 }, "2026-10-20": { workout_count: 2 }, "2026-10-04": { workout_count: 3 }, "2026-10-21": { workout_count: null } };
const wk = weeklyWorkouts(wd, "2026-10-22", 4);
check("weekly workouts: 4 weeks, oldest first, current (partial) week last", wk.length === 4 && wk.join() === "0,3,2,3", wk);
check("default is 12 weeks and all-zero when there is no data", weeklyWorkouts({}, "2026-10-22").length === 12 && weeklyWorkouts({}, "2026-10-22").every(c => c === 0));

// ---- goal visualized (demo): plan line, status against it, pace and projected date ------------------------------------
console.log("goalPlan / goalStatus");
const goal = { target_kg: 60, target_date: "2026-12-15", start_date: "2026-10-26", start_kg: 64 };
const kgDays = (from, to, kg) => { const o = {}; for (let d = from; d <= to; d = add(d, 1)) o[d] = { weight_kg: kg }; return o; };

check("daysBetween: 26 Oct -> 15 Dec is 50 days", daysBetween("2026-10-26", "2026-12-15") === 50);
check("plan starts at the start weight and ends at the target", goalPlan(goal, "2026-10-26") === 64 && goalPlan(goal, "2026-12-15") === 60);
check("plan is a straight line (day 25 of 50 = halfway = 62)", Math.abs(goalPlan(goal, "2026-11-20") - 62) < 1e-9);
check("plan after day 1 is 64 - 4/50", near(goalPlan(goal, "2026-10-27"), 64 - 4 / 50));
check("plan is flat before the start and after the target", goalPlan(goal, "2026-10-01") === 64 && goalPlan(goal, "2027-01-30") === 60);

let gs = goalStatus({ ...kgDays("2026-10-13", "2026-10-19", 65), ...kgDays("2026-10-20", "2026-10-26", 64) }, goal, "2026-10-26");
check("on track: you equal the plan, gap 0", gs.state === "on" && near(gs.gap, 0) && gs.now === 64 && gs.planToday === 64, gs);
check("to go = 4 kg, 50 days left, plan pace -0.56 kg/week", near(gs.toGo, 4) && gs.daysLeft === 50 && near(gs.planPace, -4 / (50 / 7)), gs);
check("pace = this week's average minus last week's (-1 kg/week)", near(gs.pace, -1), gs.pace);
check("at that pace: 4 kg / 1 per week = 28 days -> 23 Nov, 22 days early", gs.etaDate === "2026-11-23" && gs.etaVsTarget === -22, gs);

const behind = goalStatus(kgDays("2026-10-21", "2026-10-27", 64.5), goal, "2026-10-27");
check("behind: heavier than the plan by more than 0.3 kg", behind.state === "behind" && behind.gap > 0.3, behind);
const ahead = goalStatus(kgDays("2026-10-21", "2026-10-27", 63.0), goal, "2026-10-27");
check("ahead: lighter than the plan by more than 0.3 kg", ahead.state === "ahead" && ahead.gap < -0.3, ahead);
check("0.3 kg over the plan still counts as on track; just beyond it is behind",
  goalStatus(kgDays("2026-10-20", "2026-10-26", 64.3), goal, "2026-10-26").state === "on" && goalStatus(kgDays("2026-10-20", "2026-10-26", 64.31), goal, "2026-10-26").state === "behind");

const none = goalStatus({}, goal, "2026-10-26");
check("no weights at all -> null everything, no state", none.now === null && none.gap === null && none.state === null && none.pace === null && none.etaDate === null);
const oneWeek = goalStatus(kgDays("2026-10-20", "2026-10-26", 64), goal, "2026-10-26");
check("only one week of data: status works, pace and ETA are null", oneWeek.state === "on" && oneWeek.pace === null && oneWeek.etaDate === null, oneWeek);
const gaining = goalStatus({ ...kgDays("2026-10-13", "2026-10-19", 64), ...kgDays("2026-10-20", "2026-10-26", 65) }, goal, "2026-10-26");
check("gaining: pace is positive and there is no ETA", gaining.pace > 0 && gaining.etaDate === null, gaining);
const done = goalStatus({ ...kgDays("2026-10-13", "2026-10-19", 59.7), ...kgDays("2026-10-20", "2026-10-26", 59.5) }, goal, "2026-10-26");
check("goal reached: to go is negative and the ETA is today", done.toGo < 0 && done.etaDate === "2026-10-26" && done.etaVsTarget < 0, done);
check("days left never goes negative after the target date", goalStatus(kgDays("2026-12-10", "2026-12-20", 60), goal, "2026-12-20").daysLeft === 0);
check("before the plan starts, the plan is the start weight", goalStatus(kgDays("2026-10-14", "2026-10-20", 64), goal, "2026-10-20").planToday === 64);

// ---- the owner's MyFitnessPal streak used as a baseline ---------------------------------------------------------------
console.log("loggingStreak with the MyFitnessPal baseline");
const base568 = { days: 568, through: "2026-10-26" };
let bs = loggingStreak(logDays("2026-09-01", "2026-10-26"), "2026-10-27", base568);
check("568 days through 26 Oct, today (27th) not logged yet -> 568, from the app", bs.current === 568 && bs.fromApp === true, bs);
check("it started 567 days before the through day (7 Apr 2025)", bs.start === "2025-04-07", bs.start);
bs = loggingStreak(logDays("2026-09-01", "2026-10-27"), "2026-10-27", base568);
check("today logged -> 569", bs.current === 569 && bs.fromApp === true, bs);
bs = loggingStreak(logDays("2026-09-01", "2026-10-30"), "2026-10-30", base568);
check("four more days logged -> 572", bs.current === 572, bs);
bs = loggingStreak({ ...logDays("2026-09-01", "2026-10-26"), ...logDays("2026-10-28", "2026-10-29") }, "2026-10-29", base568);
check("a missed day after the app's number: only our own new run counts (2), no baseline", bs.current === 2 && bs.fromApp === false && bs.start === "2026-10-28", bs);
bs = loggingStreak(logDays("2026-09-01", "2026-10-26"), "2026-10-29", base568);
check("two days missed in a row -> the streak is 0 (baseline does not revive it)", bs.current === 0 && bs.fromApp === false, bs);
bs = loggingStreak(logDays("2026-09-01", "2026-10-26"), "2026-10-27", { days: 568, through: "2026-08-15" });
check("a baseline that ends before our data starts does not apply (our own 56-day run)", bs.fromApp === false && bs.current === 56, bs);
bs = loggingStreak(logDays("2026-09-01", "2026-10-26"), "2026-10-27", { days: 30, through: "2026-10-26" });
check("a small baseline replaces our count with the app's (30), since the app is the truth", bs.current === 30 && bs.fromApp === true, bs);
bs = loggingStreak({ ...logDays("2026-09-01", "2026-09-20"), ...logDays("2026-09-22", "2026-10-26") }, "2026-10-27", base568);
check("a gap in our own data before the app's day is ignored: the app's number is trusted (568)", bs.fromApp === true && bs.current === 568, bs);
bs = loggingStreak(logDays("2026-09-01", "2026-10-26"), "2026-10-27", null);
check("without a baseline nothing changes (55-ish day own run, capped)", bs.fromApp === false && bs.current === 56 && bs.capped === true, bs);
check("best is never below the app's number", loggingStreak(logDays("2026-09-01", "2026-10-26"), "2026-10-27", base568).best >= 568);

console.log(`\n${passed} passed, ${failed.length} failed`);
if (failed.length) { console.log("FAILED:", failed); process.exit(1); }
