const $ = (id) => document.getElementById(id);

async function loadMeta() {
  const meta = await fetch("/api/meta").then((r) => r.json());
  for (const [key, info] of Object.entries(meta.sites)) {
    const o = document.createElement("option");
    o.value = key;
    o.textContent = info.name + (info.kind === "review" ? " (导购)" : "");
    $("site").appendChild(o);
  }
  for (const [key, label] of Object.entries(meta.categories)) {
    const o = document.createElement("option");
    o.value = key;
    o.textContent = label;
    $("category").appendChild(o);
  }
}

function fmtPrice(v) {
  return v == null ? "—" : "$" + Number(v).toFixed(2);
}

async function loadProducts() {
  const params = new URLSearchParams();
  if ($("site").value) params.set("site", $("site").value);
  if ($("category").value) params.set("category", $("category").value);
  if (+$("minDiscount").value) params.set("min_discount", $("minDiscount").value);

  const rows = await fetch("/api/products?" + params).then((r) => r.json());
  const tbody = $("results").querySelector("tbody");
  tbody.innerHTML = "";
  if (!rows.length) {
    tbody.innerHTML = '<tr><td colspan="8">暂无数据，点击「抓取最新」。</td></tr>';
    return;
  }
  for (const r of rows) {
    const tr = document.createElement("tr");
    const disc = r.discount_pct ? r.discount_pct + "%" : "—";
    tr.innerHTML =
      `<td>${r.site}</td><td>${r.category}</td><td>${r.brand || "—"}</td>` +
      `<td><a href="${r.url}" target="_blank" rel="noopener">${r.name}</a></td>` +
      `<td>${fmtPrice(r.price)}</td><td>${fmtPrice(r.list_price)}</td>` +
      `<td>${disc}</td><td>${(r.captured_at || "").replace("T", " ")}</td>`;
    tbody.appendChild(tr);
  }
}

async function scrape() {
  $("status").textContent = "抓取中…";
  const params = new URLSearchParams();
  if ($("category").value) params.set("category", $("category").value);
  const res = await fetch("/api/scrape?" + params, { method: "POST" }).then((r) => r.json());
  $("status").textContent = `已保存 ${res.saved} 条`;
  await loadProducts();
}

$("refresh").onclick = loadProducts;
$("scrape").onclick = scrape;

loadMeta().then(loadProducts);
