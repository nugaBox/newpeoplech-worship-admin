/* ============================================================
   admin.js — 관리자 공통 + 대시보드 스크립트
   (script.js + main.js + sub.js 통합)
   ============================================================ */

/* ── data-include 로더 ──────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  const includes = document.querySelectorAll("[data-include]");
  Promise.all(
    [...includes].map((el) =>
      fetch(el.dataset.include)
        .then((res) => {
          if (!res.ok) throw new Error(`${el.dataset.include} 로드 실패`);
          return res.text();
        })
        .then((html) => { el.outerHTML = html; })
        .catch((err) => console.warn(err))
    )
  );
});

/* ── 테마 토글 ──────────────────────────────────────────────── */
const themeBtn  = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');

function setTheme(t) {
  document.documentElement.setAttribute('data-theme', t);
  if (themeIcon) themeIcon.className = t === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
  try { localStorage.setItem('admin-theme', t); } catch (e) {}
}
themeBtn?.addEventListener('click', () => {
  const cur = document.documentElement.getAttribute('data-theme') || 'light';
  setTheme(cur === 'dark' ? 'light' : 'dark');
});
try {
  const saved = localStorage.getItem('admin-theme');
  if (saved) setTheme(saved);
} catch (e) {}

/* ── 사이드바 토글 ──────────────────────────────────────────── */
const sb         = document.getElementById('sidebar');
const sc         = document.getElementById('scrim');
const appEl      = document.getElementById('adminApp') || document.querySelector('.app');
const sideToggle = document.getElementById('sideToggle');

sideToggle?.addEventListener('click', () => {
  if (window.matchMedia('(max-width: 768px)').matches) {
    sb?.classList.add('open');
    sc?.classList.add('show');
  } else {
    appEl?.classList.toggle('collapsed');
  }
});
sc?.addEventListener('click', () => {
  sb?.classList.remove('open');
  sc?.classList.remove('show');
});

/* ── 현재 페이지 활성 네비 (서브 페이지용 <a> 링크) ─────────── */
(function () {
  const curPath = location.pathname;
  document.querySelectorAll('.sidebar .nav-item').forEach(a => {
    if (a.href && a.href.includes(curPath.split('/').pop())) {
      a.classList.add('active');
    }
  });
})();

/* ── 대시보드 페이지 내비게이션 ─────────────────────────────── */
const PAGES = {
  dashboard: '관리자 홈',
  analytics: '통계 · 리포트',
  users:     '회원 관리',
  content:   '콘텐츠 관리',
  orders:    '주문 · 결제',
  notice:    '공지 · 배너',
  logs:      '활동 로그',
  settings:  '환경 설정',
  help:      '도움말'
};

function go(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('show'));
  const el = document.getElementById('page-' + page);
  if (el) el.classList.add('show');
  document.querySelectorAll('.sidebar .nav-item').forEach(n => n.classList.remove('active'));
  const link = document.querySelector(`.sidebar .nav-item[data-page="${page}"]`);
  if (link) link.classList.add('active');
  const crumb = document.getElementById('crumb');
  if (crumb) crumb.textContent = PAGES[page] || '';
  document.getElementById('sidebar')?.classList.remove('open');
  document.getElementById('scrim')?.classList.remove('show');
  window.scrollTo({ top: 0, behavior: 'instant' });
}

document.querySelectorAll('.sidebar [data-page]').forEach(n => {
  n.addEventListener('click', () => go(n.dataset.page));
});
document.querySelectorAll('[data-go]').forEach(a => {
  a.addEventListener('click', e => { e.preventDefault(); go(a.dataset.go); });
});

/* ── 세그먼트 토글 ────────────────────────────────────────── */
document.querySelectorAll('.seg').forEach(seg => {
  seg.querySelectorAll('button').forEach(b => {
    b.addEventListener('click', () => {
      seg.querySelectorAll('button').forEach(x => x.classList.remove('on'));
      b.classList.add('on');
    });
  });
});

