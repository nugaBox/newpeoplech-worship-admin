/** 예배 관리 — 목차 선택 + 생성 */

let selectedOutline = null;

function setStatus(msg, isError = false) {
  const el = document.getElementById("worship-status");
  if (!el) return;
  el.textContent = msg;
  el.style.color = isError ? "var(--danger)" : "var(--muted)";
}

function setResult(html) {
  document.getElementById("worship-result").innerHTML = html;
}

function enableActions(enabled) {
  ["card-hwp", "card-ppt-day"].forEach((id) => {
    document.getElementById(id)?.classList.toggle("disabled", !enabled);
  });
  document.getElementById("btn-hwp").disabled = !enabled;
  document.getElementById("btn-ppt-day").disabled = !enabled;
}

function showSummary(outline) {
  const box = document.getElementById("worship-outline-summary");
  const f = outline.fields;
  box.classList.remove("d-none");
  box.innerHTML = `
    <dl>
      <dt>날짜</dt><dd>${f.F_날짜 || "-"}</dd>
      <dt>경배찬송</dt><dd>${f.R_A_경배찬송 || "-"}</dd>
      <dt>설교</dt><dd>${f.R_A_설교제목 || f.R_B_설교제목 || "-"}</dd>
      <dt>설교자</dt><dd>${f.R_A_설교자 || f.R_B_인도자 || "-"}</dd>
    </dl>`;
}

async function loadOutlines() {
  const res = await fetch("/api/outlines");
  if (!res.ok) throw new Error("목차 목록을 불러오지 못했습니다.");
  const data = await res.json();
  const sel = document.getElementById("worship-outline-select");
  const cur = sel.value;
  sel.innerHTML = '<option value="">— 목차를 선택하세요 —</option>' +
    data.outlines.map((o) => `<option value="${o.id}">${o.title}</option>`).join("");
  if (cur) sel.value = cur;
}

async function selectOutline(id) {
  if (!id) {
    selectedOutline = null;
    enableActions(false);
    document.getElementById("worship-outline-summary").classList.add("d-none");
    setResult('<span class="text-muted">목차를 선택한 뒤 생성 버튼을 누르세요.</span>');
    return;
  }
  const res = await fetch(`/api/outlines/${id}`);
  if (!res.ok) throw new Error("목차를 불러오지 못했습니다.");
  selectedOutline = await res.json();
  enableActions(true);
  showSummary(selectedOutline);
  setStatus(`목차 선택: ${selectedOutline.title}`);
}

async function submitGeneration(endpoint, label, extraFiles = {}) {
  if (!selectedOutline) return;
  setStatus(`${label} 생성 중...`);
  const formData = new FormData();
  formData.append("fields_json", JSON.stringify(selectedOutline.fields));
  for (const [key, inputId] of Object.entries(extraFiles)) {
    const input = document.getElementById(inputId);
    if (input?.files?.[0]) formData.append(key, input.files[0]);
  }
  const res = await fetch(endpoint, { method: "POST", body: formData });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "생성 실패");
  let html = `<p class="mb-2">${data.message}</p>`;
  if (data.download_url) {
    html += `<a class="download-link" href="${data.download_url}" download><i class="fa-solid fa-download me-1"></i>${data.filename}</a>`;
  }
  if (data.warnings?.length) {
    html += `<ul class="mt-2 mb-0">${data.warnings.map((w) => `<li>${w}</li>`).join("")}</ul>`;
  }
  setResult(html);
  setStatus(`${label} 완료`);
}

document.getElementById("worship-outline-select")?.addEventListener("change", (e) => {
  selectOutline(e.target.value).catch((err) => setStatus(err.message, true));
});

document.getElementById("worship-reload-outlines")?.addEventListener("click", () => {
  loadOutlines().catch((err) => setStatus(err.message, true));
});

document.getElementById("btn-hwp")?.addEventListener("click", () => {
  submitGeneration("/api/bulletin/hwp", "주보").catch((e) => setStatus(e.message, true));
});

document.getElementById("btn-ppt-day")?.addEventListener("click", () => {
  submitGeneration("/api/bulletin/ppt/day", "낮예배 PPT", {
    prayer_file: "prayer-file",
    sermon_file: "sermon-file",
    ad_file: "ad-file",
  }).catch((e) => setStatus(e.message, true));
});

loadOutlines().catch((e) => setStatus(e.message, true));
