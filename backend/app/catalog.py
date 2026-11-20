"""
Каталог: темы (о чём сказка) и слоты (из каких частей она состоит).

Тема — это тег фразы. Одна фраза может относиться к нескольким темам.
Служебные теги: ``any`` — фраза подходит к любой теме, ``adult`` — фраза
скрывается в детском режиме.
Слот — роль фразы в тексте («кто», «где», «что делали»...). Фразы слота лежат
в ``data/<bank>.txt``; несколько слотов могут брать фразы из одного банка
(помощник выбирается из тех же героев, что и главный герой).
"""
from __future__ import annotations

from dataclasses import dataclass

ANY_THEME = "any"
ADULT_TAG = "adult"


@dataclass(frozen=True)
class Theme:
    id: str
    name: str
    description: str = ""  # только если названия темы мало


@dataclass(frozen=True)
class Group:
    id: str
    title: str


@dataclass(frozen=True)
class Slot:
    id: str
    title: str      # короткое название для переключателей
    question: str   # вопрос на экране выбора
    group: str
    required: bool = False
    bank: str = ""  # файл data/<bank>.txt; по умолчанию совпадает с id

    @property
    def bank_id(self) -> str:
        return self.bank or self.id


THEMES: list[Theme] = [
    Theme("fairy", "Сказочные"),
    Theme("cartoon", "Мультики"),
    Theme("movie", "Кино и супергерои"),
    Theme("space", "Космос и наука"),
    Theme("quest", "Приключения и пираты"),
    Theme("home", "Дом и семья"),
    Theme("school", "Школа"),
    Theme("sport", "Спорт"),
    Theme("spooky", "Страшилки"),
    Theme("nonsense", "Чепуха", "Говорящая картошка, летающий пельмень и прочий абсурд"),
]

GROUPS: list[Group] = [
    Group("characters", "Герои"),
    Group("setting", "Место и время"),
    Group("events", "События"),
]

# Порядок здесь — порядок вопросов при ручном выборе и порядок в коде ссылки.
# Новые слоты добавляйте только в конец, иначе старые ссылки перестанут открываться.
SLOTS: list[Slot] = [
    Slot("kto", "Герой", "Кто станет героем сказки?", "characters", required=True),
    Slot("s_kem", "Спутник", "С кем он познакомится?", "characters"),
    Slot("gde", "Место", "Где это случилось?", "setting"),
    Slot("kogda", "Время", "Когда это было?", "setting"),
    Slot("chto_delali", "Занятие", "Чем они займутся?", "events", required=True),
    Slot("lyudi_skazali", "Слова людей", "Что скажут люди?", "events"),
    Slot("delo_konchilos", "Концовка", "Чем закончится дело?", "events"),
    Slot("prepyatstvie", "Препятствие", "Что им помешает?", "events"),
    Slot("pomoshnik", "Помощник", "Кто придёт на помощь?", "characters", bank="kto"),
    Slot("moral", "Мораль", "Какая у сказки мораль?", "events"),
]

# Вопросы игры «Чепуха» — как в настоящей игре на бумажках.
CHEPUKHA_SLOTS: list[str] = [
    "kto", "s_kem", "gde", "kogda", "chto_delali", "lyudi_skazali", "delo_konchilos",
]

# Слоты, которые бывают в продолжении сказки (следующих главах).
CONTINUATION_SLOTS: list[str] = ["chto_delali", "prepyatstvie", "pomoshnik", "delo_konchilos"]

# Банки, у фраз которых указан род (m/f/n/p).
GENDERED_BANKS = {"kto"}

# Порядок, в котором части показываются и выбираются (по ходу сюжета).
UI_ORDER: list[str] = [
    "kto", "s_kem", "gde", "kogda", "chto_delali", "prepyatstvie", "pomoshnik",
    "lyudi_skazali", "delo_konchilos", "moral",
]

THEMES_BY_ID = {t.id: t for t in THEMES}
SLOTS_BY_ID = {s.id: s for s in SLOTS}
SLOTS_UI = [SLOTS_BY_ID[sid] for sid in UI_ORDER]
assert set(UI_ORDER) == set(SLOTS_BY_ID)
BANK_IDS = list(dict.fromkeys(s.bank_id for s in SLOTS))
