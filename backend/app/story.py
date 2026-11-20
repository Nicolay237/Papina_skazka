"""
Сборка сказки из выбранных фраз.

Фразы в банках хранятся в «серединном» виде (строчная буква, предлоги и падежи
уже внутри), поэтому склонять ничего не нужно. Согласование одно — глаголы
с героем по роду и числу: «Колобок познакомился», «Три поросёнка познакомились».
Герой и помощник всегда стоят в начале предложения, поэтому их заглавная буква
никогда не мешает.

Сказка состоит из глав. Первая глава — полная завязка, следующие («Продолжить
сказку») — новые приключения тех же героев. Текст однозначно задаётся фразами
и числом ``seed``, поэтому сказку можно упаковать в короткий код для ссылки
и восстановить слово в слово.
"""
from __future__ import annotations

import base64
import binascii
import random
from dataclasses import dataclass, field

from .catalog import CONTINUATION_SLOTS, SLOTS, SLOTS_BY_ID, THEMES_BY_ID, UI_ORDER
from .store import KEY_BYTES, Entry, find, find_by_key, pool, sample, upper_first

MAX_CHAPTERS = 5
CODE_VERSION = 1

G = dict[str, str]  # формы по роду: m, f, n, p


def _forms(m: str, f: str, n: str, p: str) -> G:
    return {"m": m, "f": f, "n": n, "p": p}


_PRONOUN = _forms("он", "она", "оно", "они")
_TO_THEM = _forms("нему", "ней", "нему", "ним")  # «присоединился к нему»
_MET = [
    _forms("познакомился", "познакомилась", "познакомилось", "познакомились"),
    _forms("подружился", "подружилась", "подружилось", "подружились"),
    _forms("повстречался", "повстречалась", "повстречалось", "повстречались"),
    _forms("столкнулся нос к носу", "столкнулась нос к носу", "столкнулось нос к носу", "столкнулись нос к носу"),
]
_FOUND_SELF = _forms("оказался", "оказалась", "оказалось", "оказались")
_LIVED = _forms("спокойно жил", "спокойно жила", "спокойно жило", "спокойно жили")
_SET_OFF = _forms("отправился", "отправилась", "отправилось", "отправились")
_STARTS = [
    _forms("принялся", "принялась", "принялось", "принялись"),
    _forms("стал", "стала", "стало", "стали"),
    _forms("решил", "решила", "решило", "решили"),
    _forms("не придумал ничего лучше, чем", "не придумала ничего лучше, чем",
           "не придумало ничего лучше, чем", "не придумали ничего лучше, чем"),
]
_HELPED = [
    _forms("пришёл на помощь", "пришла на помощь", "пришло на помощь", "пришли на помощь"),
    _forms("примчался на выручку", "примчалась на выручку", "примчалось на выручку", "примчались на выручку"),
    _forms("подоспел вовремя и всех выручил", "подоспела вовремя и всех выручила",
           "подоспело вовремя и всех выручило", "подоспели вовремя и всех выручили"),
]
_JOINED = _forms("присоединился", "присоединилась", "присоединилось", "присоединились")

_OBSTACLE_LEADS = ["Но вдруг", "Неожиданно", "И тут"]
_SAID_INTROS = [
    "Люди говорили:", "Люди говорили:", "Все вокруг твердили:",
    "Прохожие шептались:", "Соседи говорили:", "А люди вокруг восклицали:",
]
_ENDINGS = [
    "Дело кончилось тем, что", "Дело кончилось тем, что", "Дело кончилось тем, что",
    "А закончилось всё тем, что", "В итоге", "В конце концов",
]
_ENDINGS_AGAIN = ["На этот раз дело кончилось тем, что", "В итоге", "И в этот раз всё закончилось тем, что"]
_OPENERS_AGAIN = ["На следующий день", "Прошла неделя, и", "Через год", "Однажды утром"]
_MORAL_INTROS = ["Мораль сей сказки такова:", "А мораль такая:"]


class StoryError(ValueError):
    pass


@dataclass
class Story:
    chapters: list[dict[str, Entry]]
    seed: int
    paragraphs: list[list[str]] = field(default_factory=list)  # по главам

    @property
    def text(self) -> str:
        return "\n\n".join(p for chapter in self.paragraphs for p in chapter)

    @property
    def code(self) -> str:
        return encode(self)


def _end(s: str) -> str:
    s = s.rstrip()
    return s if s and s[-1] in ".!?…" else s + "."


# ----------------------------------------------------------------- текст

