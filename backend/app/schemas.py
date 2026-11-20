from __future__ import annotations

from pydantic import BaseModel, Field


class ThemeOut(BaseModel):
    id: str
    name: str
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
    slots: list[SlotOut] = Field(description="Части сказки в порядке сюжета")
    chepukha_slots: list[str] = Field(description="Вопросы игры «Чепуха» по порядку")
    max_chapters: int


class OptionOut(BaseModel):
    text: str = Field(description="Фраза в том виде, в каком она отправляется обратно в answers")
    label: str = Field(description="Та же фраза для плитки (с заглавной буквы)")


class OptionsRequest(BaseModel):
    slot: str = Field(max_length=40)
    themes: list[str] = Field(default_factory=list, max_length=20)
    kid: bool = Field(default=False, description="Детский режим: без фраз с пометкой adult")
    limit: int = Field(default=12, ge=1, le=40)
    exclude: list[str] = Field(default_factory=list, max_length=200)


class OptionsResponse(BaseModel):
    slot: str
    options: list[OptionOut]
    total: int


class StoryRequest(BaseModel):
    themes: list[str] = Field(default_factory=list, max_length=20)
    kid: bool = False
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


class ContinueRequest(BaseModel):
    code: str = Field(max_length=400)
    themes: list[str] = Field(default_factory=list, max_length=20)
    kid: bool = False
    include: list[str] | None = Field(default=None, max_length=20)


class PickOut(BaseModel):
    chapter: int
    slot: str
    title: str
    text: str
    label: str


class StoryResponse(BaseModel):
    code: str = Field(description="Код для ссылки /s/{code}")
    story: str
    chapters: list[list[str]] = Field(description="Абзацы по главам")
    picks: list[PickOut]
    can_continue: bool
