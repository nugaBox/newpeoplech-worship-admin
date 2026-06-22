/** Bootstrap Toast — 잠깐 뜨는 알림 */

const TOAST_DURATION_MS = 2800;

function ensureToastContainer() {
  let container = document.getElementById("toast-container");
  if (container) return container;

  container = document.createElement("div");
  container.id = "toast-container";
  container.className = "toast-container position-fixed top-0 start-50 translate-middle-x p-3";
  container.style.zIndex = "1080";
  document.body.appendChild(container);
  return container;
}

/**
 * @param {string} message
 * @param {"success"|"danger"|"warning"|"info"} [variant]
 * @param {number} [duration]
 */
function showToast(message, variant = "danger", duration = TOAST_DURATION_MS) {
  const container = ensureToastContainer();
  const toastEl = document.createElement("div");
  toastEl.className = `toast align-items-center text-bg-${variant} border-0 shadow-sm`;
  toastEl.setAttribute("role", "alert");
  toastEl.setAttribute("aria-live", "assertive");
  toastEl.setAttribute("aria-atomic", "true");
  toastEl.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="닫기"></button>
    </div>`;

  container.appendChild(toastEl);
  const toast = bootstrap.Toast.getOrCreateInstance(toastEl, {
    autohide: true,
    delay: duration,
  });
  toastEl.addEventListener("hidden.bs.toast", () => toastEl.remove());
  toast.show();
}

window.showToast = showToast;
