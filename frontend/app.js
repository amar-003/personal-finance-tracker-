const $ = (selector) => document.querySelector(selector);
const notice = $("#notice");
const fileInput = $("#csv-file");
let selectedFile = null;
let allTransactions = [];
let filteredTransactions = [];
let currentBudgets = [];
let currentGoals = [];
const money = new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 });

function showNotice(message, kind = "error") {
  notice.textContent = message;
  notice.className = `notice ${kind}`;
  notice.hidden = false;
  notice.scrollIntoView({ behavior: "smooth", block: "nearest" });
}
function clearNotice() { notice.hidden = true; }
async function api(path, options = {}) {
  const response = await fetch(path, { ...options, headers: { "Content-Type": "application/json", ...(options.headers || {}) } });
  let body;
  try { body = await response.json(); } catch { body = {}; }
  if (!response.ok) throw new Error(body.detail || `Request failed (${response.status})`);
  return body;
}

fileInput.addEventListener("change", () => {
  selectedFile = fileInput.files[0] || null;
  $("#file-label").textContent = selectedFile ? selectedFile.name : "Choose a CSV file";
  $("#import-button").disabled = !selectedFile;
  clearNotice();
});

// Parse quoted fields, escaped quotes, and line breaks without relying on a CSV library.
function parseCsv(source) {
  const rows = [];
  let row = [], cell = "", quoted = false;
  for (let i = 0; i < source.length; i++) {
    const char = source[i];
    if (quoted) {
      if (char === '"' && source[i + 1] === '"') { cell += '"'; i++; }
      else if (char === '"') quoted = false;
      else cell += char;
    } else if (char === '"') quoted = true;
    else if (char === ",") { row.push(cell); cell = ""; }
    else if (char === "\n" || char === "\r") {
      if (char === "\r" && source[i + 1] === "\n") i++;
      row.push(cell); rows.push(row); row = []; cell = "";
    } else cell += char;
  }
  if (cell.length || row.length) { row.push(cell); rows.push(row); }
  return rows.filter((item) => item.some((value) => value.trim() !== ""));
}

