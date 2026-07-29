"""Iteration 9: Backend localized error messages via Accept-Language header.

Covers:
- POST /api/auth/login   -> 'bad_credentials' EN/DE/ES
- POST /api/auth/signup  -> 'email_taken' EN/DE/ES (duplicate)
- GET  /api/stocks/ZZZZ  -> 'stock_not_found' EN/DE/ES (auth required)
- Missing token          -> 'not_authenticated' EN/DE/ES
- Invalid token          -> 'invalid_token' EN/DE/ES
- Regression: successful login/signup still works.
"""
import os
import uuid
import pytest
import requests
from dotenv import load_dotenv

load_dotenv("/app/frontend/.env")
BASE_URL = os.environ["EXPO_PUBLIC_BACKEND_URL"].rstrip("/")

EXPECTED = {
    "bad_credentials": {
        "en": "Invalid email or password",
        "de": "Ungültige E-Mail oder ungültiges Passwort",
        "es": "Correo o contraseña no válidos",
    },
    "email_taken": {
        "en": "Email already registered",
        "de": "E-Mail ist bereits registriert",
        "es": "El correo ya está registrado",
    },
    "stock_not_found": {
        "en": "Stock not found",
        "de": "Aktie nicht gefunden",
        "es": "Acción no encontrada",
    },
    "not_authenticated": {
        "en": "Not authenticated",
        "de": "Nicht authentifiziert",
        "es": "No autenticado",
    },
    "invalid_token": {
        "en": "Invalid or expired token",
        "de": "Ungültiges oder abgelaufenes Token",
        "es": "Token no válido o caducado",
    },
}


@pytest.fixture(scope="session")
def api():
    return requests.Session()


@pytest.fixture(scope="session")
def signed_up_user(api):
    """Sign up one throwaway user we can reuse for auth'd endpoints and for
    duplicate-email negative tests."""
    email = f"TEST_i18n_{uuid.uuid4().hex[:10]}@qapilo.io"
    password = "pw123456"
    r = api.post(f"{BASE_URL}/api/auth/signup",
                 json={"email": email, "password": password, "name": "TEST i18n"},
                 headers={"Accept-Language": "en"})
    assert r.status_code == 200, f"signup failed: {r.status_code} {r.text}"
    data = r.json()
    assert data.get("token")
    return {"email": email, "password": password, "token": data["token"]}


# ---------- bad credentials (login) ----------
@pytest.mark.parametrize("lang", ["en", "de", "es"])
def test_login_bad_credentials_localized(api, lang):
    r = api.post(f"{BASE_URL}/api/auth/login",
                 json={"email": f"nobody_{uuid.uuid4().hex[:6]}@qapilo.io",
                       "password": "wrongpw"},
                 headers={"Accept-Language": lang})
    assert r.status_code == 401
    assert r.json().get("detail") == EXPECTED["bad_credentials"][lang]


@pytest.mark.parametrize("lang", ["en", "de", "es"])
def test_login_wrong_password_for_existing_user(api, signed_up_user, lang):
    r = api.post(f"{BASE_URL}/api/auth/login",
                 json={"email": signed_up_user["email"], "password": "wrongpw"},
                 headers={"Accept-Language": lang})
    assert r.status_code == 401
    assert r.json().get("detail") == EXPECTED["bad_credentials"][lang]


# ---------- duplicate signup ----------
@pytest.mark.parametrize("lang", ["en", "de", "es"])
def test_signup_duplicate_email_localized(api, signed_up_user, lang):
    r = api.post(f"{BASE_URL}/api/auth/signup",
                 json={"email": signed_up_user["email"], "password": "pw123456"},
                 headers={"Accept-Language": lang})
    assert r.status_code == 400
    assert r.json().get("detail") == EXPECTED["email_taken"][lang]


# ---------- stock not found (auth required) ----------
@pytest.mark.parametrize("lang", ["en", "de", "es"])
def test_stock_not_found_localized(api, signed_up_user, lang):
    r = api.get(f"{BASE_URL}/api/stocks/ZZZZ",
                headers={"Accept-Language": lang,
                         "Authorization": f"Bearer {signed_up_user['token']}"})
    assert r.status_code == 404
    assert r.json().get("detail") == EXPECTED["stock_not_found"][lang]


# ---------- missing token ----------
@pytest.mark.parametrize("lang", ["en", "de", "es"])
def test_missing_token_localized(api, lang):
    r = api.get(f"{BASE_URL}/api/auth/me", headers={"Accept-Language": lang})
    assert r.status_code == 401
    assert r.json().get("detail") == EXPECTED["not_authenticated"][lang]


# ---------- invalid token ----------
@pytest.mark.parametrize("lang", ["en", "de", "es"])
def test_invalid_token_localized(api, lang):
    r = api.get(f"{BASE_URL}/api/auth/me",
                headers={"Accept-Language": lang,
                         "Authorization": "Bearer not-a-real-token"})
    assert r.status_code == 401
    assert r.json().get("detail") == EXPECTED["invalid_token"][lang]


# ---------- regression: successful login still works ----------
def test_login_success_regression(api, signed_up_user):
    r = api.post(f"{BASE_URL}/api/auth/login",
                 json={"email": signed_up_user["email"],
                       "password": signed_up_user["password"]},
                 headers={"Accept-Language": "de"})
    assert r.status_code == 200
    body = r.json()
    assert body.get("token")
    assert body.get("user", {}).get("email") == signed_up_user["email"].lower()


# ---------- accept-language variants (region tags, fallback) ----------
def test_accept_language_region_tag_de_de(api):
    """'de-DE,de;q=0.9' should still resolve to German."""
    r = api.post(f"{BASE_URL}/api/auth/login",
                 json={"email": f"nobody_{uuid.uuid4().hex[:6]}@qapilo.io",
                       "password": "wrongpw"},
                 headers={"Accept-Language": "de-DE,de;q=0.9,en;q=0.8"})
    assert r.status_code == 401
    assert r.json().get("detail") == EXPECTED["bad_credentials"]["de"]


def test_accept_language_unknown_falls_back_to_en(api):
    r = api.post(f"{BASE_URL}/api/auth/login",
                 json={"email": f"nobody_{uuid.uuid4().hex[:6]}@qapilo.io",
                       "password": "wrongpw"},
                 headers={"Accept-Language": "fr"})
    assert r.status_code == 401
    assert r.json().get("detail") == EXPECTED["bad_credentials"]["en"]
