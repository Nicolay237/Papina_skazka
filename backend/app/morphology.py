
from __future__ import annotations

import pymorphy3

morph = pymorphy3.MorphAnalyzer()

VALID_CASES = {"nomn", "gent", "datv", "accs", "ablt", "loct"}


def _parse(word: str):
    parses = morph.parse(word.strip())
    for p in parses:
        if p.tag.case == "nomn" and p.tag.number == "sing":
            return p
    return parses[0]


def _match_letter_case(original: str, inflected: str) -> str:
    if original[:1].isupper():
        return inflected[:1].upper() + inflected[1:]
    return inflected


def get_gender_number(word: str) -> tuple[str, str]:
    p = _parse(word)
    gender = p.tag.gender or "masc"
    number = p.tag.number or "sing"
    return gender, number


def inflect_noun(word: str, case: str, number: str | None = None, force_animate: bool = False) -> str:
    if case not in VALID_CASES:
        raise ValueError(f"Неизвестный падеж: {case}")
    p = _parse(word)
    effective_case = case
    if force_animate and case == "accs":
        gender = p.tag.gender or "masc"
        if gender == "masc" or number == "plur":
            effective_case = "gent"
    grammemes = {effective_case}
    if number:
        grammemes.add(number)
    result = p.inflect(grammemes)
    inflected = result.word if result is not None else p.word
    return _match_letter_case(word, inflected)


def inflect_adjective(word: str, case: str, gender: str = "masc", number: str = "sing") -> str:
    """Склоняет прилагательное так, чтобы оно согласовалось по роду/числу/падежу."""
    if case not in VALID_CASES:
        raise ValueError(f"Неизвестный падеж: {case}")
    p = _parse(word)
    if number == "plur":
        grammemes = {case, "plur"}
    else:
        grammemes = {case, "sing", gender}
    result = p.inflect(grammemes)
    inflected = result.word if result is not None else p.word
    return _match_letter_case(word, inflected)


def inflect_verb_past(word: str, gender: str = "masc", number: str = "sing") -> str:
    """Ставит глагол в прошедшее время, согласуя его с родом/числом подлежащего."""
    p = _parse(word)
    if number == "plur":
        grammemes = {"past", "plur"}
    else:
        grammemes = {"past", "sing", gender}
    result = p.inflect(grammemes)
    inflected = result.word if result is not None else p.word
    return _match_letter_case(word, inflected)
