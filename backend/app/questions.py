"""
Описание 7 категорий фраз игры «Чепуха», из которых строится сказка.

Каждая категория — это банк ГОТОВЫХ
ФРАЗ (а не отдельных слов). Фразы уже содержат нужные предлоги и падежи
(«с Дикобразом», «у Замка Графа Дракулы»), поэтому никакого морфологического
склонения не требуется — генератор просто выбирает и склеивает фразы.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

BANKS_DIR = Path(__file__).parent / "word_banks"


@dataclass(frozen=True)
class Question:
    id: str
    text: str
    bank_file: str


QUESTIONS: list[Question] = [
    Question("kto", "Кто?", "kto.json"),
    Question("s_kem", "С кем?", "s_kem.json"),
    Question("gde", "Где?", "gde.json"),
    Question("kogda", "Когда?", "kogda.json"),
    Question("chto_delali", "Что делали?", "chto_delali.json"),
    Question("lyudi_skazali", "Люди сказали?", "lyudi_skazali.json"),
    Question("delo_konchilos", "Дело кончилось тем, что...?", "delo_konchilos.json"),
]

QUESTIONS_BY_ID: dict[str, Question] = {q.id: q for q in QUESTIONS}


def load_bank(bank_file: str) -> list[str]:
    path = BANKS_DIR / bank_file
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def get_questions_with_options() -> list[dict]:
    """Вопросы вместе со словами банка — то, что отдаём фронтенду."""
    return [
        {"id": q.id, "text": q.text, "options": load_bank(q.bank_file)}
        for q in QUESTIONS
    ]
