"""
Сборка текста Чепухи из выбранных фраз.
"""
from __future__ import annotations

import random
import re

from .questions import QUESTIONS_BY_ID, load_bank

_LEADING_CHTO_RE = re.compile(r"^что\s+", flags=re.IGNORECASE)


class StoryGenerationError(ValueError):
    pass


def _lower_first(s: str) -> str:
    return s[0].lower() + s[1:] if s else s


def _upper_first(s: str) -> str:
    return s[0].upper() + s[1:] if s else s


def _strip_leading_chto(s: str) -> str:
    return _LEADING_CHTO_RE.sub("", s, count=1)


def _finish_sentence(s: str) -> str:
    s = s.rstrip()
    if s and s[-1] in ".!?":
        return s
    return s + "."


def validate_answers(answers: dict[str, str]) -> None:
    missing = [qid for qid in QUESTIONS_BY_ID if qid not in answers or not answers[qid]]
    if missing:
        raise StoryGenerationError(f"Не хватает ответов на вопросы: {', '.join(missing)}")

    for qid, question in QUESTIONS_BY_ID.items():
        bank = {w.lower() for w in load_bank(question.bank_file)}
        if answers[qid].strip().lower() not in bank:
            raise StoryGenerationError(
                f"Фраза «{answers[qid]}» не найдена в банке для вопроса «{question.text}»"
            )


def random_answers() -> dict[str, str]:
    return {qid: random.choice(load_bank(q.bank_file)) for qid, q in QUESTIONS_BY_ID.items()}


def generate_story(answers: dict[str, str]) -> str:
    validate_answers(answers)

    kto = answers["kto"]
    s_kem = answers["s_kem"]
    gde = _lower_first(answers["gde"])
    kogda = _lower_first(answers["kogda"])
    chto_delali = _lower_first(answers["chto_delali"])
    lyudi_skazali = answers["lyudi_skazali"]
    delo_konchilos = _lower_first(_strip_leading_chto(answers["delo_konchilos"]))

    part1 = f"{kto} познакомился {s_kem} {gde}, {kogda}"
    part2 = f"Там они {chto_delali}"
    part3 = f"Люди говорили: «{lyudi_skazali}»"
    part4 = f"Дело кончилось тем, что {delo_konchilos}"

    return "\n\n".join([
        _upper_first(_finish_sentence(part1)),
        _upper_first(_finish_sentence(part2)),
        part3,
        _upper_first(_finish_sentence(part4)),
    ])
