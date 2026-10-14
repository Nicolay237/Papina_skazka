"""
Загрузка банков фраз из ``data/*.txt`` и выборка по темам.

Формат строки:  ``тема1,тема2 | фраза``  (для слота «кто»: ``темы | род | фраза``).
Пустые строки и строки, начинающиеся с ``#``, пропускаются.
Всё читается один раз при первом обращении и дальше живёт в памяти.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .catalog import ANY_THEME, SLOTS, SLOTS_BY_ID, THEMES_BY_ID

DATA_DIR = Path(__file__).parent / "data"
GENDERS = ("m", "f", "n", "p")


class BankFormatError(ValueError):
    pass


@dataclass(frozen=True)
class Entry:
    text: str
    themes: frozenset[str]
    gender: str | None = None


def upper_first(s: str) -> str:
    return s[:1].upper() + s[1:]


def _parse_line(slot_id: str, raw: str, where: str) -> Entry:
    has_gender = SLOTS_BY_ID[slot_id].has_gender
    parts = [p.strip() for p in raw.split("|")]
    expected = 3 if has_gender else 2
    if len(parts) != expected or not all(parts):
        raise BankFormatError(f"{where}: ожидалось {expected} поля через «|»: {raw!r}")
    themes = frozenset(t for t in (x.strip() for x in parts[0].split(",")) if t)
    unknown = themes - set(THEMES_BY_ID) - {ANY_THEME}
    if not themes or unknown:
        raise BankFormatError(f"{where}: неизвестная тема {sorted(unknown) or '(пусто)'}: {raw!r}")
    gender = None
    if has_gender:
        gender = parts[1]
        if gender not in GENDERS:
            raise BankFormatError(f"{where}: род должен быть одним из {GENDERS}: {raw!r}")
    return Entry(text=parts[-1], themes=themes, gender=gender)


@lru_cache(maxsize=1)
def load_all() -> dict[str, tuple[Entry, ...]]:
    banks: dict[str, tuple[Entry, ...]] = {}
    for slot in SLOTS:
        path = DATA_DIR / f"{slot.id}.txt"
        entries: list[Entry] = []
        with path.open(encoding="utf-8") as f:
            for n, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                entries.append(_parse_line(slot.id, line, f"{path.name}:{n}"))
        banks[slot.id] = tuple(entries)
    return banks


@lru_cache(maxsize=1)
def _index() -> dict[str, dict[str, Entry]]:
    """slot_id -> {text в нижнем регистре: Entry} для проверки ответов."""
    return {sid: {e.text.casefold(): e for e in entries} for sid, entries in load_all().items()}


def find(slot_id: str, text: str) -> Entry | None:
    return _index()[slot_id].get(text.strip().casefold())


def pool(slot_id: str, theme_ids: list[str] | tuple[str, ...]) -> list[Entry]:
    """Фразы слота для выбранных тем (универсальные включаются всегда).
    Без тем — весь банк слота."""
    entries = load_all()[slot_id]
    if not theme_ids:
        return list(entries)
    wanted = set(theme_ids) | {ANY_THEME}
    return [e for e in entries if e.themes & wanted]


def sample(slot_id: str, theme_ids: list[str], rng: random.Random | None = None) -> Entry:
    rng = rng or random
    return rng.choice(pool(slot_id, theme_ids) or list(load_all()[slot_id]))


def stats() -> dict[str, dict[str, int]]:
    """slot_id -> {theme_id: сколько фраз доступно при выборе только этой темы}."""
    return {
        sid: {tid: len(pool(sid, [tid])) for tid in THEMES_BY_ID}
        for sid in load_all()
    }
