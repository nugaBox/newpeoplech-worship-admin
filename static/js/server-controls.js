/** 서버 중지·재시작 (사이드바·설정 모달 공통) */

async function waitForServerBack(maxSeconds = 30) {
  for (let i = 0; i < maxSeconds; i++) {
    await new Promise((r) => setTimeout(r, 1000));
    try {
      const res = await fetch("/api/server/status");
      if (res.ok) return true;
    } catch {}
  }
  return false;
}

async function restartServer(options = {}) {
  const {
    confirmMessage = "서버를 재시작합니다. 잠시 연결이 끊길 수 있습니다.",
    saveRuntimeFromModal = false,
    onStatus,
  } = options;

  if (!confirm(confirmMessage)) return false;

  if (typeof onStatus === "function") onStatus("재시작 중...");

  try {
    if (saveRuntimeFromModal) {
      await fetch("/api/settings/runtime", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          run_mode: document.getElementById("modal-run-mode")?.value,
          host: document.getElementById("modal-host")?.value,
          port: Number(document.getElementById("modal-port")?.value),
          open_browser: false,
        }),
      });
    }

    const res = await fetch("/api/server/restart", { method: "POST" });
    const data = await res.json();
    if (typeof onStatus === "function") onStatus(data.message || "재시작 중...");

    const ok = await waitForServerBack();
    if (ok) {
      if (typeof onStatus === "function") onStatus("서버가 다시 시작되었습니다.");
      if (typeof loadServerStatus === "function") loadServerStatus();
      if (typeof loadModalServer === "function") loadModalServer();
      return true;
    }
    if (typeof onStatus === "function") {
      onStatus("재시작 대기 시간 초과. 페이지를 새로고침하세요.", true);
    }
    return false;
  } catch (err) {
    if (typeof onStatus === "function") onStatus(err.message, true);
    return false;
  }
}

async function stopServer(options = {}) {
  const {
    confirmMessage = "서버를 중지합니다. 다시 사용하려면 터미널에서 python start.py 를 실행하세요.",
    onStatus,
  } = options;

  if (!confirm(confirmMessage)) return false;

  if (typeof onStatus === "function") onStatus("중지 중...");

  try {
    const res = await fetch("/api/server/stop", { method: "POST" });
    const data = await res.json();
    if (typeof onStatus === "function") onStatus(data.message || "서버를 중지했습니다.");
    if (typeof updateServerBadge === "function") updateServerBadge(null);
    return true;
  } catch (err) {
    if (typeof onStatus === "function") onStatus(err.message, true);
    return false;
  }
}

document.getElementById("btn-server-restart")?.addEventListener("click", () => {
  restartServer();
});

document.getElementById("btn-server-stop")?.addEventListener("click", () => {
  stopServer();
});

window.restartServer = restartServer;
window.stopServer = stopServer;