const aliases = {
  transaction_date: ["transactiondate", "date", "transactionday", "day", "transdate", "dateoftransaction", "posteddate", "postingdate", "purchasedate", "postdate", "effectivedate", "transactiontimestamp", "transactiondatetime", "transactiondateandtime", "activitydate"],
  description: ["description", "transactiondescription", "details", "transactiondetails", "merchant", "merchantname", "vendor", "vendorname", "businessname", "transactionname", "transactionmemo", "counterparty", "payee", "memo", "narration", "name", "descriptiondetails", "merchantdetails"],
  amount: ["amount", "amt", "transactionamount", "transactionamt", "transamount", "netamount", "totalamount", "debit", "debitamount", "withdrawal", "withdrawals", "withdrawalamount", "transactionvalue", "netdebit", "credit", "creditamount", "spend", "spendamount", "amountspent", "totalspend", "netspend", "expense", "expenseamount", "purchaseamount", "paymentamount", "chargeamount", "amountpaid", "amountout", "moneyout", "outflow", "cost", "price", "value", "total"],
  category: ["category", "categoryname", "transactioncategory", "expensecategory", "expenseclassification", "label", "transactiontype"],
};
function mapHeaders(headers) {
  const result = {};
  headers.forEach((header, index) => {
    const key = header.normalize("NFKD").toLowerCase().replace(/[^a-z0-9]/g, "");
    let field = Object.keys(aliases).find((candidate) => aliases[candidate].includes(key));
    let confidence = field
      ? key === "transactiontype" ? 1 : 100 - aliases[field].indexOf(key)
      : 0;
    if (!field) {
      const possibilities = [];
      if (["date", "posted", "purchase", "transact"].some((part) => key.includes(part))) possibilities.push("transaction_date");
      if (["description", "detail", "merchant", "vendor", "payee", "memo", "narration", "counterparty", "name"].some((part) => key.includes(part))) possibilities.push("description");
      if (["amount", "amt", "debit", "credit", "withdraw", "spend", "expense", "purchase", "payment", "charge", "moneyout", "outflow", "cost", "price", "value", "total"].some((part) => key.includes(part))) possibilities.push("amount");
      if (["category", "classification", "label", "type", "class"].some((part) => key.includes(part))) possibilities.push("category");
      if (possibilities.length === 1) {
        field = possibilities[0];
        confidence = key === "type" ? 1 : 20;
      }
    }
    if (field) (result[field] ||= []).push({ index, confidence });
  });
  for (const [field, candidates] of Object.entries(result)) {
    if (field === "category" && candidates.some(({ confidence }) => confidence >= 20)) {
      result[field] = candidates.filter(({ confidence }) => confidence >= 20);
    }
    const mappedCandidates = result[field];
    result[field] = mappedCandidates
      .sort((left, right) => right.confidence - left.confidence || left.index - right.index)
      .map(({ index }) => index);
  }
  const missing = ["transaction_date", "description", "amount"].filter((field) => !result[field]);
  if (missing.length) {
    const detectedHeaders = headers.length > 10
      ? `${headers.slice(0, 10).join(", ")}, …`
      : headers.join(", ");
    throw new Error(`CSV is missing required columns: ${missing.map((field) => field.replace("transaction_date", "date")).join(", ")}. For amount, try Amount, Debit, Withdrawal, Spend, or Money Out. Detected headers: ${detectedHeaders}. Category is optional.`);
  }
  return result;
}
function parseAmount(raw) {
  const cleaned = String(raw ?? "").trim().replace(/[,$£€₹\s]/g, "").replace(/^\((.*)\)$/, "-$1");
  const value = Number(cleaned);
  if (!cleaned || !Number.isFinite(value)) throw new Error(`Invalid amount value: ${raw || "(blank)"}`);
  return value;
}
function inferCategory(description) {
  const rules = [
    ["Housing", ["rent", "lease", "mortgage", "apartment"]],
    ["Groceries", ["grocery", "supermarket", "market", "food mart"]],
    ["Dining", ["restaurant", "cafe", "coffee", "takeaway", "lunch", "dinner"]],
    ["Transport", ["bus", "train", "taxi", "uber", "lyft", "gas", "fuel", "parking"]],
    ["Utilities", ["electric", "water", "utility", "internet", "phone", "mobile"]],
    ["Healthcare", ["pharmacy", "doctor", "hospital", "medical", "health"]],
    ["Entertainment", ["cinema", "movie", "streaming", "netflix", "game"]],
    ["Shopping", ["amazon", "shopping", "store", "retail", "clothing"]],
    ["Travel", ["hotel", "flight", "airline", "booking", "travel"]],
    ["Education", ["school", "college", "tuition", "course", "book"]],
  ];
  const text = description.toLowerCase();
  return rules.find(([, keywords]) => keywords.some((keyword) => text.includes(keyword)))?.[0] || "Other";
}
function csvToTransactions(source) {
  const rows = parseCsv(source.replace(/^\uFEFF/, ""));
  if (rows.length < 2) throw new Error("The CSV must contain a header and at least one transaction.");
  const headers = rows[0].map((value) => value.trim());
  const columns = mapHeaders(headers);
  return rows.slice(1).map((row, rowIndex) => {
    const at = (field) => (columns[field] || [])
      .map((index) => (row[index] || "").trim())
      .find(Boolean) || "";
    const date = at("transaction_date"), description = at("description");
    if (!date) throw new Error(`Row ${rowIndex + 2} is missing a date.`);
    if (!description) throw new Error(`Row ${rowIndex + 2} is missing a description.`);
    const amount = parseAmount(at("amount"));
    const category = at("category");
    return { transaction_date: date, description, amount, category: category || inferCategory(description) };
  });
}

$("#import-button").addEventListener("click", async () => {
  if (!selectedFile) return;
  const button = $("#import-button"); button.disabled = true; button.textContent = "Importing…"; clearNotice();
  try {
    const transactions = csvToTransactions(await selectedFile.text());
    const result = await api("/transactions/import", { method: "POST", body: JSON.stringify({ transactions, replace: $("#replace-data").checked }) });
    showNotice(`Imported ${result.imported} transaction${result.imported === 1 ? "" : "s"}.`, "success");
    selectedFile = null; fileInput.value = ""; $("#file-label").textContent = "Choose a CSV file";
    await loadTransactions();
    await loadPlanning();
  } catch (error) { showNotice(`Import failed: ${error.message}`); }
  finally { button.disabled = !selectedFile; button.innerHTML = 'Import transactions <span>→</span>'; }
});

