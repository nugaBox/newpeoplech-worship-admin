/** 로그인 · 최초 비밀번호 설정 */

const themeBtn = document.getElementById("themeToggle");
const themeIcon = document.getElementById("themeIcon");

function setTheme(t) {
  document.documentElement.setAttribute("data-theme", t);
  if (themeIcon) themeIcon.className = t === "dark" ? "fa-solid fa-sun" : "fa-solid fa-moon";
  try { localStorage.setItem("admin-theme", t); } catch (e) {}
}
themeBtn?.addEventListener("click", () => {
  const cur = document.documentElement.getAttribute("data-theme") || "light";
  setTheme(cur === "dark" ? "light" : "dark");
});
try {
  const saved = localStorage.getItem("admin-theme");
  if (saved) setTheme(saved);
} catch (e) {}

function getNextUrl() {
  const params = new URLSearchParams(location.search);
  const next = params.get("next");
  if (!next || !next.startsWith("/") || next.startsWith("//")) return "/";
  return next;
}

function showError(el, msg) {
  if (!el) return;
  if (!msg) {
    el.hidden = true;
    el.textContent = "";
    return;
  }
  el.hidden = false;
  el.textContent = msg;
}

function redirectAfterAuth() {
  location.href = getNextUrl();
}

function showAuthPanel(passwordConfigured) {
  const setupPanel = document.getElementById("setupPanel");
  const loginPanel = document.getElementById("loginPanel");
  if (passwordConfigured) {
    if (setupPanel) setupPanel.style.display = "none";
    if (loginPanel) loginPanel.style.display = "";
  } else {
    if (setupPanel) setupPanel.style.display = "";
    if (loginPanel) loginPanel.style.display = "none";
  }
}

async function initAuthPage() {
  const body = document.body;
  const defaultConfigured = body?.dataset.passwordConfigured === "true";
  const defaultUsername = body?.dataset.username || "admin";

  const setupUsername = document.getElementById("setupUsername");
  const loginId = document.getElementById("loginId");
  if (setupUsername) setupUsername.textContent = defaultUsername;
  if (loginId && !loginId.value) loginId.value = defaultUsername;

  showAuthPanel(defaultConfigured);

  try {
    const res = await fetch("/api/auth/status");
    if (!res.ok) return;
    const data = await res.json();
    if (setupUsername) setupUsername.textContent = data.username;
    if (loginId) loginId.value = data.username;
    showAuthPanel(Boolean(data.password_configured));
  } catch {
    // 서버 렌더링 결과 유지
  }
}

document.getElementById("setupForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = document.getElementById("setupSubmit");
  const errEl = document.getElementById("setupError");
  showError(errEl, "");

  const password = document.getElementById("setupPw").value;
  const password_confirm = document.getElementById("setupPwConfirm").value;

  if (password.length < 4) {
    showError(errEl, "비밀번호는 4자 이상이어야 합니다.");
    return;
  }
  if (password !== password_confirm) {
    showError(errEl, "비밀번호 확인이 일치하지 않습니다.");
    return;
  }

  btn.disabled = true;
  try {
    const res = await fetch("/api/auth/setup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password, password_confirm }),
    });
    const data = await res.json();
    if (!res.ok) {
      const detail = Array.isArray(data.detail)
        ? data.detail.map((d) => d.msg).join(", ")
        : data.detail;
      showError(errEl, detail || "비밀번호 설정에 실패했습니다.");
      return;
    }
    redirectAfterAuth();
  } catch {
    showError(errEl, "서버에 연결할 수 없습니다.");
  } finally {
    btn.disabled = false;
  }
});

document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const btn = document.getElementById("loginSubmit");
  const errEl = document.getElementById("loginError");
  showError(errEl, "");

  const username = document.getElementById("loginId").value.trim();
  const password = document.getElementById("loginPw").value;
  const remember = document.getElementById("rememberLogin").checked;

  btn.disabled = true;
  try {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password, remember }),
    });
    const data = await res.json();
    if (!res.ok) {
      const detail = Array.isArray(data.detail)
        ? data.detail.map((d) => d.msg).join(", ")
        : data.detail;
      showError(errEl, detail || "로그인에 실패했습니다.");
      return;
    }
    redirectAfterAuth();
  } catch {
    showError(errEl, "서버에 연결할 수 없습니다.");
  } finally {
    btn.disabled = false;
  }
});

initAuthPage();