def compose(chapters: list[dict[str, Entry]], seed: int) -> list[list[str]]:
    """Текст по главам. Одинаковые фразы и seed всегда дают одинаковый текст,
    а добавление главы не меняет предыдущие."""
    rng = random.Random(seed)
    first = chapters[0]
    hero = first["kto"]
    g = hero.gender or "m"
    companion = first.get("s_kem")
    place = first.get("gde")
    together = companion is not None  # героев больше одного — дальше «они»

    def who() -> tuple[str, str]:
        return ("они", "p") if together else (_PRONOUN[g], g)

    result: list[list[str]] = []
    moral_intro = ""
    for index, picks in enumerate(chapters):
        paragraphs: list[str] = []
        if index == 0:
            paragraphs.append(_opening(picks, hero, g, rng))
            pron, form = who()
            if companion:
                lead = rng.choice(["Там они", "И там они", "Вместе они"] if place else ["Тогда они", "Вместе они", "А потом они"])
            else:
                lead = f"{rng.choice(['Там', 'И там'] if place else ['Тогда', 'Потом', 'А потом'])} {pron}"
        else:
            pron, form = who()
            opener = rng.choice(_OPENERS_AGAIN)
            lead = f"{opener} {pron}"
            if index == 1:
                lead = "Но на этом история не закончилась. " + lead
        verb = rng.choice(_STARTS)[form]
        paragraphs.append(_end(f"{lead} {verb} {picks['chto_delali'].text}"))

        obstacle = picks.get("prepyatstvie")
        helper = picks.get("pomoshnik")
        if obstacle or helper:
            sentences = []
            if obstacle:
                sentences.append(_end(f"{rng.choice(_OBSTACLE_LEADS)} {obstacle.text}"))
            if helper:
                hg = helper.gender or "m"
                if obstacle:
                    sentences.append(_end(f"{helper.text} {rng.choice(_HELPED)[hg]}"))
                else:
                    to_them = "ним" if together else _TO_THEM[g]
                    sentences.append(_end(f"{helper.text} {_JOINED[hg]} к {to_them}"))
                together = True
            paragraphs.append(" ".join(sentences))

        said = picks.get("lyudi_skazali")
        if said:
            inner = said.text.replace("«", "„").replace("»", "“")  # кавычки внутри реплики — «лапки»
            paragraphs.append(f"{rng.choice(_SAID_INTROS)} «{inner}»")

        ending = picks.get("delo_konchilos")
        if ending:
            leads = _ENDINGS if index == 0 else _ENDINGS_AGAIN
            if " что " in f" {ending.text} ":  # «тем, что выяснилось, что…» — двойное «что»
                leads = [lead for lead in leads if not lead.endswith("что")]
            paragraphs.append(_end(f"{rng.choice(leads)} {ending.text}"))

        if index == 0:
            moral_intro = rng.choice(_MORAL_INTROS)  # тянем сразу, чтобы главы не сдвигали случайность
        result.append(paragraphs)

    moral = first.get("moral")
    if moral:
        result[-1].append(f"{moral_intro} {moral.text}")
    return result


def _opening(picks: dict[str, Entry], hero: Entry, g: str, rng: random.Random) -> str:
    companion = picks.get("s_kem")
    place = picks.get("gde")
    when = picks.get("kogda")
    h = hero.text
    if companion:
        met = rng.choice(_MET)[g]
        if place and rng.random() < 0.4:
            # «Колобок спокойно жил в шкафу. Как-то раз, в юности, он подружился с Лешим.»
            second = f"Как-то раз, {when.text}, {_PRONOUN[g]} {met} {companion.text}" if when \
                else f"Однажды {_PRONOUN[g]} {met} {companion.text}"
            return f"{_end(f'{h} {_LIVED[g]} {place.text}')} {_end(second)}"
        text = f"{h} {met} {companion.text}"
        if place:
            text += f" {place.text}"
    elif place:
        if rng.random() < 0.5:
            text = f"{h} {_FOUND_SELF[g]} {place.text}"
        else:
            text = f"{h} {_LIVED[g]} {place.text}"
            if when:
                return _end(f"{text}, и вот однажды, {when.text}, всё изменилось")
    else:
        text = f"{h} {_SET_OFF[g]} навстречу приключениям"
    if when:
        text += f", {when.text}"
    return _end(upper_first(text))


# ----------------------------------------------------------------- выбор фраз

def _check_themes(themes: list[str]) -> None:
    unknown = [t for t in themes if t not in THEMES_BY_ID]
    if unknown:
        raise StoryError(f"Неизвестная тема: {', '.join(unknown)}")


def _check_slots(slot_ids: list[str]) -> None:
    unknown = [s for s in slot_ids if s not in SLOTS_BY_ID]
    if unknown:
        raise StoryError(f"Неизвестная часть сказки: {', '.join(unknown)}")


def resolve_picks(
    themes: list[str],
    answers: dict[str, str],
    include: list[str] | None,
    rng: random.Random,
    kid: bool = False,
) -> dict[str, Entry]:
    """Части первой главы и фраза для каждой. Ответы, выбранные вручную,
    принимаются и в детском режиме: человек видел их на экране сам."""
    _check_themes(themes)
    _check_slots(list(answers) + list(include or []))
    wanted = set(answers) | (set(include) if include is not None else set(SLOTS_BY_ID))
    picks: dict[str, Entry] = {}
    for slot in SLOTS:
        if slot.id not in wanted and not slot.required:
            continue
        if slot.id in answers:
            entry = find(slot.id, answers[slot.id])
            if entry is None:
                raise StoryError(f"Фразы «{answers[slot.id]}» нет в банке «{slot.title}»")
        else:
            avoid = {picks["kto"].text} if slot.id == "pomoshnik" and "kto" in picks else None
            entry = sample(slot.id, themes, rng, kid, avoid)
        picks[slot.id] = entry
    return picks


