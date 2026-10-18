from __future__ import annotations

from pydantic import BaseModel, Field


class ThemeOut(BaseModel):
    id: str
    name: str
    icon: str = Field(description="Имя иконки Material Symbols")
    description: str
    size: int = Field(description="Сколько фраз доступно, если выбрана только эта тема")


class GroupOut(BaseModel):
    id: str
    title: str


class SlotOut(BaseModel):
    id: str
    title: str
    question: str
    group: str
    required: bool


class MetaResponse(BaseModel):
    total: int = Field(description="Сколько всего фраз в копилке")
    themes: list[ThemeOut]
    groups: list[GroupOut]
    slots: list[SlotOut]


class OptionOut(BaseModel):
    text: str = Field(description="Фраза в том виде, в каком она отправляется обратно в answers")
    label: str = Field(description="Та же фраза для плитки (с заглавной буквы)")


class OptionsRequest(BaseModel):
    slot: str = Field(max_length=40)
    themes: list[str] = Field(default_factory=list, max_length=20)
    limit: int = Field(default=12, ge=1, le=40)
    exclude: list[str] = Field(default_factory=list, max_length=200)


class OptionsResponse(BaseModel):
    slot: str
    options: list[OptionOut]
    total: int


class StoryRequest(BaseModel):
    themes: list[str] = Field(default_factory=list, max_length=20)
    include: list[str] | None = Field(
        default=None,
        max_length=20,
        description="Какие части сказки включить. Не указано — все. "
        "Обязательные части (герой, занятие) включаются всегда.",
    )
    answers: dict[str, str] = Field(
        default_factory=dict,
        max_length=20,
        description="Выбранные вручную фразы {slot_id: text}. Остальное выпадет случайно.",
    )


class PickOut(BaseModel):
    slot: str
    title: str
    text: str
    label: str


class StoryResponse(BaseModel):
    story: str
    paragraphs: list[str]
    picks: list[PickOut]
