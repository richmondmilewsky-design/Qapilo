"""
Iteration 5 — Watchlist feature backend tests.
Tests:
- POST /api/watchlist/{symbol}/toggle: add/remove semantics, 404 for invalid symbol, auth-gated
- GET /api/stocks: each item has 'in_watchlist' boolean; watchlisted items pinned to top
- GET /api/stocks/{symbol}: 'in_watchlist' reflects current state
- Persistence across requests (toggle → re-fetch)
"""
import os
import secrets
import pytest
import requests

BASE_URL = os.environ["EXPO_PUBLIC_BACKEND_URL"].rstrip("/")


@pytest.fixture(scope="module")
def auth_client():
    """Sign up a fresh test user, return an authenticated requests.Session."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    email = f"TEST_it5_{secrets.token_hex(4)}@tradequest.app"
    password = "demo123!"
    r = session.post(f"{BASE_URL}/api/auth/signup",
                     json={"name": "TEST it5", "email": email, "password": password})
    assert r.status_code == 200, f"signup failed: {r.status_code} {r.text}"
    token = r.json()["token"]
    session.headers.update({"Authorization": f"Bearer {token}"})
    # accept terms so the user is not gated
    session.post(f"{BASE_URL}/api/auth/accept-terms")
    session.creds = {"email": email, "password": password}  # type: ignore[attr-defined]
    return session


# --------------------------- Auth-gate ---------------------------
class TestAuthGate:
    def test_toggle_requires_auth(self):
        r = requests.post(f"{BASE_URL}/api/watchlist/AAPL/toggle")
        assert r.status_code in (401, 403), f"expected auth error, got {r.status_code}"

    def test_stocks_list_requires_auth(self):
        r = requests.get(f"{BASE_URL}/api/stocks")
        assert r.status_code in (401, 403)


# --------------------------- Toggle semantics ---------------------------
class TestToggleSemantics:
    def test_toggle_invalid_symbol_returns_404(self, auth_client):
        r = auth_client.post(f"{BASE_URL}/api/watchlist/ZZZZZ/toggle")
        assert r.status_code == 404

    def test_toggle_add_then_remove(self, auth_client):
        sym = "AAPL"
        # Reset state — force to 'not watched' by toggling until removed
        r0 = auth_client.get(f"{BASE_URL}/api/stocks/{sym}")
        assert r0.status_code == 200
        if r0.json().get("in_watchlist"):
            auth_client.post(f"{BASE_URL}/api/watchlist/{sym}/toggle")

        # Add
        r1 = auth_client.post(f"{BASE_URL}/api/watchlist/{sym}/toggle")
        assert r1.status_code == 200, r1.text
        j1 = r1.json()
        assert j1["symbol"] == sym
        assert j1["in_watchlist"] is True
        assert sym in j1["watchlist"]

        # Remove
        r2 = auth_client.post(f"{BASE_URL}/api/watchlist/{sym}/toggle")
        assert r2.status_code == 200
        j2 = r2.json()
        assert j2["in_watchlist"] is False
        assert sym not in j2["watchlist"]

    def test_toggle_lowercase_symbol_normalized(self, auth_client):
        r = auth_client.post(f"{BASE_URL}/api/watchlist/msft/toggle")
        assert r.status_code == 200
        assert r.json()["symbol"] == "MSFT"
        # cleanup
        auth_client.post(f"{BASE_URL}/api/watchlist/MSFT/toggle")


# --------------------------- List + pinning ---------------------------
class TestStocksListPinning:
    def test_list_items_have_in_watchlist_flag(self, auth_client):
        r = auth_client.get(f"{BASE_URL}/api/stocks")
        assert r.status_code == 200
        stocks = r.json()["stocks"]
        assert len(stocks) > 0
        for s in stocks:
            assert "in_watchlist" in s, f"missing in_watchlist on {s.get('symbol')}"
            assert isinstance(s["in_watchlist"], bool)

    def test_watchlisted_are_pinned_to_top(self, auth_client):
        # Ensure clean starting state
        state = auth_client.get(f"{BASE_URL}/api/stocks").json()["stocks"]
        for s in state:
            if s["in_watchlist"]:
                auth_client.post(f"{BASE_URL}/api/watchlist/{s['symbol']}/toggle")

        # Toggle two mid/late symbols
        base = auth_client.get(f"{BASE_URL}/api/stocks").json()["stocks"]
        assert len(base) >= 4
        pick = [base[-1]["symbol"], base[len(base) // 2]["symbol"]]
        for sym in pick:
            r = auth_client.post(f"{BASE_URL}/api/watchlist/{sym}/toggle")
            assert r.status_code == 200
            assert r.json()["in_watchlist"] is True

        after = auth_client.get(f"{BASE_URL}/api/stocks").json()["stocks"]
        top_syms = [s["symbol"] for s in after[: len(pick)]]
        # All watchlisted must be at the top
        assert set(top_syms) == set(pick), f"expected {pick} pinned to top, got {top_syms}"
        for s in after[: len(pick)]:
            assert s["in_watchlist"] is True
        for s in after[len(pick):]:
            assert s["in_watchlist"] is False

        # Cleanup
        for sym in pick:
            auth_client.post(f"{BASE_URL}/api/watchlist/{sym}/toggle")

    def test_stock_detail_reflects_state(self, auth_client):
        sym = "GOOGL"
        # Ensure not watchlisted
        r0 = auth_client.get(f"{BASE_URL}/api/stocks/{sym}").json()
        if r0.get("in_watchlist"):
            auth_client.post(f"{BASE_URL}/api/watchlist/{sym}/toggle")

        r1 = auth_client.get(f"{BASE_URL}/api/stocks/{sym}").json()
        assert r1["in_watchlist"] is False

        auth_client.post(f"{BASE_URL}/api/watchlist/{sym}/toggle")
        r2 = auth_client.get(f"{BASE_URL}/api/stocks/{sym}").json()
        assert r2["in_watchlist"] is True

        # Cleanup
        auth_client.post(f"{BASE_URL}/api/watchlist/{sym}/toggle")


# --------------------------- Persistence across re-login ---------------------------
class TestPersistence:
    def test_watchlist_persists_across_relogin(self, auth_client):
        sym = "TSLA"
        # Add TSLA
        r = auth_client.post(f"{BASE_URL}/api/watchlist/{sym}/toggle")
        assert r.status_code == 200
        assert r.json()["in_watchlist"] is True

        # Re-login as same user
        creds = auth_client.creds  # type: ignore[attr-defined]
        r_login = requests.post(f"{BASE_URL}/api/auth/login", json=creds)
        assert r_login.status_code == 200
        token2 = r_login.json()["token"]

        s2 = requests.Session()
        s2.headers.update({"Content-Type": "application/json",
                           "Authorization": f"Bearer {token2}"})

        detail = s2.get(f"{BASE_URL}/api/stocks/{sym}").json()
        assert detail["in_watchlist"] is True, "TSLA should still be watchlisted after re-login"

        listing = s2.get(f"{BASE_URL}/api/stocks").json()["stocks"]
        assert listing[0]["symbol"] == sym, "TSLA should be pinned to top after re-login"
        assert listing[0]["in_watchlist"] is True

        # Cleanup
        s2.post(f"{BASE_URL}/api/watchlist/{sym}/toggle")


# --------------------------- Search/category regression ---------------------------
class TestRegression:
    def test_search_still_returns_in_watchlist_flag(self, auth_client):
        r = auth_client.get(f"{BASE_URL}/api/stocks", params={"q": "app"})
        assert r.status_code == 200
        stocks = r.json()["stocks"]
        assert len(stocks) >= 1
        assert all("in_watchlist" in s for s in stocks)

    def test_category_filter_still_works(self, auth_client):
        # Use a valid category from full list
        cats = auth_client.get(f"{BASE_URL}/api/stocks").json()["categories"]
        target_cat = next((c for c in cats if c != "All"), None)
        assert target_cat is not None
        r = auth_client.get(f"{BASE_URL}/api/stocks", params={"category": target_cat})
        assert r.status_code == 200
        stocks = r.json()["stocks"]
        assert len(stocks) > 0
        for s in stocks:
            assert s["category"] == target_cat
            assert "in_watchlist" in s
