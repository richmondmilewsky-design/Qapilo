"""
Iteration 22: Tests for TUTOR_SYSTEM prompt-only update (backend/server.py).
Verifies: (1) plain-language + inline parenthetical jargon definitions in EN/DE/ES,
(2) regression of advice-refusal logic, (3) regression of disclaimer append logic,
(4) reply conciseness, (5) no invented live price data.
"""
import os
import re
import time
import uuid

import pytest
import requests

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL", "").rstrip("/")
if not BASE_URL:
    BASE_URL = "http://localhost:8001"


@pytest.fixture(scope="module")
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_token(api_client):
    """Sign up a fresh test user (prefixed TEST_) to get a JWT, or fall back to demo creds."""
    email = f"TEST_tutor_{uuid.uuid4().hex[:8]}@example.com"
    resp = api_client.post(
        f"{BASE_URL}/api/auth/signup",
        json={"email": email, "password": "demo1234"},
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        token = data.get("token") or data.get("access_token")
        if token:
            return token
    # fallback to demo credentials
    resp2 = api_client.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "demo@tradequest.app", "password": "demo123"},
    )
    assert resp2.status_code == 200, f"login fallback failed: {resp2.status_code} {resp2.text}"
    data2 = resp2.json()
    token = data2.get("token") or data2.get("access_token")
    assert token
    return token


@pytest.fixture(scope="module")
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


def chat(api_client, headers, message, lang):
    resp = api_client.post(
        f"{BASE_URL}/api/tutor/chat",
        json={"message": message, "lang": lang},
        headers=headers,
        timeout=60,
    )
    return resp


PAREN_RE = re.compile(r"\([^)]{10,220}\)")


class TestJargonDefinitionInline:
    """Verify inline parenthetical plain-language jargon definitions per language."""

    def test_english_dividend_question(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "What is a dividend?", "en")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        reply = data["reply"]
        assert isinstance(reply, str) and len(reply) > 0
        # must mention dividend
        assert "dividend" in reply.lower()
        # must have at least one inline parenthetical explanation (not glossary heading)
        parens = PAREN_RE.findall(reply)
        assert len(parens) >= 1, f"No inline parenthetical definition found. Reply: {reply}"
        # should not have a separate "Glossary" / "Definitions:" style section
        assert not re.search(r"\b(glossary|definitions?:)\b", reply, re.IGNORECASE), reply
        # disclaimer should be appended once
        assert "educational purposes only" in reply.lower() or "not constitute financial" in reply.lower()

    def test_german_dividend_question(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "Was ist eine Dividende?", "de")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        reply = data["reply"]
        # Reply should be predominantly German - check for German-specific words
        assert re.search(r"\b(ist|und|der|die|das|eine|ein|du|dir)\b", reply, re.IGNORECASE), reply
        parens = PAREN_RE.findall(reply)
        assert len(parens) >= 1, f"No inline parenthetical definition found (DE). Reply: {reply}"
        # inline definition itself should be in German, not English (heuristic: no "a small part" in English)
        assert "a small part of a company's profit" not in reply
        assert "bildungszwecken" in reply.lower() or "finanz- oder anlageberatung" in reply.lower()

    def test_spanish_dividend_question(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "¿Qué es un dividendo?", "es")
        assert resp.status_code == 200, resp.text
        data = resp.json()
        reply = data["reply"]
        assert re.search(r"\b(es|una|un|de|que|del|los|las)\b", reply, re.IGNORECASE), reply
        parens = PAREN_RE.findall(reply)
        assert len(parens) >= 1, f"No inline parenthetical definition found (ES). Reply: {reply}"
        assert "a small part of a company's profit" not in reply
        assert "fines educativos" in reply.lower() or "asesoramiento financiero" in reply.lower()


class TestConciseness:
    def test_reply_not_too_long(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "What is a stock?", "en")
        assert resp.status_code == 200, resp.text
        reply = resp.json()["reply"]
        # roughly 2-5 short paragraphs -> allow generous upper bound on paragraph count
        paragraphs = [p for p in reply.split("\n\n") if p.strip()]
        assert len(paragraphs) <= 7, f"Too many paragraphs ({len(paragraphs)}): {reply}"
        assert len(reply) < 3000, f"Reply too long ({len(reply)} chars)"


class TestAdviceRefusalRegression:
    def test_should_i_buy_tesla_refused(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "Should I buy Tesla stock right now?", "en")
        assert resp.status_code == 200, resp.text
        reply = resp.json()["reply"]
        assert "can't tell you what to buy" in reply or "cannot tell you what to buy" in reply.lower() or "personalized financial advice" in reply.lower()
        # must not contain a direct recommendation
        assert "you should buy tesla" not in reply.lower()

    def test_invest_10000_refused(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "What should I invest my $10,000 in?", "en")
        assert resp.status_code == 200, resp.text
        reply = resp.json()["reply"]
        assert "can't tell you what to buy" in reply or "personalized financial advice" in reply.lower()


class TestDisclaimerRegression:
    def test_disclaimer_present_once_en(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "What is an ETF?", "en")
        assert resp.status_code == 200, resp.text
        reply = resp.json()["reply"]
        count = reply.lower().count("educational purposes only")
        assert count <= 1, f"Disclaimer duplicated {count} times: {reply}"
        assert count == 1 or "not financial advice" in reply.lower() or "not constitute financial" in reply.lower()

    def test_disclaimer_present_de(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "Was ist ein ETF?", "de")
        assert resp.status_code == 200, resp.text
        reply = resp.json()["reply"]
        assert "bildungszwecken" in reply.lower()
        assert reply.lower().count("bildungszwecken") <= 1


class TestNoLiveDataInvented:
    def test_no_price_when_not_provided(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "What is the current price of gold today?", "en")
        assert resp.status_code == 200, resp.text
        reply = resp.json()["reply"]
        # Should indicate no live data available (heuristic check)
        assert re.search(r"(don't have|do not have|no access|can't provide|cannot provide|no real-time|not able to)", reply, re.IGNORECASE), reply