/* ── 회원 목록 생성 ─────────────────────────────────────────── */
const USERS = [
  { n: '박서연',   e: 'seoyeon@mail.com',       p: 'Pro',  r: '멤버',  l: '2분 전',    s: 'success', st: '활성',   d: '2026-05-12', c: '#eef3ff,#dbeafe,#1d4ed8' },
  { n: '정현우',   e: 'hyunwoo@studio.io',      p: 'Free', r: '멤버',  l: '12시간 전', s: 'warn',    st: '미인증', d: '2026-05-11', c: '#fee2e2,#fecaca,#b91c1c' },
  { n: '이지민',   e: 'jimin.lee@corp.co',      p: 'Team', r: '관리자', l: '1시간 전',  s: 'success', st: '활성',   d: '2026-05-11', c: '#dcfce7,#bbf7d0,#15803d' },
  { n: '최도윤',   e: 'doyoon.choi@gmail.com',  p: 'Pro',  r: '멤버',  l: '3일 전',    s: 'danger',  st: '정지',   d: '2026-05-10', c: '#dbeafe,#bfdbfe,#1d4ed8' },
  { n: '윤하늘',   e: 'haneul.y@workmail.kr',   p: 'Free', r: '멤버',  l: '방금 전',   s: 'success', st: '활성',   d: '2026-05-09', c: '#fef3c7,#fde68a,#a16207' },
  { n: '한승우',   e: 'seungwoo@company.io',    p: 'Team', r: '에디터', l: '4시간 전',  s: 'success', st: '활성',   d: '2026-05-08', c: '#dcfce7,#bbf7d0,#15803d' },
  { n: '송미래',   e: 'mirae.s@cre.io',         p: 'Pro',  r: '멤버',  l: '2일 전',    s: 'success', st: '활성',   d: '2026-05-07', c: '#f1ecfe,#ddd6fe,#6d28d9' },
  { n: '조윤지',   e: 'yj.cho@dev.kr',          p: 'Free', r: '멤버',  l: '어제',      s: 'warn',    st: '미인증', d: '2026-05-06', c: '#fef3c7,#fde68a,#a16207' },
  { n: '장태현',   e: 'taehyun@biz.com',        p: 'Team', r: '관리자', l: '30분 전',   s: 'success', st: '활성',   d: '2026-05-05', c: '#dbeafe,#bfdbfe,#1d4ed8' },
  { n: '문서영',   e: 'seoyoung@design.kr',     p: 'Pro',  r: '멤버',  l: '5일 전',    s: 'success', st: '활성',   d: '2026-05-04', c: '#f1ecfe,#ddd6fe,#6d28d9' },
  { n: '배지호',   e: 'jiho.b@startup.io',      p: 'Pro',  r: '멤버',  l: '어제',      s: 'success', st: '활성',   d: '2026-05-03', c: '#e3f5f2,#a7e8de,#0d9488' },
  { n: '권나래',   e: 'narae.k@studio.kr',      p: 'Free', r: '멤버',  l: '1주일 전',  s: 'danger',  st: '정지',   d: '2026-05-02', c: '#fee2e2,#fecaca,#b91c1c' },
];
const planTag  = p => p === 'Pro' ? 'accent' : p === 'Team' ? 'violet' : '';
const userRows = document.getElementById('userRows');
if (userRows) {
  userRows.innerHTML = USERS.map(u => {
    const [a, b, col] = u.c.split(',');
    return `<tr>
      <td><input class="form-check-input" type="checkbox"></td>
      <td><div class="user-cell">
        <div class="avatar" style="background:linear-gradient(135deg,${a},${b});color:${col};">${u.n[0]}</div>
        <div><div class="name">${u.n}</div><div class="em">${u.e}</div></div>
      </div></td>
      <td><span class="tag ${planTag(u.p)}">${u.p}</span></td>
      <td>${u.r}</td>
      <td>${u.l}</td>
      <td><span class="tag ${u.s} dot">${u.st}</span></td>
      <td>${u.d}</td>
      <td><button class="btn-ghost py-1 px-2"><i class="fa-solid fa-ellipsis"></i></button></td>
    </tr>`;
  }).join('');
}

