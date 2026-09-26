from __future__ import annotations

from pydantic import BaseModel, Field


class QuestionOut(BaseModel):
    id: str
    text: str
    options: list[str]


class QuestionsResponse(BaseModel):
    questions: list[QuestionOut]


class GenerateStoryRequest(BaseModel):
    answers: dict[str, str] = Field(
        ...,
        description="Словарь {id_вопроса: выбранное_слово}. Должны быть заполнены все 20 вопросов.",
    )


class GenerateStoryResponse(BaseModel):
    story: str


class ErrorResponse(BaseModel):
    detail: str
