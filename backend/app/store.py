"""
Загрузка банков фраз из ``data/*.txt`` и выборка по темам.

Формат строки:  ``тема1,тема2 | фраза``  (для банка «kto»: ``темы | род | фраза``).
Пустые строки и строки, начинающиеся с ``#``, пропускаются.
Всё читается один раз при первом обращении и дальше живёт в памяти.

У каждой фразы есть ``key`` — короткий хеш текста. По нему фраза находится
в коде ссылки на сказку, поэтому ключ не меняется, когда в банк дописывают
новые строки. Изменили текст фразы — старые ссылки с ней перестанут открываться.
"""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .catalog import ADULT_TAG, ANY_THEME, BANK_IDS, GENDERED_BANKS, SLOTS_BY_ID, THEMES_BY_ID

DATA_DIR = Path(__file__).parent / "data"
GENDERS = ("m", "f", "n", "p")
KEY_BYTES = 3


class BankFormatError(ValueError):
    pass


@dataclass(frozen=True)
class Entry:
    text: str
    themes: frozenset[str]
    gender: str | None = None
    adult: bool = False

    @property
    def key(self) -> bytes:
        return phrase_key(self.text)


def phrase_key(text: str) -> bytes:
    return hashlib.sha1(text.casefold().encode("utf-8")).digest()[:KEY_BYTES]


def upper_first(s: str) -> str:
    return s[:1].upper() + s[1:]


def _parse_line(bank_id: str, raw: str, where: str) -> Entry:
    has_gender = bank_id in GENDERED_BANKS
    parts = [p.strip() for p in raw.split("|")]
    expected = 3 if has_gender else 2
    if len(parts) != expected or not all(parts):
        raise BankFormatError(f"{where}: ожидалось {expected} поля через «|»: {raw!r}")
    tags = frozenset(t for t in (x.strip() for x in parts[0].split(",")) if t)
    themes = tags - {ADULT_TAG}
    unknown = themes - set(THEMES_BY_ID) - {ANY_THEME}
    if not themes or unknown:
        raise BankFormatError(f"{where}: неизвестная тема {sorted(unknown) or '(пусто)'}: {raw!r}")
    gender = None
    if has_gender:
        gender = parts[1]
        if gender not in GENDERS:
            raise BankFormatError(f"{where}: род должен быть одним из {GENDERS}: {raw!r}")
    return Entry(text=parts[-1], themes=themes, gender=gender, adult=ADULT_TAG in tags)


@lru_cache(maxsize=1)
def load_all() -> dict[str, tuple[Entry, ...]]:
    """bank_id -> фразы банка."""
    banks: dict[str, tuple[Entry, ...]] = {}
    for bank_id in BANK_IDS:
        path = DATA_DIR / f"{bank_id}.txt"
        entries: list[Entry] = []
        with path.open(encoding="utf-8") as f:
            for n, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                entries.append(_parse_line(bank_id, line, f"{path.name}:{n}"))
        keys = {}
        for e in entries:
            if e.key in keys and keys[e.key] != e.text.casefold():
                raise BankFormatError(f"{path.name}: у фраз «{keys[e.key]}» и «{e.text}» совпал ключ")
            keys[e.key] = e.text.casefold()
        banks[bank_id] = tuple(entries)
    return banks


def bank_of(slot_id: str) -> tuple[Entry, ...]:
    return load_all()[SLOTS_BY_ID[slot_id].bank_id]


@lru_cache(maxsize=1)
def _text_index() -> dict[str, dict[str, Entry]]:
    return {bid: {e.text.casefold(): e for e in entries} for bid, entries in load_all().items()}


@lru_cache(maxsize=1)
def _key_index() -> dict[str, dict[bytes, Entry]]:
    return {bid: {e.key: e for e in entries} for bid, entries in load_all().items()}


def find(slot_id: str, text: str) -> Entry | None:
    return _text_index()[SLOTS_BY_ID[slot_id].bank_id].get(text.strip().casefold())


def find_by_key(slot_id: str, key: bytes) -> Entry | None:
    return _key_index()[SLOTS_BY_ID[slot_id].bank_id].get(key)


def pool(slot_id: str, theme_ids: list[str] | tuple[str, ...], kid: bool = False) -> list[Entry]:
    """Фразы слота для выбранных тем (универсальные включаются всегда).
    Без тем — весь банк. В детском режиме фразы с тегом adult пропускаются."""
    entries = bank_of(slot_id)
    if kid:
        entries = [e for e in entries if not e.adult]
    if not theme_ids:
        return list(entries)
    wanted = set(theme_ids) | {ANY_THEME}
    return [e for e in entries if e.themes & wanted]


def sample(
    slot_id: str,
    theme_ids: list[str],
    rng: random.Random | None = None,
    kid: bool = False,
    avoid: set[str] | None = None,
) -> Entry:
    rng = rng or random
    candidates = pool(slot_id, theme_ids, kid) or pool(slot_id, [], kid)
    if avoid:
        candidates = [e for e in candidates if e.text not in avoid] or candidates
    return rng.choice(candidates)


def stats() -> dict[str, dict[str, int]]:
    """slot_id -> {theme_id: сколько фраз доступно при выборе только этой темы}."""
    return {
        sid: {tid: len(pool(sid, [tid])) for tid in THEMES_BY_ID}
        for sid in SLOTS_BY_ID
    }


def total_phrases() -> int:
    return sum(len(v) for v in load_all().values())