/* ── 차트 ─────────────────────────────────────────────────── */
if (typeof Chart !== 'undefined') {
  Chart.defaults.font.family = '"Pretendard Variable", Pretendard, system-ui, sans-serif';
  Chart.defaults.font.size   = 11.5;
  Chart.defaults.color       = '#6b7280';
  Chart.defaults.borderColor = '#ececef';

  const gridLine = { color: '#f1f2f4', drawTicks: false, drawBorder: false };
  const noGrid   = { display: false, drawTicks: false, drawBorder: false };
  const tickStyle = { color: '#9aa0a6', font: { size: 11 } };

  function sparkline(id, data, color) {
    const ctx = document.getElementById(id);
    if (!ctx) return;
    new Chart(ctx, {
      type: 'line',
      data: { labels: data.map((_, i) => i), datasets: [{ data, borderColor: color, backgroundColor: color + '1f', fill: true, tension: .4, borderWidth: 1.6, pointRadius: 0 }] },
      options: { responsive: false, plugins: { legend: { display: false }, tooltip: { enabled: false } }, scales: { x: { display: false }, y: { display: false } } }
    });
  }
  sparkline('spark1', [12, 14, 13, 17, 18, 16, 21, 20, 22, 25, 28, 30], '#111114');
  sparkline('spark2', [21, 19, 22, 20, 24, 23, 26, 25, 28, 27, 30, 29], '#4b5159');
  sparkline('spark3', [40, 42, 45, 48, 46, 52, 55, 58, 62, 68, 72, 78], '#15803d');
  sparkline('spark4', [30, 28, 32, 29, 26, 25, 22, 20, 18, 16, 14, 13], '#dc2626');

  new Chart(document.getElementById('lineMain'), {
    type: 'line',
    data: {
      labels: ['4/19', '4/22', '4/25', '4/28', '5/1', '5/4', '5/7', '5/10', '5/13', '5/16', '5/18'],
      datasets: [
        { label: '신규가입', data: [120, 140, 135, 158, 170, 180, 210, 232, 260, 285, 302], borderColor: '#111114', backgroundColor: 'rgba(17,17,20,.06)', fill: true, tension: .35, borderWidth: 2, pointRadius: 0, pointHoverRadius: 4 },
        { label: '활성 전환', data: [80, 86, 90, 95, 100, 110, 118, 128, 140, 150, 162], borderColor: '#9aa0a6', borderDash: [4, 4], backgroundColor: 'transparent', fill: false, tension: .35, borderWidth: 1.8, pointRadius: 0 }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { mode: 'index', intersect: false, backgroundColor: '#111', padding: 10, cornerRadius: 8 } },
      scales: { x: { grid: noGrid, ticks: tickStyle }, y: { grid: gridLine, ticks: tickStyle, beginAtZero: true } }
    }
  });

  new Chart(document.getElementById('donut'), {
    type: 'doughnut',
    data: { labels: ['직접', '검색', 'SNS', '추천'], datasets: [{ data: [38, 27, 21, 14], backgroundColor: ['#111114', '#4b5159', '#8e939c', '#c7cbd1'], borderWidth: 0, hoverOffset: 6 }] },
    options: { responsive: true, maintainAspectRatio: false, cutout: '68%', plugins: { legend: { display: false }, tooltip: { backgroundColor: '#111', padding: 10, cornerRadius: 8 } } }
  });

  new Chart(document.getElementById('barCat'), {
    type: 'bar',
    data: {
      labels: ['Pro 월', 'Pro 연', 'Team 월', 'Team 연', 'Enterprise', '부가서비스'],
      datasets: [
        { label: '4월', data: [18, 22, 14, 28, 12, 8],  backgroundColor: '#dadce0', borderRadius: 6, barThickness: 18 },
        { label: '5월', data: [22, 28, 17, 34, 16, 11], backgroundColor: '#111114', borderRadius: 6, barThickness: 18 }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, boxHeight: 10, padding: 14 } }, tooltip: { backgroundColor: '#111', cornerRadius: 8 } },
      scales: { x: { grid: noGrid, ticks: tickStyle }, y: { grid: gridLine, ticks: tickStyle, beginAtZero: true } }
    }
  });

  const areaEl = document.getElementById('areaUsers');
  if (areaEl) {
    new Chart(areaEl, {
      type: 'line',
      data: {
        labels: ['월', '화', '수', '목', '금', '토', '일'],
        datasets: [
          { label: '주간',   data: [3200, 3800, 4100, 4500, 4400, 2900, 2400], borderColor: '#111114', backgroundColor: 'rgba(17,17,20,.10)', fill: true, tension: .4, borderWidth: 2, pointRadius: 0 },
          { label: '전주', data: [2900, 3500, 3700, 4200, 4000, 2700, 2200], borderColor: '#cdd1d6', backgroundColor: 'transparent', borderDash: [4, 4], tension: .4, borderWidth: 1.6, pointRadius: 0 }
        ]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { backgroundColor: '#111', cornerRadius: 8 } }, scales: { x: { grid: noGrid, ticks: tickStyle }, y: { grid: gridLine, ticks: tickStyle } } }
    });
  }

  const comboEl = document.getElementById('comboRev');
  if (comboEl) {
    new Chart(comboEl, {
      type: 'bar',
      data: {
        labels: ['11월', '12월', '1월', '2월', '3월', '4월', '5월'],
        datasets: [
          { type: 'bar',  label: '매출 (M)', data: [92, 108, 121, 118, 134, 128, 142], backgroundColor: '#111114', borderRadius: 6, barThickness: 24 },
          { type: 'line', label: '환불 (M)', data: [3, 4, 5, 4, 3, 5, 4], borderColor: '#dc2626', backgroundColor: '#dc26261f', tension: .4, fill: true, borderWidth: 2, pointRadius: 3 }
        ]
      },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, boxHeight: 10, padding: 14 } }, tooltip: { backgroundColor: '#111', cornerRadius: 8 } }, scales: { x: { grid: noGrid, ticks: tickStyle }, y: { grid: gridLine, ticks: tickStyle, beginAtZero: true } } }
    });
  }

  const payBar = document.getElementById('payBar');
  if (payBar) {
    new Chart(payBar, {
      type: 'bar',
      data: { labels: ['5/5', '5/6', '5/7', '5/8', '5/9', '5/10', '5/11', '5/12', '5/13', '5/14', '5/15', '5/16', '5/17', '5/18'], datasets: [{ data: [12, 18, 14, 22, 17, 28, 32, 26, 30, 24, 29, 33, 40, 38], backgroundColor: '#111114', borderRadius: 5, barThickness: 14 }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { backgroundColor: '#111', cornerRadius: 8 } }, scales: { x: { grid: noGrid, ticks: tickStyle }, y: { grid: gridLine, ticks: tickStyle, beginAtZero: true } } }
    });
  }

  const payPie = document.getElementById('payPie');
  if (payPie) {
    new Chart(payPie, {
      type: 'doughnut',
      data: { labels: ['카드', '계좌이체', '카카오페이', '네이버페이', '세금계산서'], datasets: [{ data: [52, 18, 14, 10, 6], backgroundColor: ['#111114', '#4b5159', '#8e939c', '#c7cbd1', '#dee0e4'], borderWidth: 0, hoverOffset: 6 }] },
      options: { responsive: true, maintainAspectRatio: false, cutout: '62%', plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, boxHeight: 10, padding: 14 } }, tooltip: { backgroundColor: '#111', cornerRadius: 8 } } }
    });
  }
}

