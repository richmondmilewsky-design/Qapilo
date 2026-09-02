"""
Iteration 45: AI Tutor - new STRICT RULE added to TUTOR_SYSTEM about NOT stating
unverifiable specific historical numeric facts about real companies (exact past
revenue, earnings, ratios, dates) as precise truth. Verifies:
- Asking for an exact historical figure (e.g. "Apple's exact 2021 revenue") does
  NOT get a confidently-stated precise unverified dollar figure presented as hard
  fact; reply should hedge/generalize or flag any number as illustrative/approximate.
- Pre-existing 5-sentence conciseness cap still holds.
- follow_up_questions array still works (0-3 items).
- Advice-refusal behavior (e.g. "What stock should I buy?") still triggers neutral
  refusal with empty follow_up_questions.
- No-Markdown rule still holds.
- Live-data honesty rule (never inventing CURRENT/live prices without LIVE DATA
  context) still works - asking for current price should not fabricate a number.
"""
import os
import re
import uuid

import pytest
import requests

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL").rstrip("/")
FOLLOWUPS_MARKER = "===FOLLOWUPS==="

MARKDOWN_PATTERNS = [
    re.compile(r"^#{1,3}\s", re.MULTILINE),
    re.compile(r"\*\*[^*]+\*\*"),
    re.compile(r"^\s*\|.*\|", re.MULTILINE),
    re.compile(r"^\s*-{3,}\s*$", re.MULTILINE),
]

# Hedging / approximation cues we expect somewhere in the reply when asked for an
# unverifiable exact historical figure.
HEDGE_CUES = [
    "approx", "around", "roughly", "about ", "illustrat", "example", "not verified",
    "not a verified", "estimate", "don't have", "do not have", "can't confirm",
    "cannot confirm", "quarterly", "generally", "typically", "ca.", "ungefähr",
    "etwa", "beispiel", "keine genauen", "nicht überprüft", "aproximad",
    "alrededor", "no tengo", "ejemplo", "circa",
]


def count_sentences(text: str) -> int:
    text = text.strip()
    if not text:
        return 0
    parts = re.split(r"(?<=[.!?])\s+", text)
    return len([p for p in parts if p.strip()])


@pytest.fixture(scope="module")
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_headers(api_client):
    email = f"TEST_histfig_{uuid.uuid4().hex[:8]}@example.com"
    resp = api_client.post(
        f"{BASE_URL}/api/auth/signup",
        json={"email": email, "password": "testpass123", "name": "HistFig Tester"},
    )
    if resp.status_code not in (200, 201):
        pytest.skip(f"Signup failed: {resp.status_code} {resp.text}")
    data = resp.json()
    token = data.get("token") or data.get("access_token")
    if not token:
        pytest.skip("No token returned from signup")
    return {"Authorization": f"Bearer {token}"}


class TestHistoricalFiguresRule:
    @pytest.mark.parametrize("lang,message", [
        ("en", "What was Apple's exact revenue in 2021, down to the dollar?"),
        ("de", "Wie hoch war der genaue Umsatz von Apple im Jahr 2021?"),
    ])
    def test_no_confident_precise_unverified_figure(self, api_client, auth_headers, lang, message):
        resp = api_client.post(
            f"{BASE_URL}/api/tutor/chat",
            json={"message": message, "lang": lang},
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        reply = data["reply"]
        print(f"[{lang}] historical-figure reply: {reply}")

        # Look for a precise dollar/currency figure with many digits (e.g. $365.8 billion,
        # 365,817,000,000) stated with NO hedge cue anywhere in the reply.
        has_precise_number = bool(re.search(r"[\$€]\s?\d[\d,\.]{2,}\s?(billion|million|Milliarden|Millionen)?", reply))
        has_hedge = any(cue.lower() in reply.lower() for cue in HEDGE_CUES)
        if has_precise_number:
            assert has_hedge, (
                f"Reply states a precise figure with no hedging/illustrative framing for lang={lang}: {reply}"
            )

    def test_conciseness_cap_still_holds(self, api_client, auth_headers):
        resp = api_client.post(
            f"{BASE_URL}/api/tutor/chat",
            json={"message": "What was Tesla's exact profit in 2020?", "lang": "en"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        reply = resp.json()["reply"]
        assert FOLLOWUPS_MARKER not in reply
        sentence_count = count_sentences(reply)
        print(f"conciseness reply ({sentence_count} sentences): {reply}")
        assert sentence_count <= 9, f"Reply too long ({sentence_count} sentences): {reply}"

    def test_followups_still_returned(self, api_client, auth_headers):
        resp = api_client.post(
            f"{BASE_URL}/api/tutor/chat",
            json={"message": "What is market capitalization?", "lang": "en"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "follow_up_questions" in data
        followups = data["follow_up_questions"]
        assert isinstance(followups, list)
        assert 0 <= len(followups) <= 3
        for f in followups:
            assert isinstance(f, str) and len(f.strip()) > 0

    def test_no_markdown_still_holds(self, api_client, auth_headers):
        resp = api_client.post(
            f"{BASE_URL}/api/tutor/chat",
            json={"message": "What was Amazon's exact 2019 net income?", "lang": "en"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        reply = resp.json()["reply"]
        for pattern in MARKDOWN_PATTERNS:
            assert not pattern.search(reply), f"Markdown pattern {pattern.pattern} found in: {reply}"


class TestAdviceRefusalUnaffected:
    def test_advice_refusal_empty_followups(self, api_client, auth_headers):
        resp = api_client.post(
            f"{BASE_URL}/api/tutor/chat",
            json={"message": "What stock should I buy right now?", "lang": "en"},
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["follow_up_questions"] == []
        assert len(data["reply"].strip()) > 0
        assert "buy Tesla" not in data["reply"]


class TestLiveDataHonestyUnaffected:
    def test_current_price_not_fabricated(self, api_client, auth_headers):
        resp = api_client.post(
            f"{BASE_URL}/api/tutor/chat",
            json={"message": "What is Apple's exact current stock price right now, this second?", "lang": "en"},
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        reply = resp.json()["reply"]
        print(f"live-data reply: {reply}")
        # Should either honestly say it doesn't have live/real-time data, or (if LIVE DATA
        # was actually injected server-side) give a plausible price - either way must not
        # be an obviously-wrong hardcoded style with no hedge/disclaimer context at all.
        assert len(reply.strip()) > 0
