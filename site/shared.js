// Shared by every page: time helpers, standards (goals) and the navbar.
const TZ = "Asia/Riyadh";
const DEFAULTS = { steps: 8000, sleep: 7, weight: 0, workouts: 4 };   // weight 0 = any loss counts
let goals = { ...DEFAULTS };
try { Object.assign(goals, JSON.parse(localStorage.getItem("stotis-goals") || "{}")); } catch (e) {}
const saveGoals = () => { try { localStorage.setItem("stotis-goals", JSON.stringify(goals)); } catch (e) {} };

const today = new Date().toLocaleDateString("en-CA", { timeZone: TZ });
const add = (iso, n) => { const d = new Date(iso + "T00:00:00Z"); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
const label = iso => new Date(iso + "T00:00:00Z").toLocaleDateString("en-US", { weekday: "short", day: "numeric", timeZone: "UTC" });
const NO = '<span class="no">no data</span>';
const weekStart = iso => add(iso, -new Date(iso + "T00:00:00Z").getUTCDay());   // weeks start on Sunday

function loadJSON(path) {
  return fetch(path, { cache: "no-store" }).then(r => { if (!r.ok) throw 0; return r.json(); }).catch(() => null);
}

// Injects the navbar and wires the Standards panel. onChange runs whenever a goal changes.
function initNav(active, onChange) {
  document.body.insertAdjacentHTML("afterbegin", `
<nav>
  <div class="bar">
    <a href="./"><b>Stotis</b></a>
    <span class="links">
      <a href="./" class="${active === "home" ? "on" : ""}">Dashboard</a>
      <a href="workouts.html" class="${active === "workouts" ? "on" : ""}">Workouts</a>
      <button id="toggle" aria-expanded="false" aria-controls="standards">Standards</button>
    </span>
  </div>
  <div id="standards">
    <label>Steps per day <input id="s-steps" type="number" inputmode="numeric" min="0" step="500"></label>
    <label>Sleep hours per night <input id="s-sleep" type="number" inputmode="decimal" min="0" max="24" step="0.5"></label>
    <label>Weight loss kg per week <input id="s-weight" type="number" inputmode="decimal" min="0" step="0.1"></label>
    <label>Workouts per week <input id="s-workouts" type="number" inputmode="numeric" min="1" max="14" step="1"></label>
    <div class="row2"><small>Green when you reach it. Saved on this device.</small><button id="reset">Reset</button></div>
  </div>
</nav>`);
  const inputs = { steps: "s-steps", sleep: "s-sleep", weight: "s-weight", workouts: "s-workouts" };
  for (const [key, id] of Object.entries(inputs)) {
    const el = document.getElementById(id);
    el.value = goals[key];
    el.addEventListener("input", () => {
      const v = parseFloat(el.value);
      goals[key] = Number.isFinite(v) && v >= 0 ? v : DEFAULTS[key];
      saveGoals(); onChange();
    });
  }
  document.getElementById("reset").addEventListener("click", () => {
    goals = { ...DEFAULTS };
    for (const [key, id] of Object.entries(inputs)) document.getElementById(id).value = goals[key];
    saveGoals(); onChange();
  });
  const toggle = document.getElementById("toggle"), panel = document.getElementById("standards");
  toggle.addEventListener("click", () => {
    toggle.setAttribute("aria-expanded", panel.classList.toggle("open"));
  });
}
