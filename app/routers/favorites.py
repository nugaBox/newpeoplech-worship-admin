"""즐겨찾기 폴더·프로그램 API."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.engines.local_runner import open_path

router = APIRouter(prefix="/api/favorites", tags=["favorites"])

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "favorites.json"


class FavoriteItem(BaseModel):
    id: str
    type: Literal["folder", "file", "heading", "separator"]
    name: str
    path: str = ""
    category: Literal["folder", "file"] = "folder"


class FavoritesResponse(BaseModel):
    items: list[FavoriteItem]


class FavoriteItemCreate(BaseModel):
    type: Literal["folder", "file", "heading", "separator"] = "folder"
    name: str
    path: str = ""
    category: Literal["folder", "file"] = "folder"


class FavoriteItemUpdate(BaseModel):
    type: Literal["folder", "file", "heading", "separator"] | None = None
    name: str | None = None
    path: str | None = None
    category: Literal["folder", "file"] | None = None


class OpenPathRequest(BaseModel):
    path: str | None = None
    id: str | None = None


class ActionResult(BaseModel):
    success: bool
    message: str


def _normalize_item(item: dict) -> dict:
    """구분선·카테고리 없는 구 데이터 호환."""
    if item.get("type") == "separator":
        item = {**item, "type": "heading", "name": item.get("name") or "-"}
    if item.get("type") == "file":
        item.setdefault("category", "file")
    else:
        item.setdefault("category", "folder")
    return item


def _load() -> dict:
    if not DATA_FILE.is_file():
        return {"items": []}
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    data["items"] = [_normalize_item(item) for item in data.get("items", [])]
    return data


def _save(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


@router.get("", response_model=FavoritesResponse)
async def list_favorites() -> FavoritesResponse:
    data = _load()
    return FavoritesResponse(items=[FavoriteItem(**item) for item in data.get("items", [])])


@router.put("", response_model=FavoritesResponse)
async def replace_favorites(body: FavoritesResponse) -> FavoritesResponse:
    _save({"items": [item.model_dump() for item in body.items]})
    return body


@router.post("/items", response_model=FavoriteItem)
async def add_item(body: FavoriteItemCreate) -> FavoriteItem:
    data = _load()
    item = FavoriteItem(id=uuid.uuid4().hex[:8], **body.model_dump())
    data.setdefault("items", []).append(item.model_dump())
    _save(data)
    return item


@router.patch("/items/{item_id}", response_model=FavoriteItem)
async def update_item(item_id: str, body: FavoriteItemUpdate) -> FavoriteItem:
    data = _load()
    for item in data.get("items", []):
        if item["id"] == item_id:
            for key, val in body.model_dump(exclude_unset=True).items():
                item[key] = val
            _save(data)
            return FavoriteItem(**item)
    raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")


@router.delete("/items/{item_id}", response_model=ActionResult)
async def delete_item(item_id: str) -> ActionResult:
    data = _load()
    items = data.get("items", [])
    new_items = [i for i in items if i["id"] != item_id]
    if len(new_items) == len(items):
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")
    _save({"items": new_items})
    return ActionResult(success=True, message="삭제되었습니다.")


@router.post("/open", response_model=ActionResult)
async def open_favorite(body: OpenPathRequest) -> ActionResult:
    path_str = body.path
    if body.id:
        data = _load()
        match = next((i for i in data.get("items", []) if i["id"] == body.id), None)
        if not match:
            raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")
        if match["type"] in ("separator", "heading"):
            raise HTTPException(status_code=400, detail="소제목은 열 수 없습니다.")
        path_str = match["path"]

    if not path_str:
        raise HTTPException(status_code=400, detail="경로가 없습니다.")

    target = Path(path_str)
    try:
        open_path(target)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"열기 실패: {exc}") from exc

    label = "폴더" if target.is_dir() else "파일"
    return ActionResult(success=True, message=f"{label}을(를) 열었습니다: {target.name}")
