"""
FastAPI-приложение «Папина сказка».

    GET  /api/meta             — темы и части сказки
    POST /api/options          — случайные варианты для выбора вручную
    POST /api/story            — собрать сказку (всё случайно или с ручным выбором)
    GET  /api/story/{code}     — открыть сказку по коду из ссылки
    POST /api/story/continue   — дописать следующую главу
    GET  /api/health

Запуск для разработки:  uvicorn app.main:app --reload --port 8000
В проде, если рядом лежит собранный фронтенд (frontend/dist), он отдаётся с того же адреса,
а для ссылок /s/{code} в страницу подставляется превью для мессенджеров.
"""
from __future__ import annotations

import html
import os
import re
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from . import store
from .catalog import CHEPUKHA_SLOTS, GROUPS, SLOTS_BY_ID, SLOTS_UI, THEMES
from .schemas import (
    ContinueRequest, GroupOut, MetaResponse, OptionOut, OptionsRequest, OptionsResponse,
    PickOut, SlotOut, StoryRequest, StoryResponse, ThemeOut,
)
from .store import upper_first
from .story import MAX_CHAPTERS, Story, StoryError, continue_story, decode, generate, options, ordered_picks


@asynccontextmanager
async def lifespan(_: FastAPI):
    store.load_all()  # ошибка в банке должна ронять запуск, а не первый запрос
    yield


app = FastAPI(title="Папина сказка", version="3.0.0", lifespan=lifespan)

# CORS нужен только если фронтенд живёт на другом адресе (dev-сервер Vite).
# В проде укажите ALLOWED_ORIGINS=https://ваш-домен (через запятую, если несколько).
_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins.split(",") if o.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def _bad_request(exc: StoryError) -> HTTPException:
    return HTTPException(status_code=400, detail=str(exc))


def _story_response(story: Story) -> StoryResponse:
    return StoryResponse(
        code=story.code,
        story=story.text,
        chapters=story.paragraphs,
        picks=[
            PickOut(chapter=i + 1, slot=sid, title=SLOTS_BY_ID[sid].title, text=e.text, label=upper_first(e.text))
            for i, sid, e in ordered_picks(story)
        ],
        can_continue=len(story.chapters) < MAX_CHAPTERS,
    )


@app.get("/api/meta", response_model=MetaResponse)
def meta() -> MetaResponse:
    sizes = store.stats()
    return MetaResponse(
        total=store.total_phrases(),
        themes=[
            ThemeOut(id=t.id, name=t.name, description=t.description, size=sum(sizes[sid][t.id] for sid in sizes))
            for t in THEMES
        ],
        groups=[GroupOut(id=g.id, title=g.title) for g in GROUPS],
        slots=[
            SlotOut(id=s.id, title=s.title, question=s.question, group=s.group, required=s.required)
            for s in SLOTS_UI
        ],
        chepukha_slots=CHEPUKHA_SLOTS,
        max_chapters=MAX_CHAPTERS,
    )


@app.post("/api/options", response_model=OptionsResponse)
def get_options(req: OptionsRequest) -> OptionsResponse:
    try:
        entries, total = options(req.slot, req.themes, req.limit, req.exclude, kid=req.kid)
    except StoryError as exc:
        raise _bad_request(exc) from exc
    return OptionsResponse(
        slot=req.slot,
        options=[OptionOut(text=e.text, label=upper_first(e.text)) for e in entries],
        total=total,
    )


@app.post("/api/story", response_model=StoryResponse)
def make_story(req: StoryRequest) -> StoryResponse:
    try:
        return _story_response(generate(req.themes, req.answers, req.include, kid=req.kid))
    except StoryError as exc:
        raise _bad_request(exc) from exc


@app.post("/api/story/continue", response_model=StoryResponse)
def continue_(req: ContinueRequest) -> StoryResponse:
    try:
        story = decode(req.code)
        return _story_response(continue_story(story, req.themes, req.include, kid=req.kid))
    except StoryError as exc:
        raise _bad_request(exc) from exc


@app.get("/api/story/{code}", response_model=StoryResponse)
def open_story(code: str) -> StoryResponse:
    try:
        return _story_response(decode(code))
    except StoryError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


# --- раздача собранного фронтенда (необязательно) ---
_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
_DEFAULT_PREVIEW = re.compile(r'\s*<meta (?:property="og:description"|name="description")[^>]*>')


def _page_with_preview(code: str) -> HTMLResponse:
    """index.html с превью конкретной сказки: мессенджеры читают og-теги и не выполняют JS."""
    page = (_DIST / "index.html").read_text(encoding="utf-8")
    try:
        story = decode(code)
    except StoryError:
        return HTMLResponse(page)
    first = story.paragraphs[0][0]
    description = html.escape(first if len(first) <= 200 else first[:197].rstrip() + "…", quote=True)
    tags = (
        f'    <meta property="og:description" content="{description}" />\n'
        f'    <meta name="description" content="{description}" />\n'
    )
    page = _DEFAULT_PREVIEW.sub("", page)  # общее описание заменяется описанием этой сказки
    return HTMLResponse(page.replace("</head>", f"{tags}  </head>", 1))


if _DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=_DIST / "assets"), name="assets")

    @app.get("/s/{code}", include_in_schema=False)
    def shared(code: str) -> HTMLResponse:
        return _page_with_preview(code)

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str) -> FileResponse:
        candidate = (_DIST / path).resolve()
        if path and candidate.is_file() and _DIST in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(_DIST / "index.html")
