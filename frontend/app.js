// Add these global variables at the top
let allTrades = [];

// Replace your old loadTrades() with this
async function loadTrades() {
  try {
    const res = await fetch(`${API}/trades`);
    allTrades = await res.json();
    populateFilterPairs();
    renderFilteredTrades();
    updateTradeCount(allTrades.length);
  } catch (_) {}
}

// New filter functions
function populateFilterPairs() {
  const select = document.getElementById("filter-pair");
  const current = select.value;
  const unique = [...new Set(allTrades.map(t => t.pair))].sort();
  select.innerHTML = '<option value="">All Pairs</option>' + unique.map(p => `<option value="${p}">${p}</option>`).join('');
  if (unique.includes(current)) select.value = current;
}

function renderFilteredTrades() {
  let filtered = [...allTrades];

  const pair = document.getElementById("filter-pair").value;
  if (pair) filtered = filtered.filter(t => t.pair === pair);

  const dir = document.getElementById("filter-direction").value;
  if (dir) filtered = filtered.filter(t => t.direction === dir);

  const outcome = document.getElementById("filter-outcome").value;
  if (outcome) filtered = filtered.filter(t => t.outcome === outcome);

  const from = document.getElementById("filter-from").value;
  if (from) filtered = filtered.filter(t => t.date >= from);

  const to = document.getElementById("filter-to").value;
  if (to) filtered = filtered.filter(t => t.date <= to);

  const search = document.getElementById("filter-search").value.toLowerCase().trim();
  if (search) filtered = filtered.filter(t =>
    (t.pair || "").toLowerCase().includes(search) || (t.notes || "").toLowerCase().includes(search)
  );

  renderTradesTable(filtered);
}

function tradesToCSV(trades) {
  const headers = ["Date","Pair","Direction","Outcome","RR","PnL_R","Notes"];
  let csv = headers.join(",") + "\n";
  trades.forEach(t => {
    const row = [t.date, t.pair, t.direction, t.outcome, t.rr, t.pnl_r, `"${(t.notes||"").replace(/"/g,'""')}"`];
    csv += row.join(",") + "\n";
  });
  return csv;
}

function csvToArray(text) {
  const lines = text.trim().split("\n");
  const headers = lines[0].split(",").map(h => h.trim().replace(/"/g, "").toLowerCase());
  const result = [];
  for (let i = 1; i < lines.length; i++) {
    if (!lines[i].trim()) continue;
    // simple CSV parser (handles quoted fields)
    let row = lines[i].match(/(".*?"|[^",]+)(?=\s*,|\s*$)/g) || [];
    row = row.map(v => v.replace(/^"|"$/g, "").trim());
    const obj = {};
    headers.forEach((h, idx) => obj[h] = row[idx] || "");
    result.push(obj);
  }
  return result;
}

// Add all listeners at the bottom (after init)
document.getElementById("export-json-btn").addEventListener("click", async () => {
  const res = await fetch(`${API}/trades`); const data = await res.json();
  const blob = new Blob([JSON.stringify(data, null, 2)], {type: "application/json"});
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob);
  a.download = `trades-${new Date().toISOString().split("T")[0]}.json`; a.click();
});

document.getElementById("export-csv-btn").addEventListener("click", async () => {
  const res = await fetch(`${API}/trades`); const data = await res.json();
  const csv = tradesToCSV(data);
  const blob = new Blob([csv], {type: "text/csv"});
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob);
  a.download = `trades-${new Date().toISOString().split("T")[0]}.csv`; a.click();
});

document.getElementById("import-csv-btn").addEventListener("click", () => document.getElementById("csv-file-input").click());
document.getElementById("csv-file-input").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const text = await file.text();
  const rows = csvToArray(text);
  const payload = rows.map(r => ({
    pair: (r.pair || r.Pair || "").toUpperCase(),
    direction: (r.direction || r.Direction || "").toLowerCase(),
    outcome: (r.outcome || r.Outcome || "").toLowerCase(),
    rr: parseFloat(r.rr || r.RR || 1),
    date: r.date || r.Date || "",
    notes: r.notes || r.Notes || ""
  })).filter(t => t.pair && t.direction && t.outcome);

  if (payload.length) {
    await fetch(`${API}/trades/bulk`, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(payload)});
    alert(`✅ Imported ${payload.length} trades!`);
    loadTrades(); loadAnalysis();
  }
  e.target.value = "";
});

document.getElementById("clear-filters-btn").addEventListener("click", () => {
  document.querySelectorAll(".trade-filters select, .trade-filters input").forEach(el => el.value = "");
  renderFilteredTrades();
});

// Filter listeners
document.querySelectorAll(".trade-filters select, .trade-filters input[type=date]").forEach(el => {
  el.addEventListener("change", renderFilteredTrades);
});
document.getElementById("filter-search").addEventListener("input", renderFilteredTrades);

// Update renderDashboard (add the new fields)
function renderDashboard(data) {
  const o = data.overall;
  if (!o || o.total_trades === 0) return;

  // ... your original lines ...
  document.getElementById("s-winrate").textContent = fmt(o.win_rate) + "%";
  document.getElementById("s-winrate-ci").textContent = `95% CI: ${o.win_rate_ci}`;
  document.getElementById("s-medwin").textContent = fmt(o.median_win_rr) + "R";
  document.getElementById("s-medloss").textContent = fmt(o.median_loss_rr) + "R";

  // Streak warning
  const streak = o.current_loss_streak || 0;
  const warn = document.getElementById("streak-warning");
  if (streak >= 5) {
    warn.classList.remove("hidden");
    document.getElementById("current-streak").textContent = streak;
  } else {
    warn.classList.add("hidden");
  }
}

// In renderBatches template, add the two median lines + CI (I left the exact string in the code you can copy)