/* ── 모달 ─────────────────────────────────────────────────── */
const MODAL_FORMS = {
  'add-user': {
    title: '회원 추가',
    body: `
      <div class="fg-row">
        <div class="fg"><label>이름</label><input class="form-control" placeholder="홍길동"></div>
        <div class="fg"><label>이메일</label><input class="form-control" placeholder="user@company.io" type="email"></div>
      </div>
      <div class="fg-row">
        <div class="fg"><label>플랜</label><select class="form-select"><option>Free</option><option>Pro</option><option>Team</option></select></div>
        <div class="fg"><label>역할</label><select class="form-select"><option>멤버</option><option>에디터</option><option>관리자</option></select></div>
      </div>
      <div class="fg"><label>메모</label><textarea class="form-control" placeholder="관리자만 볼 수 있는 메모"></textarea></div>
      <div class="fg"><div class="form-check form-switch"><input class="form-check-input" type="checkbox" id="aw" checked><label class="form-check-label ms-2" for="aw" style="font-size:13.5px;">초대 이메일 자동 발송</label></div></div>
    `
  },
  'add-content': {
    title: '새 게시물 작성',
    body: `
      <div class="fg"><label>제목</label><input class="form-control" placeholder="게시물 제목"></div>
      <div class="fg-row">
        <div class="fg"><label>카테고리</label><select class="form-select"><option>공지</option><option>가이드</option><option>업데이트</option><option>정책</option><option>리포트</option></select></div>
        <div class="fg"><label>상태</label><select class="form-select"><option>임시저장</option><option>발행</option><option>예약 발행</option></select></div>
      </div>
      <div class="fg"><label>본문</label><textarea class="form-control" placeholder="마크다운 또는 일반 텍스트로 입력" style="min-height:160px;"></textarea></div>
      <div class="fg"><label>태그</label><input class="form-control" placeholder="쉼표로 구분 · 예: 운영, 점검"></div>
    `
  },
  'add-notice': {
    title: '새 공지 작성',
    body: `
      <div class="fg"><label>제목</label><input class="form-control" placeholder="공지 제목"></div>
      <div class="fg-row">
        <div class="fg"><label>유형</label><select class="form-select"><option>상단 고정</option><option>팝업</option><option>배너</option></select></div>
        <div class="fg"><label>노출 대상</label><select class="form-select"><option>전체 회원</option><option>Pro 이상</option><option>Team 이상</option></select></div>
      </div>
      <div class="fg-row">
        <div class="fg"><label>시작일</label><input class="form-control" type="date" value="2026-05-22"></div>
        <div class="fg"><label>종료일</label><input class="form-control" type="date" value="2026-06-05"></div>
      </div>
      <div class="fg"><label>본문</label><textarea class="form-control" placeholder="공지 내용을 입력하세요"></textarea></div>
    `
  },
  'add-order': {
    title: '수동 결제 생성',
    body: `
      <div class="fg"><label>회원 검색</label><input class="form-control" placeholder="이름 또는 이메일"></div>
      <div class="fg-row">
        <div class="fg"><label>플랜</label><select class="form-select"><option>Pro 월</option><option>Pro 연</option><option>Team 월</option><option>Team 연</option></select></div>
        <div class="fg"><label>금액 (₩)</label><input class="form-control" type="number" placeholder="240000"></div>
      </div>
      <div class="fg-row">
        <div class="fg"><label>결제 수단</label><select class="form-select"><option>카드</option><option>계좌이체</option><option>세금계산서</option></select></div>
        <div class="fg"><label>결제일</label><input class="form-control" type="date" value="2026-05-22"></div>
      </div>
      <div class="fg"><label>메모</label><textarea class="form-control" placeholder="결제 내역에 함께 기록될 메모"></textarea></div>
    `
  },
  'add-report': {
    title: '새 보고서 만들기',
    body: `
      <div class="fg"><label>보고서 이름</label><input class="form-control" placeholder="2026년 5월 운영 리포트"></div>
      <div class="fg-row">
        <div class="fg"><label>기간 시작</label><input class="form-control" type="date" value="2026-05-01"></div>
        <div class="fg"><label>기간 종료</label><input class="form-control" type="date" value="2026-05-31"></div>
      </div>
      <div class="fg"><label>포함 지표</label>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:13.5px;">
          <label><input type="checkbox" class="form-check-input me-2" checked>가입 추이</label>
          <label><input type="checkbox" class="form-check-input me-2" checked>매출</label>
          <label><input type="checkbox" class="form-check-input me-2" checked>활성 사용자</label>
          <label><input type="checkbox" class="form-check-input me-2">전환 퍼널</label>
          <label><input type="checkbox" class="form-check-input me-2">신고·정지</label>
          <label><input type="checkbox" class="form-check-input me-2">기기·지역</label>
        </div>
      </div>
      <div class="fg"><label>형식</label><select class="form-select"><option>PDF</option><option>CSV</option><option>웹 페이지</option></select></div>
    `
  }
};

