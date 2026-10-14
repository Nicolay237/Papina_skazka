"""
Проверка банков фраз перед выкладкой.

    python scripts/check_bank.py            # структура + орфография
    python scripts/check_bank.py --no-spell # только структура

Орфография: слова, которых нет в словаре pymorphy3, выводятся списком.
Это не ошибки, а кандидаты на просмотр глазами (имена и сленг тоже попадут).
Слова, проверенные вручную, добавляйте в scripts/known_words.txt.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import store  # noqa: E402
from app.catalog import SLOTS, THEMES  # noqa: E402

WORD_RE = re.compile(r"[A-Za-zА-Яа-яЁё]+(?:[-'’][A-Za-zА-Яа-яЁё]+)*")
LATIN_RE = re.compile(r"[A-Za-z]")
CYRILLIC_RE = re.compile(r"[А-Яа-яЁё]")
MIN_PER_THEME = 12


def structural_errors() -> list[str]:
    errors: list[str] = []
    banks = store.load_all()
    for slot in SLOTS:
        seen: Counter[str] = Counter(e.text.casefold() for e in banks[slot.id])
        for e in banks[slot.id]:
            t = e.text
            where = f"{slot.id}: «{t}»"
            if seen[t.casefold()] > 1:
                errors.append(f"{where} — дубликат")
                seen[t.casefold()] = 0
            if "  " in t or t != t.strip():
                errors.append(f"{where} — лишние пробелы")
            for w in WORD_RE.findall(t):
                if LATIN_RE.search(w) and CYRILLIC_RE.search(w):
                    errors.append(f"{where} — латиница вперемешку с кириллицей: {w}")
            if slot.id in ("gde", "kogda", "chto_delali", "s_kem") and t[0].isupper():
                errors.append(f"{where} — должна начинаться со строчной")
            if slot.id == "s_kem" and not re.match(r"со? ", t):
                errors.append(f"{where} — должна начинаться с «с»/«со»")
            if slot.id in ("kto", "lyudi_skazali") and not t[0].isupper():
                errors.append(f"{where} — должна начинаться с заглавной")
            if slot.id == "lyudi_skazali" and t[-1] not in ".!?…":
                errors.append(f"{where} — реплика без знака в конце")
            if slot.id == "delo_konchilos":
                if t[-1] in ".!?" or t.casefold().startswith("что "):
                    errors.append(f"{where} — без «что» в начале и без точки в конце")
            if slot.id == "chto_delali" and not any(re.search(r"(ть|ти|чь)(ся)?$", w) for w in t.replace(",", "").split()[:2]):
                errors.append(f"{where} — первое слово не похоже на инфинитив")
        for theme in THEMES:
            n = len(store.pool(slot.id, [theme.id]))
            if n < MIN_PER_THEME:
                errors.append(f"{slot.id}: в теме «{theme.name}» всего {n} фраз (нужно ≥ {MIN_PER_THEME})")
    return errors


def unknown_words() -> dict[str, list[str]]:
    import pymorphy3

    morph = pymorphy3.MorphAnalyzer()
    known_file = Path(__file__).with_name("known_words.txt")
    known = {w.strip().casefold() for w in known_file.read_text(encoding="utf-8").split()} if known_file.exists() else set()
    result: dict[str, list[str]] = {}
    for slot in SLOTS:
        for e in store.load_all()[slot.id]:
            for w in WORD_RE.findall(e.text):
                low = w.casefold().replace("ё", "е")
                if low in known or w.casefold() in known or not CYRILLIC_RE.search(w):
                    continue
                parts = re.split(r"[-'’]", w)
                if all(morph.word_is_known(p) or p.casefold() in known for p in parts if p):
                    continue
                result.setdefault(w, []).append(f"{slot.id}: {e.text}")
    return result


def main() -> int:
    errors = structural_errors()
    for err in errors:
        print("ОШИБКА:", err)
    print(f"структура: {'ок' if not errors else f'{len(errors)} ошибок'}")
    if "--no-spell" not in sys.argv:
        unknown = unknown_words()
        print(f"\nнеизвестных словарю слов: {len(unknown)}")
        for w, where in sorted(unknown.items()):
            print(f"  {w:25} <- {where[0]}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