def generate(
    themes: list[str] | None = None,
    answers: dict[str, str] | None = None,
    include: list[str] | None = None,
    kid: bool = False,
    rng: random.Random | None = None,
) -> Story:
    rng = rng or random.Random()
    picks = resolve_picks(themes or [], answers or {}, include, rng, kid)
    story = Story(chapters=[picks], seed=rng.randrange(1 << 16))
    story.paragraphs = compose(story.chapters, story.seed)
    return story


def continue_story(
    story: Story,
    themes: list[str] | None = None,
    include: list[str] | None = None,
    kid: bool = False,
    rng: random.Random | None = None,
) -> Story:
    """Дописывает к сказке новую главу с теми же героями."""
    if len(story.chapters) >= MAX_CHAPTERS:
        raise StoryError(f"В сказке уже {MAX_CHAPTERS} глав — это предел")
    themes = themes or []
    _check_themes(themes)
    _check_slots(list(include or []))
    rng = rng or random.Random()
    used = {p.text for chapter in story.chapters for p in chapter.values()}
    slots = [s for s in CONTINUATION_SLOTS if s == "chto_delali" or include is None or s in include]
    picks: dict[str, Entry] = {}
    for slot_id in slots:
        picks[slot_id] = sample(slot_id, themes, rng, kid, avoid=used)
    chapters = [*story.chapters, picks]
    return Story(chapters=chapters, seed=story.seed, paragraphs=compose(chapters, story.seed))


def options(
    slot_id: str,
    themes: list[str],
    limit: int = 12,
    exclude: list[str] | None = None,
    kid: bool = False,
    rng: random.Random | None = None,
) -> tuple[list[Entry], int]:
    """Случайная выборка вариантов для экрана выбора. Возвращает (варианты, всего в подборке)."""
    _check_slots([slot_id])
    _check_themes(themes)
    rng = rng or random.Random()
    entries = pool(slot_id, themes, kid)
    skip = {e.casefold() for e in (exclude or [])}
    fresh = [e for e in entries if e.text.casefold() not in skip]
    source = fresh if len(fresh) >= min(limit, len(entries)) else entries
    return rng.sample(source, min(limit, len(source))), len(entries)


def ordered_picks(story: Story) -> list[tuple[int, str, Entry]]:
    """(номер главы, слот, фраза) в порядке сюжета — для блока «Из чего сложилась сказка»."""
    return [
        (i, sid, chapter[sid])
        for i, chapter in enumerate(story.chapters)
        for sid in UI_ORDER
        if sid in chapter
    ]


# ----------------------------------------------------------------- код ссылки
# Байты: версия (1) | seed (2) | число глав (1) | на каждую главу: маска слотов (2)
# и ключи фраз по KEY_BYTES в порядке SLOTS. Всё в base64url без «=».

def encode(story: Story) -> str:
    out = bytearray([CODE_VERSION])
    out += story.seed.to_bytes(2, "big")
    out.append(len(story.chapters))
    for chapter in story.chapters:
        mask = 0
        keys = bytearray()
        for i, slot in enumerate(SLOTS):
            if slot.id in chapter:
                mask |= 1 << i
                keys += chapter[slot.id].key
        out += mask.to_bytes(2, "big") + keys
    return base64.urlsafe_b64encode(bytes(out)).decode("ascii").rstrip("=")


def decode(code: str) -> Story:
    bad = StoryError("Ссылка на сказку повреждена или устарела")
    if not code or len(code) > 400:
        raise bad
    try:
        raw = base64.urlsafe_b64decode(code + "=" * (-len(code) % 4))
    except (binascii.Error, ValueError):
        raise bad from None
    if len(raw) < 4 or raw[0] != CODE_VERSION:
        raise bad
    seed = int.from_bytes(raw[1:3], "big")
    count = raw[3]
    if not 1 <= count <= MAX_CHAPTERS:
        raise bad
    pos = 4
    chapters: list[dict[str, Entry]] = []
    for _ in range(count):
        if pos + 2 > len(raw):
            raise bad
        mask = int.from_bytes(raw[pos:pos + 2], "big")
        pos += 2
        chapter: dict[str, Entry] = {}
        for i, slot in enumerate(SLOTS):
            if mask & (1 << i):
                key = raw[pos:pos + KEY_BYTES]
                pos += KEY_BYTES
                entry = find_by_key(slot.id, key) if len(key) == KEY_BYTES else None
                if entry is None:
                    raise bad
                chapter[slot.id] = entry
        if mask >> len(SLOTS) or "chto_delali" not in chapter:
            raise bad
        chapters.append(chapter)
    if pos != len(raw) or "kto" not in chapters[0]:
        raise bad
    return Story(chapters=chapters, seed=seed, paragraphs=compose(chapters, seed))
