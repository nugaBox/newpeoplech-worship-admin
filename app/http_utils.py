"""HTTP 요청·역방향 프록시 관련 유틸."""

from __future__ import annotations

from fastapi import Request


def resolve_public_url(
    request: Request | None,
    bind_host: str,
    port: int,
    configured_public_url: str = "",
) -> str:
    """브라우저에서 보이는 접속 URL을 반환한다."""
    if configured_public_url.strip():
        return configured_public_url.rstrip("/")

    if request is not None:
        forwarded_host = request.headers.get("x-forwarded-host")
        host_header = forwarded_host or request.headers.get("host")
        if host_header:
            local_hosts = {bind_host, "127.0.0.1", "localhost", "::1"}
            local_with_port = {f"{h}:{port}" for h in local_hosts}
            if host_header not in local_hosts and host_header not in local_with_port:
                scheme = request.headers.get("x-forwarded-proto") or request.url.scheme
                return f"{scheme}://{host_header}"

    display_host = "127.0.0.1" if bind_host in ("0.0.0.0", "::") else bind_host
    return f"http://{display_host}:{port}"
