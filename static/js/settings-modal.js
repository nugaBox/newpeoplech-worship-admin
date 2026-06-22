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
    loadModalFavorites(),
  ]);
}

async function loadModalServer() {
  try {
    const data = await fetch("/api/server/status").then((r) => r.json());
    document.getElementById("modal-server-status").innerHTML = `
      <strong>${data.mode_label}</strong> · ${data.url}<br>
      가동 ${data.uptime_seconds}초 · PID ${data.pid}`;
  } catch {
    document.getElementById("modal-server-status").textContent = "서버에 연결할 수 없습니다.";
  }
}

async function loadModalPaths() {
  const res = await fetch("/api/settings/paths");
  const data = await res.json();
  document.getElementById("modal-paths-list").innerHTML = data.paths.map((p) => `
    <div class="ms-row">
      <div class="ms-meta">
        <h6>${p.exists ? "✓" : "✗"} ${p.label}</h6>
        <p><code style="font-size:12px;word-break:break-all;">${p.path}</code></p>
      </div>
    </div>`).join("");
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
  el.innerHTML = favoritesDraft.map((item, idx) => `
    <div class="fav-edit-row" data-idx="${idx}">
      <select class="form-select form-select-sm fav-type">
        <option value="folder" ${item.type === "folder" ? "selected" : ""}>폴더</option>
        <option value="file" ${item.type === "file" ? "selected" : ""}>파일</option>
        <option value="separator" ${item.type === "separator" ? "selected" : ""}>구분선</option>
      </select>
      <input class="form-control form-control-sm fav-name" value="${item.name || ""}" placeholder="메뉴 이름">
      <input class="form-control form-control-sm fav-path" value="${item.path || ""}" placeholder="경로" ${item.type === "separator" ? "disabled" : ""}>
      <button type="button" class="icon-btn fav-del" title="삭제"><i class="fa-solid fa-xmark"></i></button>
    </div>`).join("");

  el.querySelectorAll(".fav-edit-row").forEach((row) => {
    const idx = Number(row.dataset.idx);
    row.querySelector(".fav-type").addEventListener("change", (e) => {
      favoritesDraft[idx].type = e.target.value;
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
  favoritesDraft = data.items.map((i) => ({ ...i }));
  renderFavoritesEditor();
}

function addFavorite(type) {
  favoritesDraft.push({
    id: `new_${Date.now()}`,
    type,
    name: type === "separator" ? "-" : "",
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

document.getElementById("modal-btn-add-folder")?.addEventListener("click", () => addFavorite("folder"));
document.getElementById("modal-btn-add-file")?.addEventListener("click", () => addFavorite("file"));
document.getElementById("modal-btn-add-sep")?.addEventListener("click", () => addFavorite("separator"));

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
