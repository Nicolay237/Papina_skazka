"""
Каталог: темы (о чём сказка) и слоты (из каких частей она состоит).

Тема — это тег фразы. Одна фраза может относиться к нескольким темам.
Тег ``any`` ставится на универсальные фразы: они попадают в любую подборку.
Слот — роль фразы в тексте («кто», «где», «что делали»...). Для каждого слота
есть файл ``data/<slot_id>.txt``.
"""
from __future__ import annotations

from dataclasses import dataclass

ANY_THEME = "any"


@dataclass(frozen=True)
class Theme:
    id: str
    name: str
    emoji: str
    description: str


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
    has_gender: bool = False


THEMES: list[Theme] = [
    Theme("fairy", "Сказочные", "🏰", "Баба-яга, Колобок, богатыри и тридевятое царство"),
    Theme("cartoon", "Мультики", "🎠", "Чебурашка, Винни-Пух, Простоквашино и Фиксики"),
    Theme("movie", "Кино и супергерои", "🦸", "Бэтмен, Гарри Поттер, Шерлок Холмс и Йода"),
    Theme("space", "Космос и наука", "🚀", "Ракеты, инопланетяне, роботы и безумные учёные"),
    Theme("quest", "Приключения и пираты", "🏴‍☠️", "Клады, острова, джунгли и морские волки"),
    Theme("home", "Дом и семья", "🏠", "Бабушкины пирожки, папин диван и вредный кот"),
    Theme("school", "Школа", "🎒", "Контрольные, перемены, портфели и завуч"),
    Theme("sport", "Спорт", "⚽", "Матчи, рекорды, тренеры и болельщики"),
    Theme("spooky", "Страшилки", "🦇", "Привидения, вампиры и монстры из-под кровати"),
    Theme("nonsense", "Чепуха", "🌀", "Говорящая картошка, летающий пельмень и прочий абсурд"),
]

GROUPS: list[Group] = [
    Group("characters", "Герои"),
    Group("setting", "Место и время"),
    Group("events", "События"),
]

SLOTS: list[Slot] = [
    Slot("kto", "Герой", "Кто станет героем сказки?", "characters", required=True, has_gender=True),
    Slot("s_kem", "Спутник", "С кем он познакомится?", "characters"),
    Slot("gde", "Место", "Где это случилось?", "setting"),
    Slot("kogda", "Время", "Когда это было?", "setting"),
    Slot("chto_delali", "Занятие", "Чем они займутся?", "events", required=True),
    Slot("lyudi_skazali", "Слова людей", "Что скажут люди?", "events"),
    Slot("delo_konchilos", "Концовка", "Чем закончится дело?", "events"),
]

THEMES_BY_ID = {t.id: t for t in THEMES}
SLOTS_BY_ID = {s.id: s for s in SLOTS}
