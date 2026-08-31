"""
Iteration 27: Tests for TUTOR_SYSTEM prompt update (backend/server.py) - no-Markdown rule.
Verifies: (1) no Markdown headers/bold/italic/tables/links in EN/DE/ES replies,
(2) list requests use plain dashes/numbers with no bold markers,
(3) regressions: jargon-definition style, advice-refusal, disclaimer append - unaffected.
"""
import os
import re
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
    email = f"TEST_nomd_{uuid.uuid4().hex[:8]}@example.com"
    resp = api_client.post(
        f"{BASE_URL}/api/auth/signup",
        json={"email": email, "password": "demo1234"},
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        token = data.get("token") or data.get("access_token")
        if token:
            return token
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


HEADER_RE = re.compile(r"(^|\n)\s{0,3}#{1,6}\s", re.MULTILINE)
BOLD_RE = re.compile(r"\*\*[^*]+\*\*")
ITALIC_RE = re.compile(r"(?<!\*)\*[^*\n]+\*(?!\*)")
TABLE_PIPE_RE = re.compile(r"\|.*\|")
TABLE_DIVIDER_RE = re.compile(r"^\s*\|?[\s\-:|]{3,}\|?\s*$", re.MULTILINE)
DASH_DIVIDER_RE = re.compile(r"^-{3,}\s*$", re.MULTILINE)
MD_LINK_RE = re.compile(r"\[[^\]]+\]\([^)]+\)")


def assert_no_markdown(reply: str):
    assert not HEADER_RE.search(reply), f"Found Markdown header in reply: {reply}"
    assert not BOLD_RE.search(reply), f"Found **bold** markers in reply: {reply}"
    assert not ITALIC_RE.search(reply), f"Found *italic* markers in reply: {reply}"
    assert not TABLE_PIPE_RE.search(reply), f"Found '|' table syntax in reply: {reply}"
    assert not TABLE_DIVIDER_RE.search(reply), f"Found '---' table divider in reply: {reply}"
    assert not DASH_DIVIDER_RE.search(reply), f"Found standalone '---' divider in reply: {reply}"
    assert not MD_LINK_RE.search(reply), f"Found [link](url) markdown syntax in reply: {reply}"


class TestNoMarkdownComparison:
    """Comparison questions must not use Markdown tables/bold/headers."""

    def test_german_stock_vs_etf(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "Aktie vs. ETF - was ist der Unterschied?", "de")
        assert resp.status_code == 200, resp.text
        reply = resp.json()["reply"]
        assert_no_markdown(reply)
        assert len(reply) > 20

    def test_english_stock_vs_etf(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "What is the difference between a stock and an ETF?", "en")
        assert resp.status_code == 200, resp.text
        reply = resp.json()["reply"]
        assert_no_markdown(reply)
        assert len(reply) > 20

    def test_spanish_stock_vs_etf(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "¿Cuál es la diferencia entre una acción y un ETF?", "es")
        assert resp.status_code == 200, resp.text
        reply = resp.json()["reply"]
        assert_no_markdown(reply)
        assert len(reply) > 20


class TestNoMarkdownList:
    def test_list_request_plain_dashes_no_bold(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "List 3 ways people invest their money", "en")
        assert resp.status_code == 200, resp.text
        reply = resp.json()["reply"]
        assert_no_markdown(reply)
        # Expect some list-like structure: dashes or numbered points
        has_list_marker = bool(re.search(r"(^\s*-\s+\S)|(^\s*\d+[\.\)]\s+\S)", reply, re.MULTILINE))
        assert has_list_marker, f"Expected plain dash/number list markers, got: {reply}"


class TestJargonRegression:
    """Regression: 10-year-old plain language + inline parenthetical definitions still works."""

    PAREN_RE = re.compile(r"\([^)]{10,220}\)")

    def test_dividend_en(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "What is a dividend?", "en")
        assert resp.status_code == 200, resp.text
        reply = resp.json()["reply"]
        assert_no_markdown(reply)
        assert "dividend" in reply.lower()
        assert len(self.PAREN_RE.findall(reply)) >= 1, f"No inline definition: {reply}"

    def test_dividend_de(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "Was ist eine Dividende?", "de")
        assert resp.status_code == 200, resp.text
        reply = resp.json()["reply"]
        assert_no_markdown(reply)
        assert len(self.PAREN_RE.findall(reply)) >= 1, f"No inline definition (DE): {reply}"

    def test_dividend_es(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "¿Qué es un dividendo?", "es")
        assert resp.status_code == 200, resp.text
        reply = resp.json()["reply"]
        assert_no_markdown(reply)
        assert len(self.PAREN_RE.findall(reply)) >= 1, f"No inline definition (ES): {reply}"


class TestAdviceRefusalRegression:
    def test_should_i_buy_tesla_refused(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "Should I buy Tesla stock right now?", "en")
        assert resp.status_code == 200, resp.text
        reply = resp.json()["reply"]
        assert (
            "can't tell you what to buy" in reply
            or "cannot tell you what to buy" in reply.lower()
            or "personalized financial advice" in reply.lower()
        )
        assert "you should buy tesla" not in reply.lower()
        assert_no_markdown(reply)


class TestDisclaimerRegression:
    def test_disclaimer_present_once_en(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "What is an ETF?", "en")
        assert resp.status_code == 200, resp.text
        reply = resp.json()["reply"]
        count = reply.lower().count("educational purposes only")
        assert count <= 1, f"Disclaimer duplicated {count} times: {reply}"

    def test_disclaimer_present_de(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "Was ist ein ETF?", "de")
        assert resp.status_code == 200, resp.text
        reply = resp.json()["reply"]
        assert "bildungszwecken" in reply.lower()
        assert reply.lower().count("bildungszwecken") <= 1

    def test_disclaimer_present_es(self, api_client, auth_headers):
        resp = chat(api_client, auth_headers, "¿Qué es un ETF?", "es")
        assert resp.status_code == 200, resp.text
        reply = resp.json()["reply"]
        assert "fines educativos" in reply.lower() or "asesoramiento financiero" in reply.lower()
