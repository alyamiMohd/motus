// Tests for the week-to-date averaging rule in site/shared.js (weeks start Sunday).
// Steps and calories stop at YESTERDAY (today is a partial day); sleep and weight include TODAY.
// Run from the repo root:  node tests/test_week_logic.mjs   (exit code 0 = all passed)
import { readFileSync } from "node:fs";

const code = readFileSync(new URL("../site/shared.js", import.meta.url), "utf8");
const { weekStart, add, weekAvg, loggingStreak } = new Function(code + "\nreturn { weekStart, add, weekAvg, loggingStreak };")();

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
check("no data at all -> zeros", JSON.stringify(loggingStreak({}, "2026-10-22")) === JSON.stringify({ current: 0, best: 0, start: null, capped: false }));
check("month boundary is handled (28 Sep -> 3 Oct = 6 days)", loggingStreak(logDays("2026-09-28", "2026-10-03"), "2026-10-03").current === 6);

console.log(`\n${passed} passed, ${failed.length} failed`);
if (failed.length) { console.log("FAILED:", failed); process.exit(1); }
