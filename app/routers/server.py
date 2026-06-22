"""서버 상태·재시작 API."""

from pydantic import BaseModel

from fastapi import APIRouter, Request

from app.server_control import get_status_payload, schedule_restart, schedule_stop

router = APIRouter(prefix="/api/server", tags=["server"])


class ServerStatusResponse(BaseModel):
    status: str
    uptime_seconds: int
    host: str
    port: int
    url: str
    run_mode: str
    mode_label: str
    reload_enabled: bool
    pid: int


class ServerRestartResponse(BaseModel):
    message: str


class ServerStopResponse(BaseModel):
    message: str


@router.get("/status", response_model=ServerStatusResponse)
async def server_status(request: Request) -> ServerStatusResponse:
    return ServerStatusResponse(**get_status_payload(request))


@router.post("/restart", response_model=ServerRestartResponse)
async def restart_server() -> ServerRestartResponse:
    schedule_restart()
    return ServerRestartResponse(
        message="서버를 재시작합니다. 5~10초 후 자동으로 다시 연결됩니다."
    )


@router.post("/stop", response_model=ServerStopResponse)
async def stop_server() -> ServerStopResponse:
    schedule_stop()
    return ServerStopResponse(
        message="서버를 중지합니다. 다시 사용하려면 터미널에서 python start.py 를 실행하세요."
    )
