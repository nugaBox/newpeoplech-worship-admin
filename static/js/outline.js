/** 목차 관리 */

let schema = null;
let currentFields = {};
let activeTab = "basic";

function setStatus(msg, isError = false) {
  const el = document.getElementById("outline-status");
  if (!el) return;
  el.textContent = msg;
  el.style.color = isError ? "var(--danger)" : "var(--muted)";
}

function fieldsForTab(tab) {
  if (!schema) return [];
  const groupMap = { basic: "기본 정보", day: "주일낮예배", praise: "주일찬양예배" };
  return schema.fields.filter((f) => f.group === groupMap[tab]);
}

function renderFields() {
  const container = document.getElementById("outline-fields-container");
  const fields = fieldsForTab(activeTab);
  container.innerHTML = `<div class="outline-fields-grid">${fields.map((f) => {
    const val = currentFields[f.field] || "";
    const isLong = (f.sample || "").length > 60 || val.length > 60;
    return `<div class="outline-field" data-field="${f.field}">
      <label>${f.field}</label>
      ${isLong
        ? `<textarea class="form-control form-control-sm" rows="3" data-field="${f.field}">${val}</textarea>`
        : `<input type="text" class="form-control form-control-sm" data-field="${f.field}" value="${val.replace(/"/g, "&quot;")}">`}
    </div>`;
  }).join("")}</div>`;
}

function collectFields() {
  document.querySelectorAll("#outline-fields-container [data-field]").forEach((el) => {
    currentFields[el.dataset.field] = el.value || "";
  });
}

async function loadSchema() {
  const res = await fetch("/api/outlines/schema");
  if (!res.ok) throw new Error("필드 정의를 불러오지 못했습니다.");
  schema = await res.json();
  schema.fields.forEach((f) => {
    if (!(f.field in currentFields)) currentFields[f.field] = "";
  });
  renderFields();
}

async function loadOutlineList() {
  const res = await fetch("/api/outlines");
  if (!res.ok) throw new Error("목차 목록을 불러오지 못했습니다.");
  const data = await res.json();
  const list = document.getElementById("outline-list");
  list.innerHTML = data.outlines.length
    ? data.outlines.map((o) => `
      <div class="outline-list-item" data-id="${o.id}">
        <div>
          <div>${o.title}</div>
          <div class="date">${o.date || o.updated_at.slice(0, 10)}</div>
        </div>
        <button type="button" class="icon-btn btn-del" data-del="${o.id}" title="삭제"><i class="fa-solid fa-trash-can"></i></button>
      </div>`).join("")
    : '<p class="small text-muted p-2">저장된 목차가 없습니다.</p>';

  list.querySelectorAll(".outline-list-item").forEach((item) => {
    item.addEventListener("click", (e) => {
      if (e.target.closest(".btn-del")) return;
      loadOutline(item.dataset.id);
    });
  });
  list.querySelectorAll(".btn-del").forEach((btn) => {
    btn.addEventListener("click", async (e) => {
      e.stopPropagation();
      if (!confirm("이 목차를 삭제할까요?")) return;
      await fetch(`/api/outlines/${btn.dataset.del}`, { method: "DELETE" });
      if (document.getElementById("outline-id").value === btn.dataset.del) newOutline();
      loadOutlineList();
    });
  });
}

async function loadOutline(id) {
  const res = await fetch(`/api/outlines/${id}`);
  if (!res.ok) throw new Error("목차를 불러오지 못했습니다.");
  const data = await res.json();
  document.getElementById("outline-id").value = data.id;
  document.getElementById("outline-form-title").textContent = data.title;
  currentFields = { ...data.fields };
  renderFields();
  document.querySelectorAll(".outline-list-item").forEach((el) => {
    el.classList.toggle("active", el.dataset.id === id);
  });
  setStatus(`"${data.title}" 불러옴`);
}

function newOutline() {
  document.getElementById("outline-id").value = "";
  document.getElementById("outline-form-title").textContent = "새 목차";
  if (schema) {
    schema.fields.forEach((f) => { currentFields[f.field] = ""; });
  }
  renderFields();
  document.querySelectorAll(".outline-list-item").forEach((el) => el.classList.remove("active"));
}

async function saveOutline() {
  collectFields();
  const id = document.getElementById("outline-id").value || null;
  const body = {
    id,
    title: currentFields.F_날짜 || "새 목차",
    date: currentFields.F_날짜 || "",
    fields: currentFields,
  };
  const res = await fetch("/api/outlines", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "저장 실패");
  document.getElementById("outline-id").value = data.id;
  document.getElementById("outline-form-title").textContent = data.title;
  setStatus(`저장됨: ${data.title}`);
  loadOutlineList();
}

document.querySelectorAll("#outline-tabs .nav-link").forEach((tab) => {
  tab.addEventListener("click", () => {
    collectFields();
    document.querySelectorAll("#outline-tabs .nav-link").forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    activeTab = tab.dataset.tab;
    renderFields();
  });
});

document.getElementById("outline-btn-new")?.addEventListener("click", newOutline);
document.getElementById("outline-btn-save")?.addEventListener("click", () => saveOutline().catch((e) => setStatus(e.message, true)));
document.getElementById("outline-btn-load-sample")?.addEventListener("click", () => {
  if (!schema) return;
  schema.fields.forEach((f) => {
    if (f.sample) currentFields[f.field] = f.sample;
  });
  renderFields();
  setStatus("샘플 값을 불러왔습니다.");
});

Promise.all([loadSchema(), loadOutlineList()]).catch((e) => setStatus(e.message, true));
