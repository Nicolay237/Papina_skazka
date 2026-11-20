import random

import pytest
from fastapi.testclient import TestClient

from app import store
from app.catalog import CHEPUKHA_SLOTS, SLOTS, THEMES
from app.main import app
from app.story import MAX_CHAPTERS, StoryError, continue_story, decode, encode, generate, options

client = TestClient(app)


def all_text(s):
    return " ".join(p for ch in s.paragraphs for p in ch)


# ---------------------------------------------------------------- база

def test_every_theme_has_enough_phrases_in_every_slot_even_for_kids():
    for slot in SLOTS:
        for theme in THEMES:
            assert len(store.pool(slot.id, [theme.id], kid=True)) >= 12, (slot.id, theme.id)


def test_texts_are_unique_within_bank():
    for bank, entries in store.load_all().items():
        texts = [e.text.casefold() for e in entries]
        assert len(texts) == len(set(texts)), bank


def test_kid_mode_hides_adult_phrases():
    adult = [e for e in store.bank_of("kogda") if e.adult]
    assert adult, "в банке должны быть фразы с пометкой adult"
    kid_pool = store.pool("kogda", [], kid=True)
    assert not any(e.adult for e in kid_pool)
    assert len(kid_pool) == len(store.bank_of("kogda")) - len(adult)
    for seed in range(300):
        s = generate(kid=True, rng=random.Random(seed))
        assert not any(e.adult for e in s.chapters[0].values())


# ---------------------------------------------------------------- текст

def test_random_story_is_well_formed():
    for seed in range(300):
        s = generate(rng=random.Random(seed))
        for p in s.paragraphs[0]:
            assert p[0].isupper(), p
            assert p[-1] in ".!?…»", p
            assert "  " not in p and " ," not in p and ".." not in p, p


def test_story_structure_varies():
    openings = {
        generate(answers={"kto": "Колобок", "s_kem": "с Лешим", "gde": "в шкафу"}, rng=random.Random(seed))
        .paragraphs[0][0].split(" с Лешим")[0]
        for seed in range(60)
    }
    assert len(openings) >= 4, openings


def test_verb_agrees_with_hero_gender():
    cases = {"Колобок": "ся", "Баба-яга": "ась", "Три поросёнка": "ись", "Привидение из старого замка": "ось"}
    for hero, ending in cases.items():
        for seed in range(20):
            s = generate(answers={"kto": hero, "s_kem": "с Чебурашкой"}, include=["s_kem"], rng=random.Random(seed))
            first = s.paragraphs[0][0]
            assert first.startswith(hero), first
            verb = first[len(hero):].split()[0]
            assert verb.endswith(ending), (hero, first)


def test_lone_hero_story():
    s = generate(answers={"kto": "Баба-яга", "chto_delali": "вязать крючком"}, include=[], rng=random.Random(3))
    assert s.paragraphs[0][0] == "Баба-яга отправилась навстречу приключениям."
    assert " она " in s.paragraphs[0][1]
    assert len(s.paragraphs[0]) == 2


def test_helper_joins_without_obstacle_and_rescues_with_one():
    base = {"kto": "Баба-яга", "chto_delali": "вязать крючком", "pomoshnik": "Колобок"}
    s = generate(answers=base, include=[], rng=random.Random(1))
    assert "Колобок присоединился к ней." in all_text(s)
    s = generate(answers={**base, "prepyatstvie": "налетел страшный ураган"}, include=[], rng=random.Random(1))
    text = all_text(s)
    assert "налетел страшный ураган." in text and "Колобок " in text and "присоединился" not in text


def test_helper_is_never_the_hero():
    for seed in range(200):
        s = generate(answers={"kto": "Колобок"}, rng=random.Random(seed))
        assert s.chapters[0]["pomoshnik"].text != "Колобок"


def test_moral_is_always_last():
    s = generate(answers={"moral": "друзья познаются в беде."}, rng=random.Random(5))
    s = continue_story(s, rng=random.Random(6))
    assert s.paragraphs[-1][-1].endswith("друзья познаются в беде.")
    assert sum("друзья познаются" in p for ch in s.paragraphs for p in ch) == 1