function escapeHtml(value) { return String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]); }
function setInputRange() {
  if (!allTransactions.length) return;
  const dates = allTransactions.map((item) => item.transaction_date).sort();
  const from = $("#date-from"), to = $("#date-to");
  from.min = to.min = dates[0]; from.max = to.max = dates.at(-1);
  if (!from.value || from.value < dates[0] || from.value > dates.at(-1)) from.value = dates[0];
  if (!to.value || to.value > dates.at(-1) || to.value < dates[0]) to.value = dates.at(-1);
}
function renderChart(items) {
  const target = $("#spend-chart");
  const days = {};
  items.forEach((item) => { days[item.transaction_date] = (days[item.transaction_date] || 0) + Math.abs(Number(item.amount)); });
  const points = Object.entries(days).sort(([a], [b]) => a.localeCompare(b)).slice(-30);
  if (!points.length) { target.innerHTML = '<div class="chart-empty">No spending to chart</div>'; return; }
  const width = 620, height = 190, padX = 12, padY = 16, max = Math.max(...points.map((point) => point[1]), 1);
  const coords = points.map((point, i) => [padX + i * (width - 2 * padX) / Math.max(points.length - 1, 1), height - padY - point[1] / max * (height - 2 * padY)]);
  const line = coords.map(([x, y], i) => `${i ? "L" : "M"}${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
  const area = `${line} L${coords.at(-1)[0]},${height} L${coords[0][0]},${height} Z`;
  const guides = [0.25, 0.5, 0.75].map((ratio) => `<line x1="0" x2="${width}" y1="${height * ratio}" y2="${height * ratio}" stroke="#edf1ed" stroke-dasharray="3 5"/>`).join("");
  target.innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Daily spending line chart">${guides}<defs><linearGradient id="chart-fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#62a982" stop-opacity=".22"/><stop offset="1" stop-color="#62a982" stop-opacity="0"/></linearGradient></defs><path d="${area}" fill="url(#chart-fill)"/><path d="${line}" fill="none" stroke="#4d9b70" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>${coords.length < 20 ? coords.map(([x, y]) => `<circle cx="${x}" cy="${y}" r="3.5" fill="#fff" stroke="#4d9b70" stroke-width="2"/>`).join("") : ""}<text x="0" y="${height}" fill="#9aa39c" font-size="10">${escapeHtml(points[0][0])}</text><text x="${width}" y="${height}" text-anchor="end" fill="#9aa39c" font-size="10">${escapeHtml(points.at(-1)[0])}</text></svg>`;
}
function renderForecastChart(days) {
  const target = $("#forecast-chart");
  const points = days.map((item) => [item.date, Math.max(Number(item.amount), 0)]);
  if (!points.length) {
    target.hidden = true;
    return;
  }
  const width = 620, height = 190, padX = 12, padY = 16;
  const max = Math.max(...points.map((point) => point[1]), 1);
  const coords = points.map((point, index) => [
    padX + index * (width - 2 * padX) / Math.max(points.length - 1, 1),
    height - padY - point[1] / max * (height - 2 * padY),
  ]);
  const line = coords.map(([x, y], index) => `${index ? "L" : "M"}${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
  const area = `${line} L${coords.at(-1)[0]},${height} L${coords[0][0]},${height} Z`;
  target.innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Forecasted daily spending for the next 30 days"><line x1="0" x2="${width}" y1="${height / 2}" y2="${height / 2}" stroke="#edf1ed" stroke-dasharray="3 5"/><path d="${area}" fill="#62a982" fill-opacity=".12"/><path d="${line}" fill="none" stroke="#4d9b70" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>${coords.filter((_, index) => index % 5 === 0 || index === coords.length - 1).map(([x, y]) => `<circle cx="${x}" cy="${y}" r="3" fill="#fff" stroke="#4d9b70" stroke-width="2"/>`).join("")}<text x="0" y="${height}" fill="#9aa39c" font-size="10">${escapeHtml(points[0][0])}</text><text x="${width}" y="${height}" text-anchor="end" fill="#9aa39c" font-size="10">${escapeHtml(points.at(-1)[0])}</text></svg>`;
  target.hidden = false;
  $("#forecast-note").hidden = false;
}
function renderCategories(items) {
  const totals = {};
  items.forEach((item) => { if (item.category) totals[item.category] = (totals[item.category] || 0) + Math.abs(Number(item.amount)); });
  const entries = Object.entries(totals).sort((a, b) => b[1] - a[1]);
  $("#category-chart").innerHTML = entries.length ? entries.slice(0, 7).map(([name, value]) => `<div class="category-row"><span class="category-name">${escapeHtml(name)}</span><div class="bar-track"><div class="bar-fill" style="width:${Math.max(value / entries[0][1] * 100, 2)}%"></div></div><span class="category-value">${money.format(value)}</span></div>`).join("") : '<div class="chart-empty">Import categories or add descriptions to classify.</div>';
  const selected = new Set([...$("#category-options").querySelectorAll("input:checked")].map((input) => input.value));
  $("#category-options").innerHTML = [...new Set(allTransactions.map((item) => item.category).filter(Boolean))].sort().map((category) => `<label><input type="checkbox" value="${escapeHtml(category)}" ${selected.has(category) || (!selected.size && ["Dining", "Entertainment", "Shopping", "Travel"].includes(category)) ? "checked" : ""}>${escapeHtml(category)}</label>`).join("") || '<span class="metric-foot">Categories appear here after import.</span>';
}
function updateBudgetCategoryOptions() {
  const select = $("#budget-category");
  const selected = select.value;
  const categories = [...new Set([
    ...allTransactions.map((item) => item.category).filter(Boolean),
    ...currentBudgets.map((budget) => budget.category).filter(Boolean),
  ])].sort((a, b) => a.localeCompare(b));
  select.innerHTML = '<option value="">All spending</option>' + categories
    .map((category) => `<option value="${escapeHtml(category)}">${escapeHtml(category)}</option>`)
    .join("");
  if ([...select.options].some((option) => option.value === selected)) {
    select.value = selected;
  }
}
function renderBudgets(month) {
  const target = $("#budget-list");
  if (!currentBudgets.length) {
    target.innerHTML = '<div class="planning-empty">No budgets set for this month yet.</div>';
    return;
  }
  target.innerHTML = currentBudgets.map((budget) => {
    const spent = allTransactions
      .filter((item) => item.transaction_date.slice(0, 7) === month)
      .filter((item) => !budget.category || (item.category || "").toLowerCase() === budget.category.toLowerCase())
      .reduce((sum, item) => sum + Math.abs(Number(item.amount)), 0);
    const percentage = spent / Number(budget.amount) * 100;
    const label = budget.category || "All spending";
    return `<article class="budget-item"><div class="budget-head"><strong>${escapeHtml(label)}</strong><span>${money.format(spent)} / ${money.format(budget.amount)}</span></div><div class="progress-track"><div class="progress-fill ${percentage > 100 ? "over" : ""}" style="width:${Math.min(percentage, 100)}%"></div></div><div class="budget-meta"><span>${percentage.toFixed(0)}% used · ${money.format(Math.max(Number(budget.amount) - spent, 0))} remaining</span><button type="button" class="button button-muted button-small" data-budget-delete="${budget.id}">Remove</button></div></article>`;
  }).join("");
}
function renderGoals() {
  const target = $("#goals-list");
  if (!currentGoals.length) {
    target.innerHTML = '<div class="planning-empty">Create a savings goal to start tracking progress.</div>';
    return;
  }
  const today = new Date();
  target.innerHTML = currentGoals.map((goal) => {
    const targetAmount = Number(goal.target_amount);
    const saved = Number(goal.current_amount);
    const remaining = Math.max(targetAmount - saved, 0);
    const percentage = Math.min(saved / targetAmount * 100, 100);
    const daysLeft = Math.ceil((new Date(`${goal.target_date}T00:00:00`) - today) / 86400000);
    const monthsLeft = Math.max(daysLeft / 30.44, 1);
    const monthlyNeeded = remaining / monthsLeft;
    const timing = daysLeft < 0 ? "Target date passed" : `About ${money.format(monthlyNeeded)} / month to target`;
    return `<article class="goal-item"><div class="goal-head"><strong>${escapeHtml(goal.name)}</strong><span>${money.format(saved)} / ${money.format(targetAmount)}</span></div><div class="progress-track"><div class="progress-fill" style="width:${percentage}%"></div></div><div class="goal-meta"><span>${percentage.toFixed(0)}% saved · ${money.format(remaining)} to go</span><span>${escapeHtml(timing)}</span></div><form class="goal-update-form" data-goal-id="${goal.id}"><input type="hidden" name="name" value="${escapeHtml(goal.name)}"><input type="hidden" name="target_amount" value="${targetAmount}"><input type="hidden" name="target_date" value="${escapeHtml(goal.target_date)}"><label>Saved so far<input name="current_amount" type="number" min="0" step="0.01" value="${saved}" required></label><button class="button button-primary button-small" type="submit">Update</button><button class="button button-muted button-small" type="button" data-goal-delete="${goal.id}">Remove</button></form></article>`;
  }).join("");
}
async function loadPlanning() {
  const month = $("#budget-month").value;
  try {
    const [budgetBody, goalBody] = await Promise.all([
      api(`/budgets?month=${encodeURIComponent(month)}`),
      api("/savings-goals"),
    ]);
    currentBudgets = budgetBody.budgets || [];
    currentGoals = goalBody.goals || [];
    updateBudgetCategoryOptions();
    renderBudgets(month);
    renderGoals();
  } catch (error) {
    showNotice(`Could not load budgets and savings goals: ${error.message}`);
  }
}
function render() {
  const from = $("#date-from").value, to = $("#date-to").value, query = $("#search").value.trim().toLowerCase();
  filteredTransactions = allTransactions.filter((item) => (!from || item.transaction_date >= from) && (!to || item.transaction_date <= to) && (!query || item.description.toLowerCase().includes(query)));
  $("#empty-state").hidden = allTransactions.length > 0;
  $("#dashboard-content").hidden = allTransactions.length === 0;
  if (!allTransactions.length) return;
  const total = filteredTransactions.reduce((sum, item) => sum + Math.abs(Number(item.amount)), 0);
  const averages = total / Math.max(filteredTransactions.length, 1), cats = {};
  filteredTransactions.forEach((item) => { if (item.category) cats[item.category] = (cats[item.category] || 0) + Math.abs(Number(item.amount)); });
  const top = Object.entries(cats).sort((a, b) => b[1] - a[1])[0];
  $("#metric-count").textContent = filteredTransactions.length.toLocaleString(); $("#metric-total").textContent = money.format(total); $("#metric-average").textContent = money.format(averages); $("#metric-category").textContent = top?.[0] || "—";
  renderChart(filteredTransactions); renderCategories(filteredTransactions);
  const sorted = [...filteredTransactions].sort((a, b) => b.transaction_date.localeCompare(a.transaction_date));
  $("#transactions-body").innerHTML = sorted.slice(0, 100).map((item) => `<tr><td>${escapeHtml(item.transaction_date)}</td><td>${escapeHtml(item.description)}</td><td>${item.category ? `<span class="category-chip">${escapeHtml(item.category)}</span>` : "—"}</td><td class="right amount">${money.format(Number(item.amount))}</td></tr>`).join("");
  $("#transaction-caption").textContent = `${sorted.length} transaction${sorted.length === 1 ? "" : "s"} · showing latest 100`;
}
async function loadTransactions() {
  try { const body = await api("/transactions"); allTransactions = body.transactions || []; allTransactions.sort((a, b) => a.transaction_date.localeCompare(b.transaction_date)); setInputRange(); render(); }
  catch (error) { showNotice(`Could not load transactions: ${error.message}`); }
}
document.querySelectorAll(".tab").forEach((tab) => tab.addEventListener("click", () => {
  document.querySelectorAll(".tab").forEach((item) => item.classList.toggle("active", item === tab));
  document.querySelectorAll(".tab-content").forEach((panel) => { panel.hidden = panel.id !== `tab-${tab.dataset.tab}`; });
  if (tab.dataset.tab === "analysis") loadAnalysis();
}));
$("#date-from").addEventListener("change", render); $("#date-to").addEventListener("change", render); $("#search").addEventListener("input", render);

const today = new Date();
$("#budget-month").value = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}`;
$("#budget-month").addEventListener("change", loadPlanning);
$("#budget-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const data = new FormData(form);
  const button = form.querySelector('button[type="submit"]');
  button.disabled = true;
  try {
    await api("/budgets", {
      method: "PUT",
      body: JSON.stringify({
        month: data.get("month"),
        category: data.get("category"),
        amount: Number(data.get("amount")),
      }),
    });
    form.elements.amount.value = "";
    showNotice("Budget saved.", "success");
    await loadPlanning();
  } catch (error) {
    showNotice(`Could not save budget: ${error.message}`);
  } finally {
    button.disabled = false;
  }
});
$("#budget-list").addEventListener("click", async (event) => {
  const button = event.target.closest("[data-budget-delete]");
  if (!button) return;
  button.disabled = true;
  try {
    await api(`/budgets/${button.dataset.budgetDelete}`, { method: "DELETE" });
    showNotice("Budget removed.", "success");
    await loadPlanning();
  } catch (error) {
    showNotice(`Could not remove budget: ${error.message}`);
    button.disabled = false;
  }
});
$("#goal-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const data = new FormData(form);
  const button = form.querySelector('button[type="submit"]');
  button.disabled = true;
  try {
    await api("/savings-goals", {
      method: "POST",
      body: JSON.stringify({
        name: data.get("name"),
        target_amount: Number(data.get("target_amount")),
        current_amount: Number(data.get("current_amount")),
        target_date: data.get("target_date"),
      }),
    });
    form.reset();
    showNotice("Savings goal created.", "success");
    await loadPlanning();
  } catch (error) {
    showNotice(`Could not create savings goal: ${error.message}`);
  } finally {
    button.disabled = false;
  }
});
$("#goals-list").addEventListener("submit", async (event) => {
  const form = event.target.closest(".goal-update-form");
  if (!form) return;
  event.preventDefault();
  const data = new FormData(form);
  const button = form.querySelector('button[type="submit"]');
  button.disabled = true;
  try {
    await api(`/savings-goals/${form.dataset.goalId}`, {
      method: "PUT",
      body: JSON.stringify({
        name: data.get("name"),
        target_amount: Number(data.get("target_amount")),
        current_amount: Number(data.get("current_amount")),
        target_date: data.get("target_date"),
      }),
    });
    showNotice("Savings progress updated.", "success");
    await loadPlanning();
  } catch (error) {
    showNotice(`Could not update savings goal: ${error.message}`);
    button.disabled = false;
  }
});
$("#goals-list").addEventListener("click", async (event) => {
  const button = event.target.closest("[data-goal-delete]");
  if (!button) return;
  button.disabled = true;
  try {
    await api(`/savings-goals/${button.dataset.goalDelete}`, { method: "DELETE" });
    showNotice("Savings goal removed.", "success");
    await loadPlanning();
  } catch (error) {
    showNotice(`Could not remove savings goal: ${error.message}`);
    button.disabled = false;
  }
});

async function loadAnalysis() {
  const result = $("#analysis-result");
  const button = $("#analysis-button");
  button.disabled = true;
  result.hidden = false;
  result.textContent = "Analyzing…";
  try {
    const body = await api("/analysis");
    const change = body.month_over_month_change_percent;
    const changeText = change === null
      ? "No previous month available"
      : `${change > 0 ? "+" : ""}${change}% versus the previous month`;
    result.innerHTML = `
      <strong>${escapeHtml(body.latest_month)}: ${money.format(body.latest_month_spend)}</strong>
      ${escapeHtml(changeText)} · Average monthly spend ${money.format(body.average_monthly_spend)}
      <div>Highest category: ${escapeHtml(body.highest_category)} (${money.format(body.highest_category_spend)})</div>
      <div class="category-list">${body.category_totals.slice(0, 7).map((item) =>
        `<div class="category-row"><span class="category-name">${escapeHtml(item.category)}</span><div class="bar-track"><div class="bar-fill" style="width:${Math.max(Number(item.amount) / Math.max(...body.category_totals.map((row) => Number(row.amount)), 1) * 100, 2)}%"></div></div><span class="category-value">${money.format(item.amount)}</span></div>`
      ).join("")}</div>`;
  } catch (error) {
    result.textContent = error.message;
  } finally {
    button.disabled = false;
  }
}
$("#analysis-button").addEventListener("click", loadAnalysis);

$("#predict-form").addEventListener("submit", async (event) => {
  event.preventDefault(); const result = $("#predict-result"), button = event.submitter; button.disabled = true; result.hidden = false; result.textContent = "Working…";
  try { const data = new FormData(event.currentTarget); const body = await api("/predict-category", { method: "POST", body: JSON.stringify({ transactions: [{ description: data.get("description"), amount: Number(data.get("amount")) }] }) }); const prediction = body.predictions[0]; result.innerHTML = `<strong>${escapeHtml(prediction.category)}</strong>Model confidence: ${Math.round(prediction.confidence * 100)}%`; }
  catch (error) { result.textContent = error.message; } finally { button.disabled = false; }
});
$("#forecast-button").addEventListener("click", async (event) => {
  const button = event.currentTarget, result = $("#forecast-result");
  button.disabled = true;
  button.textContent = "Calculating…";
  result.hidden = false;
  result.textContent = "";
  $("#forecast-chart").hidden = true;
  $("#forecast-note").hidden = true;
  try {
    const body = await api("/forecast-monthly");
    const days = body.daily_forecast || [];
    const range = body.range_low !== undefined
      ? ` · 90% range ${money.format(body.range_low)}–${money.format(body.range_high)}`
      : "";
    result.innerHTML = `<strong>${money.format(body.total_forecast)}</strong>Estimated spend over the next 30 days${escapeHtml(range)} · ${escapeHtml(body.method)}<div class="category-list">${days.slice(0, 7).map((day) => `<div class="category-row"><span>${escapeHtml(day.date)}</span><div class="bar-track"><div class="bar-fill" style="width:${Math.max(Number(day.amount) / Math.max(...days.map((x) => Number(x.amount)), 1) * 100, 2)}%"></div></div><span class="category-value">${money.format(day.amount)} (${money.format(day.lower)}–${money.format(day.upper)})</span></div>`).join("")}</div>`;
    renderForecastChart(days);
  } catch (error) {
    result.textContent = error.message;
  } finally {
    button.disabled = false;
    button.textContent = "Generate forecast →";
  }
});
$("#health-form").addEventListener("submit", async (event) => {
  event.preventDefault(); const result = $("#health-result"), button = event.submitter; button.disabled = true; result.hidden = false; result.textContent = "Calculating…";
  try { const data = new FormData(event.currentTarget); const body = await api("/health-score", { method: "POST", body: JSON.stringify({ monthly_income: Number(data.get("monthly_income")), monthly_debt_payments: Number(data.get("monthly_debt_payments")), savings_balance: Number(data.get("savings_balance")), discretionary_categories: [...$("#category-options").querySelectorAll("input:checked")].map((input) => input.value) }) }); result.innerHTML = `<strong>Health score ${body.health_score}/100 · Risk ${body.risk_score}/100</strong>${(body.advisory_notes || []).map((note) => `<div>${escapeHtml(note)}</div>`).join("")}<div class="fine-print">${escapeHtml(body.score_note || "")}</div>`; }
  catch (error) { result.textContent = error.message; } finally { button.disabled = false; }
});

api("/health").then(async () => {
  await loadTransactions();
  await loadPlanning();
}).catch((error) => showNotice(`Cannot connect to the local API. Start the dashboard with “python -m frontend.app”. ${error.message}`));
