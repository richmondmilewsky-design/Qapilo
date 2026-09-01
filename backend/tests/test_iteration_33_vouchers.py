"""
Voucher/discount-code validation feature tests.
Covers POST /api/vouchers/validate — validation only, never redeems.
Pre-seeded codes: WELCOME20, EXPIRED10, INACTIVE5, MAXEDOUT, PROONLY.
"""
import os
import pytest
import requests

BASE_URL = os.environ.get('EXPO_PUBLIC_BACKEND_URL').rstrip('/')
EMAIL = "demo@tradequest.app"
PASSWORD = "demo123"


@pytest.fixture(scope="module")
def auth_token():
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/api/auth/login", json={"email": EMAIL, "password": PASSWORD})
    if resp.status_code != 200:
        pytest.skip(f"Login failed: {resp.status_code} {resp.text}")
    token = resp.json().get("token") or resp.json().get("access_token")
    if not token:
        pytest.skip("No token in login response")
    return token


@pytest.fixture
def api_client(auth_token):
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}"})
    return session


class TestVoucherValidate:
    def test_welcome20_case_insensitive(self, api_client):
        resp = api_client.post(f"{BASE_URL}/api/vouchers/validate", json={"code": "welcome20", "plan_id": "monthly"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is True
        assert data["code"] == "WELCOME20"
        assert data["discount_percent"] == 20

    def test_expired10(self, api_client):
        resp = api_client.post(f"{BASE_URL}/api/vouchers/validate", json={"code": "EXPIRED10", "plan_id": "monthly"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is False
        assert data["reason"] == "expired"

    def test_inactive5(self, api_client):
        resp = api_client.post(f"{BASE_URL}/api/vouchers/validate", json={"code": "INACTIVE5", "plan_id": "monthly"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is False
        assert data["reason"] == "inactive"

    def test_maxedout(self, api_client):
        resp = api_client.post(f"{BASE_URL}/api/vouchers/validate", json={"code": "MAXEDOUT", "plan_id": "monthly"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is False
        assert data["reason"] == "limit_reached"

    def test_proonly_not_applicable_then_applicable(self, api_client):
        resp1 = api_client.post(f"{BASE_URL}/api/vouchers/validate", json={"code": "PROONLY", "plan_id": "lite"})
        assert resp1.status_code == 200
        data1 = resp1.json()
        assert data1["valid"] is False
        assert data1["reason"] == "not_applicable"

        resp2 = api_client.post(f"{BASE_URL}/api/vouchers/validate", json={"code": "PROONLY", "plan_id": "yearly_individual"})
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["valid"] is True
        assert data2["discount_percent"] == 25

    def test_not_found(self, api_client):
        resp = api_client.post(f"{BASE_URL}/api/vouchers/validate", json={"code": "DOESNOTEXIST", "plan_id": "monthly"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is False
        assert data["reason"] == "not_found"

    def test_unauthenticated_rejected(self):
        session = requests.Session()
        resp = session.post(f"{BASE_URL}/api/vouchers/validate", json={"code": "WELCOME20", "plan_id": "monthly"})
        assert resp.status_code in (401, 403)

    def test_redemption_count_never_incremented(self, api_client):
        # call validate several times for WELCOME20
        for _ in range(3):
            r = api_client.post(f"{BASE_URL}/api/vouchers/validate", json={"code": "WELCOME20", "plan_id": "monthly"})
            assert r.status_code == 200

        import motor.motor_asyncio
        import asyncio
        from dotenv import load_dotenv
        load_dotenv("/app/backend/.env")
        mongo_url = os.environ["MONGO_URL"]
        db_name = os.environ["DB_NAME"]

        async def check():
            client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
            db = client[db_name]
            doc = await db.discount_codes.find_one({"code": "WELCOME20"}, {"_id": 0})
            return doc

        doc = asyncio.run(check())
        assert doc is not None
        assert doc.get("redemption_count", 0) == 0
