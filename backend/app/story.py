"""
Сборка сказки из выбранных фраз.

Фразы в банках хранятся в «серединном» виде (строчная буква, предлоги и падежи
уже внутри), поэтому склонять ничего не нужно. Единственное согласование —
глаголы с героем по роду и числу: «Колобок познакомился», «Три поросёнка
познакомились». Род и число героя задаются в банке ``kto``.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from .catalog import SLOTS, SLOTS_BY_ID, THEMES_BY_ID
from .store import Entry, find, pool, sample, upper_first

# формы по роду: m, f, n, p
_ACQUAINTED = {"m": "познакомился", "f": "познакомилась", "n": "познакомилось", "p": "познакомились"}
_FOUND_SELF = {"m": "оказался", "f": "оказалась", "n": "оказалось", "p": "оказались"}
_SET_OFF = {"m": "отправился", "f": "отправилась", "n": "отправилось", "p": "отправились"}
_PRONOUN = {"m": "он", "f": "она", "n": "оно", "p": "они"}

# Вводные для второго предложения: «принялись / стали / решили ... + инфинитив»
_STARTS = [
    {"m": "принялся", "f": "принялась", "n": "принялось", "p": "принялись"},
    {"m": "стал", "f": "стала", "n": "стало", "p": "стали"},
    {"m": "решил", "f": "решила", "n": "решило", "p": "решили"},
    {"m": "не придумал ничего лучше, чем", "f": "не придумала ничего лучше, чем",
     "n": "не придумало ничего лучше, чем", "p": "не придумали ничего лучше, чем"},
]
_LEADS_WITH_PLACE = ["Там", "Там", "И там"]
_LEADS_NO_PLACE = ["Тогда", "Потом", "А потом"]
_SAID_INTROS = [
    "Люди говорили:", "Люди говорили:", "Все вокруг твердили:",
    "Прохожие шептались:", "Соседи говорили:", "А люди вокруг восклицали:",
]
_ENDINGS = [
    "Дело кончилось тем, что", "Дело кончилось тем, что", "Дело кончилось тем, что",
    "А закончилось всё тем, что", "В итоге", "В конце концов",
]


class StoryError(ValueError):
    pass


@dataclass(frozen=True)
class Story:
    paragraphs: list[str]
    picks: dict[str, Entry]

    @property
    def text(self) -> str:
        return "\n\n".join(self.paragraphs)


def _end(s: str) -> str:
    s = s.rstrip()
    return s if s and s[-1] in ".!?…" else s + "."


def _check_themes(themes: list[str]) -> None:
    unknown = [t for t in themes if t not in THEMES_BY_ID]
    if unknown:
        raise StoryError(f"Неизвестная тема: {', '.join(unknown)}")


def resolve_picks(
    themes: list[str],
    answers: dict[str, str],
    include: list[str] | None,
    rng: random.Random,
) -> dict[str, Entry]:
    """Определяет, какие части участвуют в сказке и какая фраза в каждой."""
    _check_themes(themes)
    unknown_slots = [s for s in (list(answers) + list(include or [])) if s not in SLOTS_BY_ID]
    if unknown_slots:
        raise StoryError(f"Неизвестная часть сказки: {', '.join(unknown_slots)}")

    wanted = set(answers) | (set(include) if include is not None else {s.id for s in SLOTS})
    picks: dict[str, Entry] = {}
    for slot in SLOTS:
        if slot.id not in wanted and not slot.required:
            continue
        if slot.id in answers:
            entry = find(slot.id, answers[slot.id])
            if entry is None:
                raise StoryError(f"Фразы «{answers[slot.id]}» нет в банке «{slot.title}»")
        else:
            entry = sample(slot.id, themes, rng)
        picks[slot.id] = entry
    return picks


def compose(picks: dict[str, Entry], rng: random.Random) -> Story:
    hero = picks["kto"]
    g = hero.gender or "m"
    companion = picks.get("s_kem")
    place = picks.get("gde")
    when = picks.get("kogda")
    doing = picks["chto_delali"]

    # 1. Знакомство / завязка
    if companion:
        first = f"{hero.text} {_ACQUAINTED[g]} {companion.text}"
        if place:
            first += f" {place.text}"
    elif place:
        first = f"{hero.text} {_FOUND_SELF[g]} {place.text}"
    else:
        first = f"{hero.text} {_SET_OFF[g]} навстречу приключениям"
    if when:
        first += f", {when.text}"
    paragraphs = [_end(upper_first(first))]

    # 2. Чем занялись
    who = "они" if companion else _PRONOUN[g]
    form = "p" if companion else g
    lead = rng.choice(_LEADS_WITH_PLACE if place else _LEADS_NO_PLACE)
    verb = rng.choice(_STARTS)[form]
    paragraphs.append(_end(f"{lead} {who} {verb} {doing.text}"))

    # 3. Что сказали люди
    said = picks.get("lyudi_skazali")
    if said:
        inner = said.text.replace("«", "„").replace("»", "“")  # кавычки внутри реплики — «лапки»
        paragraphs.append(f"{rng.choice(_SAID_INTROS)} «{inner}»")

    # 4. Чем всё кончилось
    ending = picks.get("delo_konchilos")
    if ending:
        paragraphs.append(_end(f"{rng.choice(_ENDINGS)} {ending.text}"))

    return Story(paragraphs=paragraphs, picks=picks)


def generate(
    themes: list[str] | None = None,
    answers: dict[str, str] | None = None,
    include: list[str] | None = None,
    rng: random.Random | None = None,
) -> Story:
    rng = rng or random.Random()
    picks = resolve_picks(themes or [], answers or {}, include, rng)
    return compose(picks, rng)


def options(
    slot_id: str,
    themes: list[str],
    limit: int = 12,
    exclude: list[str] | None = None,
    rng: random.Random | None = None,
) -> tuple[list[Entry], int]:
    """Случайная выборка вариантов для экрана выбора. Возвращает (варианты, всего в подборке)."""
    if slot_id not in SLOTS_BY_ID:
        raise StoryError(f"Неизвестная часть сказки: {slot_id}")
    _check_themes(themes)
    rng = rng or random.Random()
    entries = pool(slot_id, themes)
    skip = {e.casefold() for e in (exclude or [])}
    fresh = [e for e in entries if e.text.casefold() not in skip]
    source = fresh if len(fresh) >= min(limit, len(entries)) else entries
    return rng.sample(source, min(limit, len(source))), len(entries)
