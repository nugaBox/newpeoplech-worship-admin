/** 관리자 공통 UI (테마, 사이드바, 모달) */

const themeBtn = document.getElementById("themeToggle");
const themeIcon = document.getElementById("themeIcon");

function setTheme(t) {
  document.documentElement.setAttribute("data-theme", t);
  if (themeIcon) themeIcon.className = t === "dark" ? "fa-solid fa-sun" : "fa-solid fa-moon";
  try { localStorage.setItem("admin-theme", t); } catch (e) {}
}
window.setAdminTheme = setTheme;

themeBtn?.addEventListener("click", () => {
  const cur = document.documentElement.getAttribute("data-theme") || "light";
  setTheme(cur === "dark" ? "light" : "dark");
});
try {
  const saved = localStorage.getItem("admin-theme");
  if (saved) setTheme(saved);
} catch (e) {}

const sb = document.getElementById("sidebar");
const sc = document.getElementById("scrim");
const appEl = document.getElementById("adminApp");
const sideToggle = document.getElementById("sideToggle");

sideToggle?.addEventListener("click", () => {
  if (window.matchMedia("(max-width: 768px)").matches) {
    sb?.classList.add("open");
    sc?.classList.add("show");
  } else {
    appEl?.classList.toggle("collapsed");
  }
});
sc?.addEventListener("click", () => {
  sb?.classList.remove("open");
  sc?.classList.remove("show");
});

(function () {
  const curPath = location.pathname.replace(/\/$/, "") || "/";
  document.querySelectorAll(".sidebar .nav-item").forEach((a) => {
    const href = a.getAttribute("href")?.replace(/\/$/, "") || "/";
    if (href === curPath) a.classList.add("active");
  });
})();

function openModal(id) {
  const el = document.getElementById("modal-" + id);
  if (el) {
    el.classList.add("show");
    document.body.style.overflow = "hidden";
    if (id === "settings" && typeof loadSettingsModal === "function") {
      loadSettingsModal();
    }
  }
}
function closeModal(el) {
  el.classList.remove("show");
  if (!document.querySelector(".modal-bd.show")) document.body.style.overflow = "";
}

document.addEventListener("click", (e) => {
  const trigger = e.target.closest("[data-open-modal]");
  if (trigger) {
    openModal(trigger.dataset.openModal);
    e.preventDefault();
    return;
  }
  if (e.target.closest("[data-close-modal]")) {
    const m = e.target.closest(".modal-bd");
    if (m) closeModal(m);
    return;
  }
  if (e.target.classList.contains("modal-bd")) closeModal(e.target);
});

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") document.querySelectorAll(".modal-bd.show").forEach(closeModal);
});

document.querySelectorAll(".modal-settings .ms-item").forEach((item) => {
  item.addEventListener("click", () => {
    document.querySelectorAll(".modal-settings .ms-item").forEach((i) => i.classList.remove("active"));
    item.classList.add("active");
    const target = item.dataset.ms;
    document.querySelectorAll(".modal-settings .ms-pane").forEach((p) => {
      p.style.display = p.dataset.pane === target ? "" : "none";
    });
  });
});
