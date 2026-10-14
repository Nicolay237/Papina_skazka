"""
FastAPI-приложение «Папина сказка».

    GET  /api/meta     — темы и части сказки
    POST /api/options  — случайные варианты для выбора вручную
    POST /api/story    — собрать сказку (всё случайно или с ручным выбором)
    GET  /api/health

Запуск для разработки:  uvicorn app.main:app --reload --port 8000
В проде, если рядом лежит собранный фронтенд (frontend/dist), он отдаётся с того же адреса.
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import store
from .catalog import GROUPS, SLOTS, SLOTS_BY_ID, THEMES
from .schemas import (
    GroupOut, MetaResponse, OptionOut, OptionsRequest, OptionsResponse,
    PickOut, SlotOut, StoryRequest, StoryResponse, ThemeOut,
)
from .store import upper_first
from .story import StoryError, generate, options


@asynccontextmanager
async def lifespan(_: FastAPI):
    store.load_all()  # ошибка в банке должна ронять запуск, а не первый запрос
    yield


app = FastAPI(title="Папина сказка", version="2.0.0", lifespan=lifespan)

# CORS нужен только если фронтенд живёт на другом адресе (dev-сервер Vite).
# В проде укажите ALLOWED_ORIGINS=https://ваш-домен (через запятую, если несколько).
_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins.split(",") if o.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/api/meta", response_model=MetaResponse)
def meta() -> MetaResponse:
    sizes = store.stats()
    return MetaResponse(
        total=sum(len(v) for v in store.load_all().values()),
        themes=[
            ThemeOut(
                id=t.id, name=t.name, emoji=t.emoji, description=t.description,
                size=sum(sizes[sid][t.id] for sid in sizes),
            )
            for t in THEMES
        ],
        groups=[GroupOut(id=g.id, title=g.title) for g in GROUPS],
        slots=[
            SlotOut(id=s.id, title=s.title, question=s.question, group=s.group, required=s.required)
            for s in SLOTS
        ],
    )


@app.post("/api/options", response_model=OptionsResponse)
def get_options(req: OptionsRequest) -> OptionsResponse:
    try:
        entries, total = options(req.slot, req.themes, req.limit, req.exclude)
    except StoryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return OptionsResponse(
        slot=req.slot,
        options=[OptionOut(text=e.text, label=upper_first(e.text)) for e in entries],
        total=total,
    )


@app.post("/api/story", response_model=StoryResponse)
def make_story(req: StoryRequest) -> StoryResponse:
    try:
        result = generate(req.themes, req.answers, req.include)
    except StoryError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return StoryResponse(
        story=result.text,
        paragraphs=result.paragraphs,
        picks=[
            PickOut(slot=sid, title=SLOTS_BY_ID[sid].title, text=e.text, label=upper_first(e.text))
            for sid, e in result.picks.items()
        ],
    )


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


# --- раздача собранного фронтенда (необязательно) ---
_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if _DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=_DIST / "assets"), name="assets")

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str) -> FileResponse:
        candidate = (_DIST / path).resolve()
        if path and candidate.is_file() and _DIST in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(_DIST / "index.html")
