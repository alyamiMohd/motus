// Shared by every page: time helpers, standards (goals) and the navbar.
const TZ = "Asia/Riyadh";
const DEFAULTS = { steps: 8000, sleep: 7, calories: 1500, weight: 0, workouts: 4, days: [1, 2, 3, 5, 6] };  // training days: 0=Sun ... 6=Sat   // weight 0 = any loss counts
let goals = { ...DEFAULTS, days: [...DEFAULTS.days] };
try { Object.assign(goals, JSON.parse(localStorage.getItem("stotis-goals") || "{}")); } catch (e) {}
if (!Array.isArray(goals.days)) goals.days = [...DEFAULTS.days];
const saveGoals = () => { try { localStorage.setItem("stotis-goals", JSON.stringify(goals)); } catch (e) {} };
try {   // one-time: devices that saved the old 2000 default move to 1500
  if (!localStorage.getItem("stotis-cal1500")) {
    if (goals.calories === 2000) goals.calories = 1500;
    localStorage.setItem("stotis-cal1500", "1");
    saveGoals();
  }
} catch (e) {}

const ADMIN_KEY = "motus-admin-token";   // session-only; set by edit.html after you sign in
const adminToken = () => { try { return sessionStorage.getItem(ADMIN_KEY) || ""; } catch (e) { return ""; } };

