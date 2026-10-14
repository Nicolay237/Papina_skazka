import random

import pytest
from fastapi.testclient import TestClient

from app import store
from app.catalog import SLOTS, THEMES
from app.main import app
from app.story import StoryError, generate, options

client = TestClient(app)


def test_every_theme_has_enough_phrases_in_every_slot():
    for slot in SLOTS:
        for theme in THEMES:
            assert len(store.pool(slot.id, [theme.id])) >= 12, (slot.id, theme.id)


def test_texts_are_unique_within_slot():
    for slot in SLOTS:
        texts = [e.text.casefold() for e in store.load_all()[slot.id]]
        assert len(texts) == len(set(texts)), slot.id


def test_random_story_has_four_paragraphs_and_ends_with_punctuation():
    for seed in range(200):
        s = generate(rng=random.Random(seed))
        assert len(s.paragraphs) == 4
        for p in s.paragraphs:
            assert p[0].isupper(), p
            assert p[-1] in ".!?…»", p
            assert "  " not in p and " ," not in p and ".." not in p, p


def test_verb_agrees_with_hero_gender():
    cases = {"Колобок": "познакомился", "Баба-яга": "познакомилась",
             "Три поросёнка": "познакомились", "Привидение из старого замка": "познакомилось"}
    for hero, verb in cases.items():
        s = generate(answers={"kto": hero, "s_kem": "с Чебурашкой"}, include=["s_kem"], rng=random.Random(1))
        assert f"{hero} {verb} с Чебурашкой" in s.paragraphs[0]


def test_lone_hero_uses_matching_pronoun_and_verb():
    s = generate(answers={"kto": "Баба-яга", "chto_delali": "вязать крючком"}, include=[], rng=random.Random(3))
    assert s.paragraphs[0] == "Баба-яга отправилась навстречу приключениям."
    assert " она " in s.paragraphs[1]
    assert len(s.paragraphs) == 2


def test_with_companion_second_sentence_is_plural():
    s = generate(answers={"kto": "Баба-яга", "s_kem": "с Лешим", "chto_delali": "вязать крючком"},
                 include=["s_kem"], rng=random.Random(3))
    assert " они " in s.paragraphs[1]


def test_themes_restrict_the_pool():
    for seed in range(50):
        s = generate(themes=["space"], rng=random.Random(seed))
        for slot_id, e in s.picks.items():
            assert e.themes & {"space", "any"}, (slot_id, e)


def test_unknown_phrase_and_theme_are_rejected():
    with pytest.raises(StoryError):
        generate(answers={"kto": "Несуществующий"})
    with pytest.raises(StoryError):
        generate(themes=["nope"])
    with pytest.raises(StoryError):
        generate(include=["nope"])


def test_options_respect_limit_and_exclude():
    opts, total = options("gde", ["fairy"], limit=5)
    assert len(opts) == 5 and total >= 12
    excluded = [o.text for o in opts]
    again, _ = options("gde", ["fairy"], limit=5, exclude=excluded)
    assert not {o.text for o in again} & set(excluded)


def test_api_meta_and_story_and_options():
    meta = client.get("/api/meta").json()
    assert len(meta["themes"]) == len(THEMES) and len(meta["slots"]) == len(SLOTS)

    r = client.post("/api/story", json={"themes": ["fairy"]})
    assert r.status_code == 200
    body = r.json()
    assert body["story"] == "\n\n".join(body["paragraphs"])
    assert {p["slot"] for p in body["picks"]} == {s.id for s in SLOTS}

    r = client.post("/api/story", json={"include": ["gde"]})
    assert {p["slot"] for p in r.json()["picks"]} == {"kto", "chto_delali", "gde"}

    r = client.post("/api/options", json={"slot": "kto", "themes": ["sport"], "limit": 6})
    assert r.status_code == 200 and len(r.json()["options"]) == 6


def test_api_rejects_bad_input():
    assert client.post("/api/story", json={"answers": {"kto": "нет такого"}}).status_code == 400
    assert client.post("/api/story", json={"themes": ["zzz"]}).status_code == 400
    assert client.post("/api/options", json={"slot": "zzz"}).status_code == 400
    assert client.post("/api/options", json={"slot": "kto", "limit": 1000}).status_code == 422


def test_quotes_inside_a_quote_are_not_nested():
    s = generate(answers={"lyudi_skazali": "Папа сказал: «Только на минутку» — и пропал на три часа!"}, rng=random.Random(0))
    said = s.paragraphs[2]
    assert said.count("«") == 1 and said.count("»") == 1
