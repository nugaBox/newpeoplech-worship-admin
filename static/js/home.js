/** 홈 — 빠른 시작, 즐겨찾기 */

function setStatus(msg, isError = false) {
  const el = document.getElementById("home-status");
  if (!el) return;
  el.textContent = msg;
  el.style.color = isError ? "var(--danger)" : "var(--muted)";
}

async function runQuickStart(endpoint, inputId, emptyMessage) {
  const input = document.getElementById(inputId);
  const number = Number(input?.value);
  if (!number || number < 1) {
    showToast(emptyMessage, "warning");
    input?.focus();
    return;
  }

  setStatus(`${number}장 실행 중...`);
  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ number }),
    });
    const data = await res.json();
    if (!res.ok) {
      if (res.status === 404) {
        showToast("해당 파일이 없습니다.", "danger");
        setStatus("");
        return;
      }
      showToast(data.detail || "실행 실패", "danger");
      setStatus("");
      return;
    }
    setStatus(`${data.message} (${data.file_name})`);
    input?.select();
  } catch {
    showToast("실행 중 오류가 발생했습니다.", "danger");
    setStatus("");
  }
}

function setupQuickStart() {
  document.getElementById("quick-hymn-form")?.addEventListener("submit", (e) => {
    e.preventDefault();
    runQuickStart("/api/quick-start/hymn", "quick-hymn-num", "찬송가 장 번호를 입력하세요.");
  });

  document.getElementById("quick-responsive-form")?.addEventListener("submit", (e) => {
    e.preventDefault();
    runQuickStart("/api/quick-start/responsive", "quick-responsive-num", "교독문 장 번호를 입력하세요.");
  });
}

async function openItem(id) {
  setStatus("열고 있습니다...");
  try {
    const res = await fetch("/api/favorites/open", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "열기 실패");
    setStatus(data.message);
  } catch (err) {
    setStatus(err.message, true);
  }
}

function normalizeItem(item) {
  const normalized = { ...item };
  if (normalized.type === "separator") {
    normalized.type = "heading";
    normalized.name = normalized.name === "-" ? "" : normalized.name;
  }
  if (!normalized.category) {
    normalized.category = normalized.type === "file" ? "file" : "folder";
  }
  return normalized;
}

function renderSection(containerId, items, icon) {
  const el = document.getElementById(containerId);
  if (!el) return;

  if (!items.length) {
    el.innerHTML = '<p class="small text-muted mb-0">등록된 항목이 없습니다.</p>';
    return;
  }

  el.innerHTML = items.map((item) => {
    if (item.type === "heading") {
      const label = item.name || "—";
      return `<div class="quick-heading">${label}</div>`;
    }
    return `
      <button type="button" class="quick-btn" data-id="${item.id}" title="${item.path}">
        <span class="ic"><i class="fa-solid fa-${icon}"></i></span>
        <span>${item.name}</span>
      </button>`;
  }).join("");

  el.querySelectorAll(".quick-btn").forEach((btn) => {
    btn.addEventListener("click", () => openItem(btn.dataset.id));
  });
}

async function loadHome() {
  const res = await fetch("/api/favorites");
  if (!res.ok) throw new Error("즐겨찾기를 불러오지 못했습니다.");
  const data = await res.json();
  const items = data.items.map(normalizeItem);
  const folders = items.filter((i) => i.category === "folder");
  const files = items.filter((i) => i.category === "file");
  renderSection("home-folders", folders, "folder");
  renderSection("home-files", files, "file");
}

loadHome().catch((err) => setStatus(err.message, true));
setupQuickStart();