const today = new Date().toLocaleDateString("en-CA", { timeZone: TZ });
const add = (iso, n) => { const d = new Date(iso + "T00:00:00Z"); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
const label = iso => new Date(iso + "T00:00:00Z").toLocaleDateString("en-US", { weekday: "short", day: "numeric", timeZone: "UTC" });
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const dayMonth = iso => +iso.slice(8) + " " + MONTHS[+iso.slice(5, 7) - 1];      // "27 Sep"
const NO = '<span class="no">no data</span>';
const weekStart = iso => add(iso, -new Date(iso + "T00:00:00Z").getUTCDay());   // weeks start on Sunday

// Week-to-date average (weeks start on Sunday). Steps and calories stop at YESTERDAY because today is only a
// partial day (first steps / first meals); sleep and weight include TODAY (a night's sleep and a morning weigh-in are complete).
// Days without data are ignored; no data at all gives null (on a Sunday, steps/calories have nothing to average yet).
const AVG_THROUGH = { steps: "yesterday", calories: "yesterday", sleep_hours: "today", weight_kg: "today" };
function weekAvg(days, key, todayISO = today) {
  const from = weekStart(todayISO);
  const to = AVG_THROUGH[key] === "yesterday" ? add(todayISO, -1) : todayISO;
  const v = [];
  for (let d = from; d <= to; d = add(d, 1)) { const x = (days[d] || {})[key]; if (x != null) v.push(x); }
  return v.length ? v.reduce((a, b) => a + b) / v.length : null;
}

// Calorie-logging streak: consecutive days with calories recorded. Today does not break the streak until the day ends
// (if today is not logged yet the run is counted up to yesterday). best = the longest run in our data. capped = the current
// run reaches the first day we have data for, so the real streak (e.g. inside MyFitnessPal) may be longer than we can see.
function loggingStreak(days, todayISO = today) {
  const logged = d => ((days[d] || {}).calories != null);
  const dates = Object.keys(days).filter(logged).sort();
  if (!dates.length) return { current: 0, best: 0, start: null, capped: false };
  let best = 0, run = 0, prev = null;
  for (const d of dates) { run = prev && add(prev, 1) === d ? run + 1 : 1; best = Math.max(best, run); prev = d; }
  const end = logged(todayISO) ? todayISO : add(todayISO, -1);
  let current = 0;
  for (let d = end; logged(d); d = add(d, -1)) current++;
  const start = current ? add(end, -(current - 1)) : null;
  return { current, best, start, capped: current > 0 && start === dates[0] };
}

// The last `weeks` Sunday-Saturday weeks as a calendar (weeks*7 cells, oldest first): which days have calories recorded.
function streakGrid(days, todayISO = today, weeks = 4) {
  const start = add(weekStart(todayISO), -7 * (weeks - 1)), cells = [];
  for (let i = 0; i < weeks * 7; i++) {
    const d = add(start, i);
    cells.push({ date: d, logged: ((days[d] || {}).calories != null), today: d === todayISO, future: d > todayISO });
  }
  return cells;
}

// Workouts per Sunday-Saturday week for the last n weeks, oldest first (the current week is partial).
function weeklyWorkouts(days, todayISO = today, n = 12) {
  const first = add(weekStart(todayISO), -7 * (n - 1));
  return Array.from({ length: n }, (_, i) => {
    let c = 0;
    for (let k = 0; k < 7; k++) c += (days[add(first, 7 * i + k)] || {}).workout_count || 0;
    return c;
  });
}

function loadJSON(path) {
  return fetch(path, { cache: "no-store" }).then(r => { if (!r.ok) throw 0; return r.json(); }).catch(() => null);
}

// Injects the navbar and wires the Standards panel. onChange runs whenever a goal changes.
function initNav(active, onChange) {
  document.body.insertAdjacentHTML("afterbegin", `
<nav>
  <div class="bar">
    <a href="./"><b>Motus</b></a>
    <span class="links">
      <a href="./" class="${active === "home" ? "on" : ""}">Dashboard</a>
      <a href="workouts.html" class="${active === "workouts" ? "on" : ""}">Workouts</a>
      <a href="weeks.html" class="${active === "weeks" ? "on" : ""}">Weeks</a>
      <button id="toggle" aria-expanded="false" aria-controls="standards">Standards</button>
    </span>
  </div>
  <div id="standards">
    <label>Steps per day <input id="s-steps" type="number" inputmode="numeric" min="0" step="500"></label>
    <label>Sleep hours per night <input id="s-sleep" type="number" inputmode="decimal" min="0" max="24" step="0.5"></label>
    <label>Calories per day, less than <input id="s-calories" type="number" inputmode="numeric" min="0" step="50"></label>
    <label>Weight loss kg per week <input id="s-weight" type="number" inputmode="decimal" min="0" step="0.1"></label>
    <label>Workouts per week <input id="s-workouts" type="number" inputmode="numeric" min="1" max="14" step="1"></label>
    ${adminToken() ? '<div class="row2" style="margin:0 0 8px"><a href="edit.html" style="text-decoration:underline">Edit data →</a></div>' : ""}
    <div class="label2">Training days</div>
    <div class="chips" id="s-days"></div>
    <div class="row2"><small>Green when you reach it. Saved on this device.</small><button id="reset">Reset</button></div>
  </div>
</nav>`);
  const inputs = { steps: "s-steps", sleep: "s-sleep", calories: "s-calories", weight: "s-weight", workouts: "s-workouts" };
  for (const [key, id] of Object.entries(inputs)) {
    const el = document.getElementById(id);
    el.value = goals[key];
    el.addEventListener("input", () => {
      const v = parseFloat(el.value);
      goals[key] = Number.isFinite(v) && v >= 0 ? v : DEFAULTS[key];
      saveGoals(); onChange();
    });
  }
  const chips = document.getElementById("s-days");
  const drawChips = () => {
    chips.innerHTML = "SMTWTFS".split("").map((l, i) =>
      `<button type="button" data-d="${i}" aria-pressed="${goals.days.includes(i)}">${l}</button>`).join("");
  };
  drawChips();
  chips.addEventListener("click", e => {
    const b = e.target.closest("button"); if (!b) return;
    const d = +b.dataset.d;
    goals.days = goals.days.includes(d) ? goals.days.filter(x => x !== d) : [...goals.days, d].sort();
    saveGoals(); drawChips(); onChange();
  });
  document.getElementById("reset").addEventListener("click", () => {
    goals = { ...DEFAULTS, days: [...DEFAULTS.days] };
    drawChips();
    for (const [key, id] of Object.entries(inputs)) document.getElementById(id).value = goals[key];
    saveGoals(); onChange();
  });
  const toggle = document.getElementById("toggle"), panel = document.getElementById("standards");
  toggle.addEventListener("click", () => {
    toggle.setAttribute("aria-expanded", panel.classList.toggle("open"));
  });
}
