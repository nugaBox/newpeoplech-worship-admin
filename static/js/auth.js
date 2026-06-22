/** 로그아웃 */

document.getElementById("btn-logout")?.addEventListener("click", async () => {
  if (!confirm("로그아웃 하시겠습니까?")) return;
  try {
    await fetch("/api/auth/logout", { method: "POST" });
  } catch {}
  location.href = "/login";
});
