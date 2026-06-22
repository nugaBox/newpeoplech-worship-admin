/** 홈 — 즐겨찾기 폴더·파일 열기 */

function setStatus(msg, isError = false) {
  const el = document.getElementById("home-status");
  if (!el) return;
  el.textContent = msg;
  el.style.color = isError ? "var(--danger)" : "var(--muted)";
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

function renderSection(containerId, items, icon) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = items.map((item) => {
    if (item.type === "separator") return '<div class="quick-sep"></div>';
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
  const folders = data.items.filter((i) => i.type === "folder" || i.type === "separator");
  const programs = data.items.filter((i) => i.type === "file" || (i.type === "separator" && !folders.includes(i)));
  // programs: file + separators that appear after first file block
  let inPrograms = false;
  const progItems = [];
  for (const item of data.items) {
    if (item.type === "file") inPrograms = true;
    if (inPrograms && (item.type === "file" || item.type === "separator")) progItems.push(item);
  }
  renderSection("home-folders", folders, "folder");
  renderSection("home-programs", progItems.length ? progItems : data.items.filter((i) => i.type === "file"), "file");
}

loadHome().catch((err) => setStatus(err.message, true));