def test_quotes_inside_a_quote_are_not_nested():
    s = generate(answers={"lyudi_skazali": "Папа сказал: «Только на минутку» — и пропал на три часа!"},
                 include=["lyudi_skazali"], rng=random.Random(0))
    said = next(p for p in s.paragraphs[0] if "Папа сказал" in p)
    assert said.count("«") == 1 and said.count("»") == 1


def test_themes_restrict_the_pool():
    for seed in range(50):
        s = generate(themes=["space"], rng=random.Random(seed))
        for slot_id, e in s.chapters[0].items():
            assert e.themes & {"space", "any"}, (slot_id, e)


# ---------------------------------------------------------------- главы и ссылки

def test_continue_keeps_earlier_chapters_and_stops_at_limit():
    s = generate(include=["s_kem", "gde", "lyudi_skazali", "delo_konchilos"], rng=random.Random(7))
    first = list(s.paragraphs[0])
    for n in range(2, MAX_CHAPTERS + 1):
        s = continue_story(s, rng=random.Random(n))
        assert len(s.paragraphs) == n
        assert s.paragraphs[0] == first
    with pytest.raises(StoryError):
        continue_story(s)


def test_code_roundtrip_restores_exact_text():
    for seed in range(100):
        s = generate(rng=random.Random(seed))
        if seed % 3 == 0:
            s = continue_story(s, rng=random.Random(seed + 1))
        restored = decode(encode(s))
        assert restored.text == s.text
        assert len(s.code) < 120


@pytest.mark.parametrize("code", ["", "abc", "AAAA", "!!!", "x" * 500])
def test_bad_codes_are_rejected(code):
    with pytest.raises(StoryError):
        decode(code)


def test_unknown_phrase_and_theme_are_rejected():
    with pytest.raises(StoryError):
        generate(answers={"kto": "Несуществующий"})
    with pytest.raises(StoryError):
        generate(themes=["nope"])
    with pytest.raises(StoryError):
        generate(include=["nope"])


def test_options_respect_limit_exclude_and_kid_mode():
    opts, total = options("gde", ["fairy"], limit=5)
    assert len(opts) == 5 and total >= 12
    excluded = [o.text for o in opts]
    again, _ = options("gde", ["fairy"], limit=5, exclude=excluded)
    assert not {o.text for o in again} & set(excluded)
    kid_opts, _ = options("kogda", [], limit=40, kid=True)
    assert not any(o.adult for o in kid_opts)


# ---------------------------------------------------------------- API

def test_api_flow_create_open_continue():
    meta = client.get("/api/meta").json()
    assert [s["id"] for s in meta["slots"]][:2] == ["kto", "s_kem"]
    assert meta["chepukha_slots"] == CHEPUKHA_SLOTS

    body = client.post("/api/story", json={"themes": ["fairy"], "kid": True}).json()
    assert body["can_continue"] and body["code"]
    assert body["story"] == "\n\n".join(p for ch in body["chapters"] for p in ch)

    opened = client.get(f"/api/story/{body['code']}").json()
    assert opened["story"] == body["story"]

    more = client.post("/api/story/continue", json={"code": body["code"], "kid": True}).json()
    assert len(more["chapters"]) == 2 and more["chapters"][0][0] == body["chapters"][0][0]
    assert {p["chapter"] for p in more["picks"]} == {1, 2}

    r = client.post("/api/story", json={"include": ["gde"]})
    assert {p["slot"] for p in r.json()["picks"]} == {"kto", "chto_delali", "gde"}


def test_api_rejects_bad_input():
    assert client.post("/api/story", json={"answers": {"kto": "нет такого"}}).status_code == 400
    assert client.post("/api/story", json={"themes": ["zzz"]}).status_code == 400
    assert client.post("/api/options", json={"slot": "zzz"}).status_code == 400
    assert client.post("/api/options", json={"slot": "kto", "limit": 1000}).status_code == 422
    assert client.get("/api/story/broken").status_code == 404
    assert client.post("/api/story/continue", json={"code": "broken"}).status_code == 400
