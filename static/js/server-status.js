/** 서버 상태 (settings-modal.js와 worship-admin.js에서 공통 사용) */

async function fetchServerStatus() {
  const res = await fetch("/api/server/status");
  if (!res.ok) throw new Error("서버 상태를 불러오지 못했습니다.");
  return res.json();
}

function formatUptime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  if (m > 0) return `${m}분 ${s}초`;
  return `${s}초`;
}

function updateServerBadge(data) {
  const dot = document.getElementById("nav-server-dot");
  const label = document.getElementById("side-server-label");
  if (dot) {
    dot.className = `server-dot ${data ? "online" : "offline"}`;
    dot.title = data ? `실행 중 (${data.mode_label})` : "연결 끊김";
  }
  if (label) {
    label.textContent = data
      ? `${data.mode_label} · ${formatUptime(data.uptime_seconds)}`
      : "연결 끊김";
  }
}

async function loadServerStatus() {
  try {
    const data = await fetchServerStatus();
    updateServerBadge(data);
    return data;
  } catch {
    updateServerBadge(null);
    return null;
  }
}

if (document.getElementById("nav-server-dot")) {
  loadServerStatus();
  setInterval(loadServerStatus, 15000);
}
