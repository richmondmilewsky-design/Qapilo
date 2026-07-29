"""Iteration 7 — Localization regression:
- /api/lessons/{id}?lang=de|es — options/explanations translated
- /api/practice?lang=de|es — questions/options translated
- /api/tutor/chat — replies in German/Spanish + localized disclaimer line
- Brand: 'Qapilo' present everywhere (system prompt).
"""

import os
import re
import uuid

import pytest
import requests

BASE = os.environ["EXPO_PUBLIC_BACKEND_URL"].rstrip("/")
API = f"{BASE}/api"


# ------------------------------ auth fixture ------------------------------
@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    email = f"TEST_it7_{uuid.uuid4().hex[:8]}@qapilo.app"
    r = s.post(f"{API}/auth/signup", json={"email": email, "password": "test1234", "name": "IT7 Tester"})
    assert r.status_code == 200, r.text
    body = r.json()
    token = body.get("access_token") or body.get("token")
    assert token, f"no token in signup response: {body}"
    s.headers.update({"Authorization": f"Bearer {token}"})
    # Accept terms so tutor endpoint works cleanly
    s.post(f"{API}/auth/accept-terms")
    return s


# ------------------------------ lessons ------------------------------
class TestLessonsLocalization:
    def test_lesson_en_de_differ(self, session):
        en = session.get(f"{API}/lessons/l1?lang=en").json()
        de = session.get(f"{API}/lessons/l1?lang=de").json()
        es = session.get(f"{API}/lessons/l1?lang=es").json()

        assert en["questions"] and de["questions"] and es["questions"]
        # At least one question text differs across langs
        assert en["questions"][0]["q"] != de["questions"][0]["q"]
        assert en["questions"][0]["q"] != es["questions"][0]["q"]
        # Same shape
        assert len(en["questions"][0]["options"]) == len(de["questions"][0]["options"]) == len(es["questions"][0]["options"])

    def test_curriculum_lang(self, session):
        de = session.get(f"{API}/curriculum?lang=de").json()
        en = session.get(f"{API}/curriculum?lang=en").json()
        assert de["units"] and en["units"]
        assert de["units"][0]["title"] != en["units"][0]["title"]


# ------------------------------ practice ------------------------------
class TestPracticeLocalization:
    def test_practice_de(self, session):
        r = session.get(f"{API}/practice?lang=de")
        assert r.status_code == 200
        data = r.json()
        assert "questions" in data and len(data["questions"]) == 5
        for q in data["questions"]:
            assert len(q["options"]) == 4

    def test_practice_es(self, session):
        r = session.get(f"{API}/practice?lang=es")
        assert r.status_code == 200
        data = r.json()
        assert len(data["questions"]) == 5


# ------------------------------ tutor lang ------------------------------
GERMAN_HINTS = re.compile(
    r"\b(?:die|der|das|ist|und|nicht|Aktie|Aktien|Finanzberatung|Bildungszwecken|keine|zu)\b",
    re.IGNORECASE,
)
SPANISH_HINTS = re.compile(
    r"\b(?:el|la|los|las|una|es|no|acci[oó]n|acciones|financiero|educativos|asesoramiento)\b",
    re.IGNORECASE,
)


class TestTutorLangReply:
    def test_tutor_reply_german(self, session):
        r = session.post(
            f"{API}/tutor/chat",
            json={"message": "Was ist eine Aktie?", "lang": "de"},
            timeout=90,
        )
        assert r.status_code == 200, r.text
        reply = r.json().get("reply", "")
        assert reply, "empty reply"
        # Reply is in German — check enough German function-word hits
        hits = len(GERMAN_HINTS.findall(reply))
        assert hits >= 3, f"Expected German content, got: {reply[:400]}"
        # Should NOT look English (no dominant English marker phrase)
        assert "not financial advice" not in reply.lower(), (
            f"Disclaimer wasn't translated to German: {reply[-300:]}"
        )

    def test_tutor_reply_spanish(self, session):
        r = session.post(
            f"{API}/tutor/chat",
            json={"message": "¿Qué es una acción?", "lang": "es"},
            timeout=90,
        )
        assert r.status_code == 200, r.text
        reply = r.json().get("reply", "")
        assert reply, "empty reply"
        hits = len(SPANISH_HINTS.findall(reply))
        assert hits >= 3, f"Expected Spanish content, got: {reply[:400]}"
        assert "not financial advice" not in reply.lower(), (
            f"Disclaimer wasn't translated to Spanish: {reply[-300:]}"
        )

    def test_tutor_reply_english(self, session):
        r = session.post(
            f"{API}/tutor/chat",
            json={"message": "What is a stock?", "lang": "en"},
            timeout=90,
        )
        assert r.status_code == 200, r.text
        reply = r.json().get("reply", "")
        assert reply
        # Sanity: English reply should contain common English words
        assert re.search(r"\b(the|is|a|stock|company)\b", reply, re.IGNORECASE)
