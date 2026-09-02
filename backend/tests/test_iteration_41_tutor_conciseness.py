"""
Iteration 41: AI Tutor conciseness cap.
TUTOR_SYSTEM prompt tightened from "2-5 short paragraphs" to a hard cap of
"maximum of 5 sentences total" for the main answer (excluding ===FOLLOWUPS===
section). Verifies:
- POST /api/tutor/chat returns noticeably short main answers (~5 sentences,
  allow some LLM variance up to ~8) in en/de.
- follow_up_questions array still returned correctly (unaffected).
- advice-refusal behavior unaffected -> follow_up_questions: [].
- no-Markdown rule still holds in shortened replies.
- inline jargon definition style still present.
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


def count_sentences(text: str) -> int:
    # crude sentence counter: split on . ! ? followed by space/end, ignore short abbrevs
    text = text.strip()
    if not text:
        return 0
    # remove trailing disclaimer-ish content markers isn't needed here since we pass raw answer part
    parts = re.split(r"(?<=[.!?])\s+", text)
    return len([p for p in parts if p.strip()])


@pytest.fixture(scope="module")
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="module")
def auth_headers(api_client):
    email = f"TEST_concise_{uuid.uuid4().hex[:8]}@example.com"
    resp = api_client.post(
        f"{BASE_URL}/api/auth/signup",
        json={"email": email, "password": "testpass123", "name": "Concise Tester"},
    )
    if resp.status_code not in (200, 201):
        pytest.skip(f"Signup failed: {resp.status_code} {resp.text}")
    data = resp.json()
    token = data.get("token") or data.get("access_token")
    if not token:
        pytest.skip("No token returned from signup")
    return {"Authorization": f"Bearer {token}"}


def get_main_answer(reply: str) -> str:
    """Strip trailing disclaimer sentence (last sentence appended) heuristically by
    just returning full reply text minus follow-ups marker (already split by API)."""
    return reply.strip()


class TestConciseness:
    """Main answer should be noticeably short - roughly ~5 sentences (allow up to ~8 for LLM variance)."""

    @pytest.mark.parametrize("lang,message", [
        ("en", "What is a dividend?"),
        ("de", "Was ist eine Dividende?"),
    ])
    def test_reply_is_short(self, api_client, auth_headers, lang, message):
        resp = api_client.post(
            f"{BASE_URL}/api/tutor/chat",
            json={"message": message, "lang": lang},
            headers=auth_headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        reply = data["reply"]
        assert FOLLOWUPS_MARKER not in reply

        sentence_count = count_sentences(reply)
        print(f"[{lang}] reply ({sentence_count} sentences): {reply}")
        # Allow generous slack for LLM variance + appended disclaimer sentence,
        # but must be clearly shorter than old multi-paragraph essays (~10-15+ sentences).
        assert sentence_count <= 9, (
            f"Reply too long ({sentence_count} sentences) for lang={lang}: {reply}"
        )
        assert len(reply) < 1800, f"Reply char length too long for lang={lang}: {len(reply)}"

    def test_followups_still_returned(self, api_client, auth_headers):
        resp = api_client.post(
            f"{BASE_URL}/api/tutor/chat",
            json={"message": "What is an ETF?", "lang": "en"},
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

    def test_no_markdown_in_shortened_reply(self, api_client, auth_headers):
        resp = api_client.post(
            f"{BASE_URL}/api/tutor/chat",
            json={"message": "Compare a stock and an ETF briefly.", "lang": "en"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        reply = resp.json()["reply"]
        for pattern in MARKDOWN_PATTERNS:
            assert not pattern.search(reply), f"Markdown pattern {pattern.pattern} found in: {reply}"

    def test_inline_jargon_definition_present(self, api_client, auth_headers):
        resp = api_client.post(
            f"{BASE_URL}/api/tutor/chat",
            json={"message": "What is a dividend?", "lang": "en"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        reply = resp.json()["reply"]
        # look for a parenthetical inline definition style "(...)"
        assert "(" in reply and ")" in reply, f"No inline parenthetical definition found: {reply}"


class TestAdviceRefusalUnaffected:
    """Advice-seeking questions must still get neutral refusal with empty follow_up_questions."""

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
        # refusal reply should not recommend a specific ticker
        assert "buy Tesla" not in data["reply"]
