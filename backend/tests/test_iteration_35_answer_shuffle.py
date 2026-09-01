"""
Iteration 35: Tests for the answer-shuffle fix in loc_lesson_full()/_shuffle_options()
(backend/server.py, ~line 203). Verifies:
  - Option order / answer index varies across repeated calls (randomization actually happens)
  - The option text AT the returned answer index is always the historically-correct text
  - Behavior holds across GET /api/lessons/{id}, GET /api/practice, and duel question sets
  - Works across lang=en/de/es
  - Regression: /complete endpoints still work with {correct, total} bodies
"""
import os
import sys
import pytest
import requests

BASE_URL = os.environ.get("EXPO_PUBLIC_BACKEND_URL", "").rstrip("/")
sys.path.insert(0, "/app/backend")
from curriculum import LESSON_MAP, LESSON_ORDER, LESSON_T  # noqa: E402

EMAIL = "demo@tradequest.app"
PASSWORD = "demo123"


@pytest.fixture(scope="module")
def api_client():
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    resp = session.post(f"{BASE_URL}/api/auth/login", json={"email": EMAIL, "password": PASSWORD})
    if resp.status_code != 200:
        pytest.skip(f"Login failed: {resp.status_code} {resp.text}")
    token = resp.json()["token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    return session


def ground_truth_correct_text(lesson_id: str, q_index: int, lang: str) -> str:
    """Returns the correct option text for a given lesson's q_index & lang,
    computed independently from the raw curriculum source (not via the API)."""
    l = LESSON_MAP[lesson_id]
    raw_q = l["questions"][q_index]
    answer_idx = raw_q["answer"]
    if lang == "en":
        return raw_q["options"][answer_idx]
    t = LESSON_T.get(lang, {}).get(lesson_id)
    if not t:
        return raw_q["options"][answer_idx]
    return t["questions"][q_index]["options"][answer_idx]


class TestLessonShuffle:
    LESSON_ID = LESSON_ORDER[0]  # 'l1'

    @pytest.mark.parametrize("lang", ["en", "de", "es"])
    def test_answer_index_varies_and_correct_text_stable(self, api_client, lang):
        n_calls = 15
        answer_indices = []
        correct_texts = []
        expected_text = ground_truth_correct_text(self.LESSON_ID, 0, lang)

        for _ in range(n_calls):
            resp = api_client.get(f"{BASE_URL}/api/lessons/{self.LESSON_ID}", params={"lang": lang})
            assert resp.status_code == 200, resp.text
            data = resp.json()
            questions = data["questions"]
            assert len(questions) > 0
            q0 = questions[0]
            idx = q0["answer"]
            options = q0["options"]
            assert 0 <= idx < len(options)
            answer_indices.append(idx)
            correct_texts.append(options[idx])

        # 1) Randomization actually happening: not all indices identical across 15 calls
        assert len(set(answer_indices)) > 1, (
            f"lang={lang}: answer index never varied across {n_calls} calls: {answer_indices}"
        )

        # 2) Correctness preserved: option at answer index always matches ground truth text
        for i, text in enumerate(correct_texts):
            assert text == expected_text, (
                f"lang={lang} call#{i}: option at answer index = '{text}' != expected '{expected_text}'"
            )

    def test_lesson_not_found_returns_404(self, api_client):
        resp = api_client.get(f"{BASE_URL}/api/lessons/does_not_exist", params={"lang": "en"})
        assert resp.status_code == 404


class TestPracticeShuffle:
    def test_practice_answer_index_varies_and_correct(self, api_client):
        n_calls = 15
        all_answer_indices = []
        mismatches = []

        for _ in range(n_calls):
            resp = api_client.get(f"{BASE_URL}/api/practice", params={"lang": "en"})
            assert resp.status_code == 200, resp.text
            data = resp.json()
            questions = data["questions"]
            assert len(questions) == 5
            for q in questions:
                idx = q["answer"]
                options = q["options"]
                assert 0 <= idx < len(options)
                all_answer_indices.append(idx)
                # find ground truth by matching question text AND option-set (as a set,
                # since order is shuffled) against LESSON_MAP -- question text alone can
                # repeat across different lessons (e.g. "What is a share?" appears 3x
                # with different option sets), so option-set must match too.
                matched = None
                for lid, l in LESSON_MAP.items():
                    for qi, raw_q in enumerate(l["questions"]):
                        if raw_q["q"] == q["q"] and set(raw_q["options"]) == set(options):
                            matched = ground_truth_correct_text(lid, qi, "en")
                            break
                    if matched:
                        break
                if matched is not None and options[idx] != matched:
                    mismatches.append((q["q"], options[idx], matched))

        assert len(set(all_answer_indices)) > 1, (
            f"Practice answer index never varied across {n_calls*5} questions: {all_answer_indices}"
        )
        assert not mismatches, f"Mismatched correct answers in practice: {mismatches}"


class TestDuelShuffle:
    def test_duel_option_order_can_vary_across_fetches_and_stays_correct(self, api_client):
        # create duel
        resp = api_client.post(f"{BASE_URL}/api/duels", params={"lang": "en"})
        assert resp.status_code == 201 or resp.status_code == 200, resp.text
        duel = resp.json()
        duel_id = duel["duel_id"]
        assert len(duel["questions"]) > 0

        # fetch the duel's question set multiple times (simulating reloads / 2nd player)
        fetched_indices_per_call = []
        for _ in range(6):
            r = api_client.get(f"{BASE_URL}/api/duels/{duel_id}", params={"lang": "en"})
            assert r.status_code == 200, r.text
            qdata = r.json()
            qs = qdata["questions"]
            assert len(qs) == len(duel["questions"])
            idxs = [q["answer"] for q in qs]
            fetched_indices_per_call.append(idxs)

            # correctness check for each question in this fetch
            for q in qs:
                idx = q["answer"]
                options = q["options"]
                assert 0 <= idx < len(options)
                matched = None
                for lid, l in LESSON_MAP.items():
                    for qi, raw_q in enumerate(l["questions"]):
                        if raw_q["q"] == q["q"] and set(raw_q["options"]) == set(options):
                            matched = ground_truth_correct_text(lid, qi, "en")
                            break
                    if matched:
                        break
                if matched is not None:
                    assert options[idx] == matched, (
                        f"Duel Q '{q['q']}' answer index {idx} -> '{options[idx]}' != expected '{matched}'"
                    )

        # confirm at least one question's index differs across the 6 fetches (order not fixed)
        varied = False
        for pos in range(len(fetched_indices_per_call[0])):
            vals = {call[pos] for call in fetched_indices_per_call}
            if len(vals) > 1:
                varied = True
                break
        assert varied, f"Duel option order never varied across fetches: {fetched_indices_per_call}"


class TestCompleteRegressions:
    def test_lesson_complete_still_works(self, api_client):
        lesson_id = LESSON_ORDER[0]
        resp = api_client.post(
            f"{BASE_URL}/api/lessons/{lesson_id}/complete", json={"correct": 3, "total": 4}
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "earned_xp" in data
        assert "user" in data

    def test_practice_complete_still_works(self, api_client):
        resp = api_client.post(
            f"{BASE_URL}/api/practice/complete", json={"correct": 4, "total": 5, "tier": 1}
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "earned_xp" in data
        assert "user" in data

    def test_duel_complete_still_works(self, api_client):
        resp = api_client.post(f"{BASE_URL}/api/duels", params={"lang": "en"})
        assert resp.status_code in (200, 201)
        duel_id = resp.json()["duel_id"]
        resp2 = api_client.post(
            f"{BASE_URL}/api/duels/{duel_id}/complete", json={"correct": 5, "total": 5}
        )
        assert resp2.status_code == 200, resp2.text
        data = resp2.json()
        assert data["creator_result"]["correct"] == 5
        assert data["creator_result"]["total"] == 5
