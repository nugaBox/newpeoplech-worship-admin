/** 설정 모달 */

let favoritesDraft = [];

function setModalStatus(id, msg, isError = false) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = msg;
  el.style.color = isError ? "var(--danger)" : "var(--muted)";
}

async function loadSettingsModal() {
  await Promise.all([
    loadModalServer(),
    loadModalPaths(),
    loadModalRuntime(),
    loadModalAdmin(),
    loadModalFavorites(),
  ]);
}

async function loadModalAdmin() {
  try {
    const data = await fetch("/api/auth/me").then((r) => r.json());
    const el = document.getElementById("modal-admin-username");
    if (el) el.textContent = data.username;
  } catch {
    const el = document.getElementById("modal-admin-username");
    if (el) el.textContent = "—";
  }
  const form = document.getElementById("modal-admin-password-form");
  form?.reset();
  setModalStatus("modal-admin-status", "");
}

function apiErrorMessage(data, fallback) {
  if (Array.isArray(data.detail)) {
    return data.detail.map((d) => d.msg).join(", ");
  }
  return data.detail || fallback;
}

async function loadModalServer() {
  const statusEl = document.getElementById("modal-server-status");
  const dotEl = document.getElementById("modal-server-dot");
  const modeEl = document.getElementById("modal-server-mode");
  try {
    const data = await fetch("/api/server/status").then((r) => r.json());
    const uptime = formatModalUptime(data.uptime_seconds);
    statusEl.innerHTML = `
      <strong>${data.mode_label}</strong> · ${data.url}<br>
      가동 ${uptime} · PID ${data.pid}`;
    if (dotEl) {
      dotEl.className = "server-dot online";
      dotEl.title = `실행 중 (${data.mode_label})`;
    }
    if (modeEl) modeEl.textContent = data.mode_label;
  } catch {
    statusEl.textContent = "서버에 연결할 수 없습니다.";
    if (dotEl) {
      dotEl.className = "server-dot offline";
      dotEl.title = "연결 끊김";
    }
    if (modeEl) modeEl.textContent = "연결 끊김";
  }
}

function formatModalUptime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  if (m > 0) return `${m}분 ${s}초`;
  return `${s}초`;
}

async function loadModalPaths() {
  const res = await fetch("/api/settings/paths");
  const data = await res.json();
  const el = document.getElementById("modal-paths-list");

  const groupOrder = ["document", "quick_start"];
  const groupTitles = {
    document: "문서·생성",
    quick_start: "빠른 시작",
  };

  el.innerHTML = groupOrder.map((groupId) => {
    const items = data.paths.filter((p) => (p.group || "document") === groupId);
    if (!items.length) return "";
    return `
      <div class="path-group">
        <div class="path-group-label">${groupTitles[groupId] || items[0].group_label}</div>
        ${items.map((p) => renderPathRow(p)).join("")}
      </div>`;
  }).join("");

  el.querySelectorAll(".path-browse-btn").forEach((btn) => {
    btn.addEventListener("click", () => browsePath(btn.dataset.key));
  });
  el.querySelectorAll(".path-save-btn").forEach((btn) => {
    btn.addEventListener("click", () => savePath(btn.dataset.key));
  });
}

function renderPathRow(p) {
  const hint = p.hint
    ? `<p class="path-setting-hint small text-muted mb-2">${p.hint}</p>`
    : "";
  return `
    <div class="path-setting-row" data-key="${p.key}">
      <div class="path-setting-meta">
        <h6><span class="path-status ${p.exists ? "ok" : "bad"}">${p.exists ? "✓" : "✗"}</span> ${p.label}</h6>
        ${hint}
        <div class="path-setting-field">
          <input type="text" class="form-control form-control-sm path-input" value="${escapeAttr(p.path)}">
          <button type="button" class="btn-ghost path-browse-btn" data-key="${p.key}">
            <i class="fa-solid fa-folder-open me-1"></i>${p.kind === "file" ? "파일 찾기" : "폴더 찾기"}
          </button>
          <button type="button" class="btn-dark-pill path-save-btn" data-key="${p.key}">저장</button>
        </div>
      </div>
    </div>`;
}