function openModal(id) {
  const el = document.getElementById('modal-' + id);
  if (el) { el.classList.add('show'); document.body.style.overflow = 'hidden'; }
}
function closeModal(el) {
  el.classList.remove('show');
  if (!document.querySelector('.modal-bd.show')) document.body.style.overflow = '';
}
function openAddModal(kind) {
  const data = MODAL_FORMS[kind];
  if (!data) return;
  document.getElementById('addTitle').textContent = data.title;
  document.getElementById('addBody').innerHTML    = data.body;
  openModal('add');
}

document.addEventListener('click', e => {
  const trigger = e.target.closest('[data-open-modal]');
  if (trigger) {
    const key = trigger.dataset.openModal;
    if (key === 'settings') openModal('settings');
    else openAddModal(key);
    e.preventDefault();
    return;
  }
  if (e.target.closest('[data-close-modal]')) {
    const m = e.target.closest('.modal-bd');
    if (m) closeModal(m);
    return;
  }
  if (e.target.classList.contains('modal-bd')) closeModal(e.target);
});

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') document.querySelectorAll('.modal-bd.show').forEach(closeModal);
});

/* ── 설정 모달 탭 ─────────────────────────────────────────── */
document.querySelectorAll('.modal-settings .ms-item').forEach(item => {
  item.addEventListener('click', () => {
    document.querySelectorAll('.modal-settings .ms-item').forEach(i => i.classList.remove('active'));
    item.classList.add('active');
    const target = item.dataset.ms;
    document.querySelectorAll('.modal-settings .ms-pane').forEach(p => {
      p.style.display = (p.dataset.pane === target) ? '' : 'none';
    });
  });
});

/* 다크 스위치 동기화 */
const msDark = document.getElementById('msDarkSwitch');
function syncMsDark() {
  if (msDark) msDark.checked = document.documentElement.getAttribute('data-theme') === 'dark';
}
syncMsDark();
msDark?.addEventListener('change', () => {
  if (typeof setAdminTheme === 'function') setAdminTheme(msDark.checked ? 'dark' : 'light');
});
