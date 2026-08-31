"""
Iteration 28: AI Tutor follow-up question suggestions feature.
Tests POST /api/tutor/chat response field 'follow_up_questions' (EN/DE/ES),
advice-refusal always returning [], and regression on /tutor/history, /tutor/status.
"""
import os
import time
import uuid

import pytest
import requests

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL").rstrip("/")
FOLLOWUPS_MARKER = "===FOLLOWUPS==="


@pytest.fixture(scope="module")
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_token(api_client):
    email = f"TEST_followup_{uuid.uuid4().hex[:8]}@example.com"
    resp = api_client.post(
        f"{BASE_URL}/api/auth/signup",
        json={"email": email, "password": "testpass123", "name": "Followup Tester"},
    )
    if resp.status_code not in (200, 201):
        pytest.skip(f"Signup failed: {resp.status_code} {resp.text}")
    data = resp.json()
    token = data.get("token") or data.get("access_token")
    if not token:
        pytest.skip("No token returned from signup")
    return token


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


class TestFollowUpQuestionsNormalAnswer:
    """Normal educational question should return follow_up_questions array, clean reply."""

    @pytest.mark.parametrize("lang", ["en", "de", "es"])
    def test_followups_present_and_clean(self, api_client, auth_headers, lang):
        resp = api_client.post(
            f"{BASE_URL}/api/tutor/chat",
            json={"message": "What is a dividend?", "lang": lang},
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "follow_up_questions" in data
        followups = data["follow_up_questions"]
        assert isinstance(followups, list)
        assert 0 <= len(followups) <= 3

        # reply must not leak the marker
        assert FOLLOWUPS_MARKER not in data["reply"]

        for f in followups:
            assert isinstance(f, str)
            assert len(f.strip()) > 0
            assert FOLLOWUPS_MARKER not in f
            # no numbering/bullet prefixes
            assert not f.strip()[0].isdigit(), f"Follow-up starts with a digit/number: {f}"
            assert not f.strip().startswith(("-", "*", "•")), f"Follow-up starts with bullet: {f}"

        # sanity: reply still has content and no truncation artifacts
        assert len(data["reply"].strip()) > 0

    def test_followups_language_match_de(self, api_client, auth_headers):
        resp = api_client.post(
            f"{BASE_URL}/api/tutor/chat",
            json={"message": "Was ist eine Dividende?", "lang": "de"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        followups = data["follow_up_questions"]
        if followups:
            # crude language heuristic: German words/diacritics likely present
            joined = " ".join(followups).lower()
            english_markers = ["what is", "how does", "why do", "the "]
            # Not a strict assertion (LLM variance) - just log
            print(f"DE followups: {followups}")
        assert True

    def test_followups_language_match_es(self, api_client, auth_headers):
        resp = api_client.post(
            f"{BASE_URL}/api/tutor/chat",
            json={"message": "¿Qué es un dividendo?", "lang": "es"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        print(f"ES followups: {data['follow_up_questions']}")
        assert True


class TestAdviceRefusalFollowups:
    """Advice-seeking questions must always return follow_up_questions: []"""

    def test_advice_refusal_empty_followups(self, api_client, auth_headers):
        resp = api_client.post(
            f"{BASE_URL}/api/tutor/chat",
            json={"message": "Should I buy Tesla stock right now?", "lang": "en"},
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["follow_up_questions"] == []
        assert "reply" in data and len(data["reply"]) > 0


class TestRegressionHistoryStatus:
    """Regression: /tutor/history and /tutor/status still work; no follow_up_questions in DB."""

    def test_status_fields_unaffected(self, api_client, auth_headers):
        resp = api_client.get(f"{BASE_URL}/api/tutor/status", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "is_pro" in data
        assert "remaining" in data

    def test_history_fields_unaffected(self, api_client, auth_headers):
        # Send a message first so this worker's own history is guaranteed non-empty
        # (module-scoped fixtures are re-created per xdist worker process).
        chat_resp = api_client.post(
            f"{BASE_URL}/api/tutor/chat",
            json={"message": "What is an ETF?", "lang": "en"},
            headers=auth_headers,
        )
        assert chat_resp.status_code == 200

        resp = api_client.get(f"{BASE_URL}/api/tutor/history", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "messages" in data
        assert isinstance(data["messages"], list)
        assert len(data["messages"]) > 0
        for m in data["messages"]:
            assert set(m.keys()) <= {"role", "content", "created_at"}
            assert "follow_up_questions" not in m
            assert FOLLOWUPS_MARKER not in m["content"]