function escapeAttr(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;");
}

function updatePathRow(row, pathData) {
  if (!row) return;
  const status = row.querySelector(".path-status");
  const input = row.querySelector(".path-input");
  if (status) {
    status.textContent = pathData.exists ? "✓" : "✗";
    status.classList.toggle("ok", pathData.exists);
    status.classList.toggle("bad", !pathData.exists);
  }
  if (input) input.value = pathData.path;
}

async function browsePath(key) {
  setModalStatus("modal-paths-status", "폴더·파일 찾기 창을 여는 중...");
  try {
    const res = await fetch(`/api/settings/paths/${key}/browse`, { method: "POST" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "찾기 실패");
    updatePathRow(document.querySelector(`.path-setting-row[data-key="${key}"]`), data);
    setModalStatus("modal-paths-status", `저장됨: ${data.path}`);
  } catch (err) {
    setModalStatus("modal-paths-status", err.message, true);
  }
}

async function savePath(key) {
  const row = document.querySelector(`.path-setting-row[data-key="${key}"]`);
  const input = row?.querySelector(".path-input");
  if (!input) return;
  const path = input.value.trim();
  if (!path) return setModalStatus("modal-paths-status", "경로를 입력하세요.", true);

  setModalStatus("modal-paths-status", "저장 중...");
  try {
    const res = await fetch(`/api/settings/paths/${key}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "저장 실패");
    updatePathRow(row, data);
    setModalStatus("modal-paths-status", `저장됨: ${data.path}`);
  } catch (err) {
    setModalStatus("modal-paths-status", err.message, true);
  }
}

async function loadModalRuntime() {
  const res = await fetch("/api/settings/runtime");
  const data = await res.json();
  document.getElementById("modal-run-mode").value = data.run_mode;
  document.getElementById("modal-host").value = data.host;
  document.getElementById("modal-port").value = data.port;
}

function renderFavoritesEditor() {
  const el = document.getElementById("modal-favorites-editor");
  el.innerHTML = favoritesDraft.map((item, idx) => {
    const isHeading = item.type === "heading" || item.type === "separator";
    const type = item.type === "separator" ? "heading" : item.type;
    return `
    <div class="fav-edit-row" data-idx="${idx}">
      <select class="form-select form-select-sm fav-category">
        <option value="folder" ${item.category !== "file" ? "selected" : ""}>폴더 영역</option>
        <option value="file" ${item.category === "file" ? "selected" : ""}>파일 영역</option>
      </select>
      <select class="form-select form-select-sm fav-type">
        <option value="folder" ${type === "folder" ? "selected" : ""}>폴더</option>
        <option value="file" ${type === "file" ? "selected" : ""}>파일</option>
        <option value="heading" ${type === "heading" ? "selected" : ""}>소제목</option>
      </select>
      <input class="form-control form-control-sm fav-name" value="${item.name || ""}" placeholder="${isHeading ? "소제목 (예: 찬송가)" : "메뉴 이름"}">
      <input class="form-control form-control-sm fav-path" value="${item.path || ""}" placeholder="경로" ${isHeading ? "disabled" : ""}>
      <button type="button" class="icon-btn fav-del" title="삭제"><i class="fa-solid fa-xmark"></i></button>
    </div>`;
  }).join("");

  el.querySelectorAll(".fav-edit-row").forEach((row) => {
    const idx = Number(row.dataset.idx);
    row.querySelector(".fav-category").addEventListener("change", (e) => {
      favoritesDraft[idx].category = e.target.value;
    });
    row.querySelector(".fav-type").addEventListener("change", (e) => {
      favoritesDraft[idx].type = e.target.value;
      if (e.target.value === "heading") favoritesDraft[idx].path = "";
      renderFavoritesEditor();
    });
    row.querySelector(".fav-name").addEventListener("input", (e) => {
      favoritesDraft[idx].name = e.target.value;
    });
    row.querySelector(".fav-path").addEventListener("input", (e) => {
      favoritesDraft[idx].path = e.target.value;
    });
    row.querySelector(".fav-del").addEventListener("click", () => {
      favoritesDraft.splice(idx, 1);
      renderFavoritesEditor();
    });
  });
}

async function loadModalFavorites() {
  const res = await fetch("/api/favorites");
  const data = await res.json();
  favoritesDraft = data.items.map((i) => ({
    ...i,
    category: i.category || (i.type === "file" ? "file" : "folder"),
    type: i.type === "separator" ? "heading" : i.type,
  }));
  renderFavoritesEditor();
}

function addFavorite(type, category = "folder") {
  favoritesDraft.push({
    id: `new_${Date.now()}`,
    type,
    category,
    name: type === "heading" ? "" : "",
    path: "",
  });
  renderFavoritesEditor();
}

document.getElementById("modal-btn-refresh-server")?.addEventListener("click", () => {
  loadModalServer().then(() => setModalStatus("modal-server-action", "새로고침했습니다."));
});

document.getElementById("modal-btn-restart-server")?.addEventListener("click", () => {
  restartServer({
    saveRuntimeFromModal: true,
    onStatus: (msg, isError) => setModalStatus("modal-server-action", msg, isError),
  });
});

document.getElementById("modal-btn-stop-server")?.addEventListener("click", () => {
  stopServer({
    onStatus: (msg, isError) => setModalStatus("modal-server-action", msg, isError),
  });
});

document.getElementById("modal-btn-save-runtime")?.addEventListener("click", async () => {
  const body = {
    run_mode: document.getElementById("modal-run-mode").value,
    host: document.getElementById("modal-host").value,
    port: Number(document.getElementById("modal-port").value),
    open_browser: false,
  };
  const res = await fetch("/api/settings/runtime", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) return setModalStatus("modal-runtime-status", data.detail || "저장 실패", true);
  setModalStatus("modal-runtime-status", `저장됨: ${data.mode_label} (포트 변경은 재시작 후 적용)`);
});

document.getElementById("modal-btn-add-folder")?.addEventListener("click", () => addFavorite("folder", "folder"));
document.getElementById("modal-btn-add-file")?.addEventListener("click", () => addFavorite("file", "file"));
document.getElementById("modal-btn-add-heading")?.addEventListener("click", () => addFavorite("heading", "folder"));

document.getElementById("modal-admin-password-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = document.getElementById("modal-btn-change-password");
  const current_password = document.getElementById("modal-admin-current-pw").value;
  const new_password = document.getElementById("modal-admin-new-pw").value;
  const new_password_confirm = document.getElementById("modal-admin-new-pw-confirm").value;

  if (new_password.length < 4) {
    return setModalStatus("modal-admin-status", "새 비밀번호는 4자 이상이어야 합니다.", true);
  }
  if (new_password !== new_password_confirm) {
    return setModalStatus("modal-admin-status", "새 비밀번호 확인이 일치하지 않습니다.", true);
  }

  btn.disabled = true;
  setModalStatus("modal-admin-status", "변경 중...");
  try {
    const res = await fetch("/api/auth/password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ current_password, new_password, new_password_confirm }),
    });
    const data = await res.json();
    if (!res.ok) {
      return setModalStatus("modal-admin-status", apiErrorMessage(data, "비밀번호 변경에 실패했습니다."), true);
    }
    document.getElementById("modal-admin-password-form")?.reset();
    setModalStatus("modal-admin-status", data.message || "비밀번호가 변경되었습니다.");
  } catch {
    setModalStatus("modal-admin-status", "서버에 연결할 수 없습니다.", true);
  } finally {
    btn.disabled = false;
  }
});

document.getElementById("modal-btn-save-favorites")?.addEventListener("click", async () => {
  const res = await fetch("/api/favorites", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ items: favoritesDraft }),
  });
  if (!res.ok) return setModalStatus("modal-favorites-status", "저장 실패", true);
  setModalStatus("modal-favorites-status", "저장되었습니다. 홈 화면을 새로고침하면 반영됩니다.");
});

window.loadSettingsModal = loadSettingsModal;
