"""
FastAPI-приложение генератора сказок.

Эндпоинты:
    GET  /api/questions  — список из 20 вопросов вместе с банками слов
    POST /api/generate   — принимает ответы пользователя и возвращает готовую сказку

Запуск для разработки:
    uvicorn app.main:app --reload --port 8000
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .questions import get_questions_with_options
from .schemas import GenerateStoryRequest, GenerateStoryResponse, QuestionsResponse
from .story import StoryGenerationError, generate_story, random_answers

app = FastAPI(
    title="Генератор сказок",
    description="Собирает сказку из ответов на 20 вопросов, "
    "корректно склоняя слова из заранее заданных банков.",
    version="1.0.0",
)

# На время разработки разрешаем запросы с любого источника (React будет
# работать на отдельном порту, на http://localhost:5173).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/questions", response_model=QuestionsResponse)
def get_questions() -> QuestionsResponse:
    """Возвращает все 20 вопросов вместе с вариантами ответов (банками слов)."""
    return QuestionsResponse(questions=get_questions_with_options())


@app.post(
    "/api/generate",
    response_model=GenerateStoryResponse,
    responses={400: {"description": "Не хватает ответов или слово не из банка"}},
)
def generate(request: GenerateStoryRequest) -> GenerateStoryResponse:
    """Генерирует текст сказки по ответам пользователя."""
    try:
        story = generate_story(request.answers)
    except StoryGenerationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return GenerateStoryResponse(story=story)


@app.post("/api/generate/random", response_model=GenerateStoryResponse)
def generate_random() -> GenerateStoryResponse:
    """Генерирует сказку из случайно выбранных слов — без участия пользователя."""
    answers = random_answers()
    story = generate_story(answers)
    return GenerateStoryResponse(story=story)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}
