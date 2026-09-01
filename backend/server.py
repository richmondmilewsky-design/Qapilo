import os
import uuid
import base64
import asyncio
import random
import re
import secrets
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta, date
from typing import Optional, List

import jwt
import httpx
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from dotenv import load_dotenv

from curriculum import (
    UNITS, LESSON_MAP, LESSON_ORDER, BADGES, BADGE_MAP,
    UNIT_T, LESSON_T, STOCK_T, norm_lang, LESSONS_BY_TIER, TIER_META,
)
from errors_i18n import L, set_lang_from_header, lang_ctx
from stocks import STOCKS, STOCK_MAP, CATEGORIES, fallback_quote, fallback_history
from emergentintegrations.llm.chat import LlmChat, UserMessage
import email_service as email

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

JWT_SECRET = os.environ.get("JWT_SECRET", "change-me-dev-secret")
JWT_ALG = "HS256"
JWT_EXPIRES_DAYS = 30
FINNHUB_KEY = os.environ.get("FINNHUB_API_KEY", "").strip()
TAVILY_KEY = os.environ.get("TAVILY_API_KEY", "").strip()
DAILY_GOAL_XP = 50

# --- Transactional email / password reset config ---
RESET_TOKEN_TTL_MIN = int(os.environ.get("RESET_TOKEN_TTL_MIN", "30"))
VERIFY_CODE_TTL_MIN = int(os.environ.get("VERIFY_CODE_TTL_MIN", "30"))
EMAIL_LOG_RETENTION_DAYS = int(os.environ.get("EMAIL_LOG_RETENTION_DAYS", "90"))
SUPPORT_RETENTION_DAYS = int(os.environ.get("SUPPORT_RETENTION_DAYS", "180"))
QAPILO_APP_URL = os.environ.get("QAPILO_APP_URL", "").strip().rstrip("/")
SUPPORT_EMAIL = os.environ.get("QAPILO_SUPPORT_EMAIL", "").strip()
# In-memory rate-limit buckets (email + IP) for password reset & support.
_rl_buckets: dict = {}

# --- Monetization / AI config ---
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "").strip()
CLAUDE_MODEL = "claude-sonnet-4-6"
TRIAL_DAYS = 7
# Free usage phase (no payment yet): ends after 30 days OR when the user reaches level 30.
FREE_TRIAL_DAYS = 30
FREE_LEVEL_LIMIT = 60
# Founder/team override: emails listed here (comma-separated, case-insensitive)
# always get full premium access, no subscription record required. Unset/empty
# by default — configure separately via the FOUNDER_EMAILS env var.
FOUNDER_EMAILS = {
    e.strip().lower()
    for e in os.environ.get("FOUNDER_EMAILS", "").split(",")
    if e.strip()
}
PRO_UNITS = {f"u{i}" for i in range(21, 51)}  # tiers 3-5 (advanced) gated behind Pro
FREE_TUTOR_DAILY_LIMIT = 3
PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID", "").strip()
PAYPAL_SECRET = os.environ.get("PAYPAL_SECRET", "").strip()
PAYPAL_MODE = os.environ.get("PAYPAL_MODE", "sandbox").strip()
PRO_PRICE = os.environ.get("PRO_PRICE", "4.99").strip()
PAYPAL_BASE = (
    "https://api-m.paypal.com" if PAYPAL_MODE == "live" else "https://api-m.sandbox.paypal.com"
)

# --- Sign in with Apple ---
APPLE_ISSUER = "https://appleid.apple.com"
APPLE_JWKS_URL = "https://appleid.apple.com/auth/keys"
APPLE_AUDIENCES = [
    a.strip() for a in os.environ.get("APPLE_AUDIENCES", "").split(",") if a.strip()
]
_apple_jwks_cache: dict = {"keys": None, "fetched_at": 0.0}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tradequest")

app = FastAPI()
api = APIRouter(prefix="/api")


# ----------------------------- Models -----------------------------
class SignupBody(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: Optional[str] = None
    lang: Optional[str] = "en"


class ForgotPasswordBody(BaseModel):
    email: EmailStr
    lang: Optional[str] = "en"


class ResetPasswordBody(BaseModel):
    token: str
    new_password: str
    lang: Optional[str] = "en"


class SupportBody(BaseModel):
    category: str
    subject: str
    message: str
    reply_email: Optional[EmailStr] = None
    lang: Optional[str] = "en"


class LoginBody(BaseModel):
    email: EmailStr
    password: str


class GoogleBody(BaseModel):
    session_id: str


class AppleBody(BaseModel):
    identity_token: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class CompleteBody(BaseModel):
    correct: int
    total: int


class AcceptTermsBody(BaseModel):
    # Required consents
    accepted_terms: bool = True
    accepted_disclaimer: bool = True
    # Optional (voluntary) consents — default off
    consent_analytics: bool = False
    consent_product: bool = False
    consent_marketing: bool = False


class ConsentsBody(BaseModel):
    consent_analytics: bool
    consent_product: bool
    consent_marketing: bool


class VerifyEmailBody(BaseModel):
    code: str
    lang: Optional[str] = "en"


class ResendVerificationBody(BaseModel):
    lang: Optional[str] = "en"


class ExperienceBody(BaseModel):
    experience_level: str


# ----------------------------- Helpers -----------------------------
def make_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": user_id, "iat": now, "exp": now + timedelta(days=JWT_EXPIRES_DAYS)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def level_for_xp(xp: int) -> int:
    # 100 XP per level, level 1 at 0 XP
    return xp // 100 + 1


def xp_into_level(xp: int) -> dict:
    lvl = level_for_xp(xp)
    floor_xp = (lvl - 1) * 100
    return {"level": lvl, "current": xp - floor_xp, "needed": 100}


def today_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


LANG_NAMES = {"en": "English", "de": "German (Deutsch)", "es": "Spanish (Español)"}


def loc_unit(u: dict, lang: str) -> dict:
    t = UNIT_T.get(lang, {}).get(u["id"])
    if t:
        return {"title": t["title"], "subtitle": t["subtitle"]}
    return {"title": u["title"], "subtitle": u["subtitle"]}


def loc_lesson_title(lesson_id: str, default: str, lang: str) -> str:
    t = LESSON_T.get(lang, {}).get(lesson_id)
    return t["title"] if t else default


def _shuffle_options(q: dict) -> dict:
    """Return a copy of a question dict with option order randomized and
    the answer index remapped to match the new order."""
    order = list(range(len(q["options"])))
    random.shuffle(order)
    return {
        **q,
        "options": [q["options"][i] for i in order],
        "answer": order.index(q["answer"]),
    }


def loc_lesson_full(l: dict, lang: str) -> dict:
    """Return localized title, cards and questions. Answer indices come from the
    English source (l) so translated option order must match. Option order is
    then randomized per-request so the correct answer isn't always at a fixed
    position."""
    t = LESSON_T.get(lang, {}).get(l["id"])
    if not t:
        return {"title": l["title"], "cards": l["cards"],
                "questions": [_shuffle_options(q) for q in l["questions"]]}
    questions = []
    for i, q in enumerate(l["questions"]):
        tq = t["questions"][i]
        questions.append(_shuffle_options({"q": tq["q"], "options": tq["options"],
                          "answer": q["answer"], "explain": tq["explain"]}))
    return {"title": t["title"], "cards": t["cards"], "questions": questions}


def loc_stock_explain(symbol: str, default: str, lang: str) -> str:
    return STOCK_T.get(lang, {}).get(symbol, default)


def _parse_dt(v):
    if not v:
        return None
    if isinstance(v, datetime):
        return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
    try:
        d = datetime.fromisoformat(v)
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def compute_pro(u: dict) -> dict:
    """Single source of truth for access state.

    Free usage phase is active until EITHER 30 days elapse (trial_ends_at)
    OR the user reaches level 60. A paid subscription (pro_active) always
    grants premium access. Returns a clear internal status only — the full
    paywall / enforcement UI is a separate step.
    """
    now = datetime.now(timezone.utc)
    trial_end = _parse_dt(u.get("trial_ends_at"))
    trial_start = _parse_dt(u.get("trial_started_at")) or _parse_dt(u.get("created_at"))
    sub_active = bool(u.get("pro_active", False))
    has_sub_history = bool(u.get("subscription_id") or u.get("subscription_status"))
    is_founder = u.get("email", "").lower() in FOUNDER_EMAILS

    # Self-heal: a missing/unparseable trial_ends_at (e.g. an account created
    # before this field existed, or inserted through a path that skipped it)
    # must never look like an immediately-ended trial. Grant a fresh 30-day
    # window starting now and persist it, so the record self-heals without a
    # manual migration. Users who genuinely have an expired trial_ends_at in
    # the past are unaffected (trial_end is not None for them), and users
    # with any subscription history keep their real "ended" status.
    if trial_end is None and not sub_active and not has_sub_history:
        trial_start = now
        trial_end = now + timedelta(days=FREE_TRIAL_DAYS)
        u["trial_started_at"] = trial_start.isoformat()
        u["trial_ends_at"] = trial_end.isoformat()
        user_id = u.get("user_id")
        if user_id:
            asyncio.ensure_future(db.users.update_one(
                {"user_id": user_id},
                {"$set": {"trial_started_at": u["trial_started_at"], "trial_ends_at": u["trial_ends_at"]}},
            ))

    level = xp_into_level(u.get("xp", 0))["level"]

    time_active = bool(trial_end and now < trial_end)
    level_active = level < FREE_LEVEL_LIMIT
    trial_active = time_active and level_active
    is_pro = sub_active or trial_active or is_founder

    # Why the free phase ended (drives the upcoming paywall messaging).
    trial_end_reason = None
    if not sub_active and not trial_active and not is_founder:
        if trial_end and now >= trial_end:
            trial_end_reason = "time"
        elif not level_active:
            trial_end_reason = "level"

    if is_founder:
        trial_status, source = "premium", "founder"
    elif sub_active:
        trial_status, source = "premium", "subscription"
    elif trial_active:
        trial_status, source = "active", "trial"
    else:
        trial_status, source = "ended", "free"

    trial_days_left = (trial_end - now).days + 1 if time_active else 0
    return {
        "is_pro": is_pro,
        "pro_source": source,
        "in_trial": trial_active,
        "trial_status": trial_status,          # active | ended | premium
        "trial_end_reason": trial_end_reason,   # None | "time" | "level"
        "trial_days_left": trial_days_left,
        "trial_started_at": (trial_start.isoformat() if trial_start else u.get("created_at")),
        "trial_ends_at": u.get("trial_ends_at"),
        "current_level": level,
        "free_level_limit": FREE_LEVEL_LIMIT,
        "subscription_status": u.get("subscription_status"),
    }


def public_user(u: dict) -> dict:
    xp = u.get("xp", 0)
    prog = xp_into_level(xp)
    return {
        "user_id": u["user_id"],
        "email": u.get("email"),
        "name": u.get("name") or (u.get("email", "").split("@")[0] if u.get("email") else "Investor"),
        "picture": u.get("picture"),
        "xp": xp,
        "level": prog["level"],
        "level_current": prog["current"],
        "level_needed": prog["needed"],
        "streak": u.get("streak", 0),
        "longest_streak": u.get("longest_streak", 0),
        "completed_lessons": u.get("completed_lessons", []),
        "perfect_lessons": u.get("perfect_lessons", []),
        "badges": u.get("badges", []),
        "daily_xp": u.get("daily_xp", 0) if u.get("daily_date") == today_str() else 0,
        "daily_goal": DAILY_GOAL_XP,
        "auth_provider": u.get("auth_provider", "password"),
        "email_verified": u.get("email_verified", True),
        "created_at": u.get("created_at"),
        "accepted_terms": u.get("accepted_terms", False),
        "accepted_disclaimer": u.get("accepted_disclaimer", False),
        "experience_level": u.get("experience_level"),
        "consent_analytics": u.get("consent_analytics", False),
        "consent_product": u.get("consent_product", False),
        "consent_marketing": u.get("consent_marketing", False),
        "consent_marketing_confirmed_at": u.get("consent_marketing_confirmed_at"),
        "consent_marketing_ip": u.get("consent_marketing_ip"),
        **compute_pro(u),
    }


async def get_current_user(request: Request) -> dict:
    auth = request.headers.get("Authorization", "")
    if not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail=L("not_authenticated"))
    token = auth.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail=L("invalid_token"))
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail=L("user_not_found"))
    # Session invalidation after password reset: reject tokens issued before the reset.
    inv = user.get("sessions_invalid_before")
    if inv:
        iat = payload.get("iat", 0)
        if isinstance(iat, (int, float)) and iat < inv:
            raise HTTPException(status_code=401, detail=L("invalid_token"))
    return user


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


async def _issue_email_code(user_id: str, user_email: str, lang: str):
    """Generate a 6-digit email-verification code, store only its hash with an
    expiry, and send it via the transactional email service."""
    code = f"{secrets.randbelow(1_000_000):06d}"
    await db.email_verifications.delete_many({"user_id": user_id})
    await db.email_verifications.insert_one({
        "user_id": user_id,
        "code_hash": _hash_token(code),
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=VERIFY_CODE_TTL_MIN),
        "attempts": 0,
    })
    asyncio.create_task(email.send_and_log(
        db, "email_verification", lang, user_email, user_id,
        {"code": code, "ttl": VERIFY_CODE_TTL_MIN}))


async def _issue_marketing_code(user_id: str, user_email: str, lang: str):
    """Generate a 6-digit marketing-consent (double opt-in) confirmation code,
    store only its hash with an expiry, and send it via the transactional email
    service. Mirrors _issue_email_code but uses its own collection/template so
    the account email-verification flow stays completely untouched."""
    code = f"{secrets.randbelow(1_000_000):06d}"
    await db.marketing_consents.delete_many({"user_id": user_id})
    await db.marketing_consents.insert_one({
        "user_id": user_id,
        "code_hash": _hash_token(code),
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=VERIFY_CODE_TTL_MIN),
        "attempts": 0,
    })
    asyncio.create_task(email.send_and_log(
        db, "marketing_confirmation", lang, user_email, user_id,
        {"code": code, "ttl": VERIFY_CODE_TTL_MIN}))


def _rate_limited(key: str, limit: int, window_sec: int) -> bool:
    """Return True if `key` has exceeded `limit` events within `window_sec`."""
    import time
    now = time.time()
    bucket = [t for t in _rl_buckets.get(key, []) if now - t < window_sec]
    if len(bucket) >= limit:
        _rl_buckets[key] = bucket
        return True
    bucket.append(now)
    _rl_buckets[key] = bucket
    return False


async def ensure_indexes():
    await db.users.create_index("email", unique=True, sparse=True)
    await db.users.create_index("user_id", unique=True)
    await db.password_resets.create_index("expires_at", expireAfterSeconds=0)
    await db.email_verifications.create_index("expires_at", expireAfterSeconds=0)
    await db.marketing_consents.create_index("expires_at", expireAfterSeconds=0)
    await db.lesson_memory.create_index([("user_id", 1), ("lesson_id", 1)], unique=True)
    await db.duels.create_index("duel_id", unique=True)
    await db.duels.create_index("expires_at", expireAfterSeconds=0)
    await db.discount_codes.create_index("code", unique=True)
    await db.email_events.create_index(
        "created_at", expireAfterSeconds=EMAIL_LOG_RETENTION_DAYS * 86400)
    await db.support_requests.create_index(
        "created_at", expireAfterSeconds=SUPPORT_RETENTION_DAYS * 86400)


SEED_BOTS = [
    ("Ava Chen", 640, 9), ("Marcus Bell", 480, 5), ("Priya Nair", 355, 4),
    ("Diego Torres", 220, 3), ("Lena Wolf", 120, 2),
]


async def seed_bots():
    for name, xp, streak in SEED_BOTS:
        email = name.lower().replace(" ", ".") + "@demo.tradequest"
        existing = await db.users.find_one({"email": email})
        if existing:
            continue
        await db.users.insert_one({
            "user_id": f"user_{uuid.uuid4().hex[:12]}",
            "email": email, "name": name, "picture": None,
            "hashed_password": None, "auth_provider": "bot",
            "xp": xp, "streak": streak, "longest_streak": streak,
            "completed_lessons": [], "perfect_lessons": [], "badges": [],
            "daily_xp": 0, "daily_date": today_str(), "last_active": today_str(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        })


@app.on_event("startup")
async def _startup():
    await ensure_indexes()
    await seed_bots()


@app.on_event("shutdown")
async def _shutdown():
    client.close()


# ----------------------------- Auth -----------------------------
@api.post("/auth/signup")
async def signup(body: SignupBody):
    existing = await db.users.find_one({"email": body.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail=L("email_taken"))
    user = {
        "user_id": f"user_{uuid.uuid4().hex[:12]}",
        "email": body.email.lower(),
        "name": body.name or body.email.split("@")[0],
        "picture": None,
        "hashed_password": pwd_context.hash(body.password),
        "auth_provider": "password",
        "xp": 0, "streak": 0, "longest_streak": 0,
        "completed_lessons": [], "perfect_lessons": [], "badges": [],
        "daily_xp": 0, "daily_date": today_str(),
        "last_active": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "trial_started_at": datetime.now(timezone.utc).isoformat(),
        "trial_ends_at": (datetime.now(timezone.utc) + timedelta(days=FREE_TRIAL_DAYS)).isoformat(),
        "pro_active": False, "subscription_id": None, "subscription_status": None,
        "accepted_terms": False,
        "email_verified": False,
    }
    await db.users.insert_one(user)
    asyncio.create_task(email.send_and_log(
        db, "trial_started", (body.lang or "en"), user["email"], user["user_id"],
        {"days": FREE_TRIAL_DAYS}))
    await _issue_email_code(user["user_id"], user["email"], body.lang or "en")
    return {"token": make_token(user["user_id"]), "user": public_user(user)}


@api.post("/auth/login")
async def login(body: LoginBody):
    user = await db.users.find_one({"email": body.email.lower()})
    dummy = pwd_context.hash("dummy-timing-guard")
    if not user or not user.get("hashed_password"):
        pwd_context.verify(body.password, dummy)
        raise HTTPException(status_code=401, detail=L("bad_credentials"))
    if not pwd_context.verify(body.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail=L("bad_credentials"))
    return {"token": make_token(user["user_id"]), "user": public_user(user)}


@api.post("/auth/google")
async def google_auth(body: GoogleBody):
    async with httpx.AsyncClient(timeout=20) as hc:
        r = await hc.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": body.session_id},
        )
    if r.status_code != 200:
        raise HTTPException(status_code=401, detail=L("google_invalid"))
    data = r.json()
    email = data["email"].lower()
    user = await db.users.find_one({"email": email})
    if not user:
        user = {
            "user_id": f"user_{uuid.uuid4().hex[:12]}",
            "email": email,
            "name": data.get("name") or email.split("@")[0],
            "picture": data.get("picture"),
            "hashed_password": None,
            "auth_provider": "google",
            "xp": 0, "streak": 0, "longest_streak": 0,
            "completed_lessons": [], "perfect_lessons": [], "badges": [],
            "daily_xp": 0, "daily_date": today_str(),
            "last_active": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "trial_started_at": datetime.now(timezone.utc).isoformat(),
            "trial_ends_at": (datetime.now(timezone.utc) + timedelta(days=FREE_TRIAL_DAYS)).isoformat(),
            "pro_active": False, "subscription_id": None, "subscription_status": None,
            "accepted_terms": False,
        }
        await db.users.insert_one(user)
    else:
        # refresh profile picture/name from google
        await db.users.update_one(
            {"user_id": user["user_id"]},
            {"$set": {"picture": data.get("picture"), "name": user.get("name") or data.get("name")}},
        )
        user = await db.users.find_one({"user_id": user["user_id"]})
    return {"token": make_token(user["user_id"]), "user": public_user(user)}


async def _apple_jwks() -> dict:
    """Fetch Apple's public JWKS, cached for 24h."""
    import time
    now = time.time()
    if not _apple_jwks_cache["keys"] or now - _apple_jwks_cache["fetched_at"] > 86400:
        async with httpx.AsyncClient(timeout=15) as hc:
            r = await hc.get(APPLE_JWKS_URL)
        r.raise_for_status()
        _apple_jwks_cache["keys"] = r.json().get("keys", [])
        _apple_jwks_cache["fetched_at"] = now
    return _apple_jwks_cache["keys"]


async def verify_apple_token(identity_token: str) -> dict:
    """Verify an Apple identity token against Apple's JWKS (RS256).
    Checks signature, issuer, audience and expiry. Returns the decoded claims."""
    try:
        header = jwt.get_unverified_header(identity_token)
    except Exception:
        raise HTTPException(status_code=401, detail=L("apple_invalid"))
    keys = await _apple_jwks()
    jwk = next((k for k in keys if k.get("kid") == header.get("kid")), None)
    if not jwk:
        raise HTTPException(status_code=401, detail=L("apple_invalid"))
    try:
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
        claims = jwt.decode(
            identity_token,
            public_key,
            algorithms=["RS256"],
            audience=APPLE_AUDIENCES if APPLE_AUDIENCES else None,
            issuer=APPLE_ISSUER,
            options={"verify_aud": bool(APPLE_AUDIENCES)},
        )
    except Exception:
        raise HTTPException(status_code=401, detail=L("apple_invalid"))
    return claims


@api.post("/auth/apple")
async def apple_auth(body: AppleBody):
    claims = await verify_apple_token(body.identity_token)
    apple_sub = claims.get("sub")
    if not apple_sub:
        raise HTTPException(status_code=401, detail=L("apple_invalid"))
    # Email may come from the token (first sign-in) or the client payload.
    email = (claims.get("email") or (body.email or "")).lower() or None

    user = await db.users.find_one({"apple_sub": apple_sub})
    if not user and email:
        # Link to an existing account with the same email if present.
        user = await db.users.find_one({"email": email})
        if user:
            await db.users.update_one(
                {"user_id": user["user_id"]}, {"$set": {"apple_sub": apple_sub}}
            )
            user = await db.users.find_one({"user_id": user["user_id"]})

    if not user:
        display_name = (body.name or (email.split("@")[0] if email else "Investor"))
        user = {
            "user_id": f"user_{uuid.uuid4().hex[:12]}",
            "email": email,
            "apple_sub": apple_sub,
            "name": display_name,
            "picture": None,
            "hashed_password": None,
            "auth_provider": "apple",
            "xp": 0, "streak": 0, "longest_streak": 0,
            "completed_lessons": [], "perfect_lessons": [], "badges": [],
            "daily_xp": 0, "daily_date": today_str(),
            "last_active": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "trial_started_at": datetime.now(timezone.utc).isoformat(),
            "trial_ends_at": (datetime.now(timezone.utc) + timedelta(days=FREE_TRIAL_DAYS)).isoformat(),
            "pro_active": False, "subscription_id": None, "subscription_status": None,
            "accepted_terms": False,
        }
        await db.users.insert_one(user)
    return {"token": make_token(user["user_id"]), "user": public_user(user)}



@api.get("/auth/me")
async def me(user: dict = Depends(get_current_user)):
    return {"user": public_user(user)}


@api.post("/auth/logout")
async def logout(user: dict = Depends(get_current_user)):
    return {"ok": True}


@api.post("/auth/verify-email")
async def verify_email(body: VerifyEmailBody, user: dict = Depends(get_current_user)):
    """Confirm the user's email with the 6-digit code they received (non-blocking)."""
    if user.get("email_verified", True):
        fresh = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
        return {"user": public_user(fresh)}
    code = (body.code or "").strip()
    rec = await db.email_verifications.find_one({"user_id": user["user_id"]})
    if not rec:
        raise HTTPException(status_code=400, detail=L("verify_invalid"))
    exp = rec.get("expires_at")
    if exp is not None and exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if not exp or exp < datetime.now(timezone.utc):
        await db.email_verifications.delete_many({"user_id": user["user_id"]})
        raise HTTPException(status_code=400, detail=L("verify_invalid"))
    if rec.get("attempts", 0) >= 6:
        await db.email_verifications.delete_many({"user_id": user["user_id"]})
        raise HTTPException(status_code=429, detail=L("rate_limited"))
    if _hash_token(code) != rec.get("code_hash"):
        await db.email_verifications.update_one({"_id": rec["_id"]}, {"$inc": {"attempts": 1}})
        raise HTTPException(status_code=400, detail=L("verify_invalid"))
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"email_verified": True,
                  "email_verified_at": datetime.now(timezone.utc).isoformat()}},
    )
    await db.email_verifications.delete_many({"user_id": user["user_id"]})
    fresh = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    return {"user": public_user(fresh)}


@api.post("/auth/resend-verification")
async def resend_verification(body: ResendVerificationBody, user: dict = Depends(get_current_user)):
    if user.get("email_verified", True):
        return {"ok": True}
    if _rate_limited(f"verify:{user['user_id']}", 3, 900):
        raise HTTPException(status_code=429, detail=L("rate_limited"))
    await _issue_email_code(user["user_id"], user["email"], body.lang or "en")
    return {"ok": True, "message": L("verify_sent")}


@api.patch("/auth/experience")
async def set_experience(body: ExperienceBody, user: dict = Depends(get_current_user)):
    """One-time (and later editable) learning experience level selection."""
    level = (body.experience_level or "").strip()
    if level not in ("beginner", "some", "advanced"):
        raise HTTPException(status_code=400, detail=L("bad_request"))
    await db.users.update_one(
        {"user_id": user["user_id"]}, {"$set": {"experience_level": level}}
    )
    fresh = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    return {"user": public_user(fresh)}


@api.post("/auth/accept-terms")
async def accept_terms(body: AcceptTermsBody, user: dict = Depends(get_current_user)):
    # Terms of Service and the financial disclaimer are mandatory to proceed.
    if not (body.accepted_terms and body.accepted_disclaimer):
        raise HTTPException(status_code=400, detail=L("consent_required"))
    now = datetime.now(timezone.utc).isoformat()
    set_fields = {
        "accepted_terms": True,
        "accepted_disclaimer": True,
        "consent_analytics": body.consent_analytics,
        "consent_product": body.consent_product,
        "terms_accepted_at": now,
        "consents_updated_at": now,
    }
    pending = False
    if body.consent_marketing and not user.get("consent_marketing", False):
        # Double opt-in: marketing consent only becomes true after the user
        # confirms an emailed code (see /auth/confirm-marketing-consent).
        await _issue_marketing_code(user["user_id"], user["email"], lang_ctx.get())
        pending = True
    else:
        set_fields["consent_marketing"] = body.consent_marketing
    await db.users.update_one({"user_id": user["user_id"]}, {"$set": set_fields})
    fresh = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    result = public_user(fresh)
    if pending:
        result["consent_marketing_pending"] = True
    return {"user": result}


@api.patch("/auth/consents")
async def update_consents(body: ConsentsBody, user: dict = Depends(get_current_user)):
    """GDPR right to withdraw: update the optional (voluntary) consents anytime.
    Marketing opt-in requires double opt-in confirmation via an emailed code;
    opting out always stays immediate, no confirmation needed."""
    set_fields = {
        "consent_analytics": body.consent_analytics,
        "consent_product": body.consent_product,
        "consents_updated_at": datetime.now(timezone.utc).isoformat(),
    }
    pending = False
    if body.consent_marketing and not user.get("consent_marketing", False):
        await _issue_marketing_code(user["user_id"], user["email"], lang_ctx.get())
        pending = True
    else:
        set_fields["consent_marketing"] = body.consent_marketing
    await db.users.update_one({"user_id": user["user_id"]}, {"$set": set_fields})
    fresh = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    result = public_user(fresh)
    if pending:
        result["consent_marketing_pending"] = True
    return {"user": result}


@api.post("/auth/confirm-marketing-consent")
async def confirm_marketing_consent(body: VerifyEmailBody, request: Request, user: dict = Depends(get_current_user)):
    """Confirm the optional marketing/newsletter consent (double opt-in) with the
    6-digit code emailed to the user. Follows the exact validation logic of
    verify_email (expiry, attempt limit, rate limiting)."""
    if user.get("consent_marketing", False):
        fresh = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
        return {"user": public_user(fresh)}
    if _rate_limited(f"mktg_confirm:{user['user_id']}", 6, 900):
        raise HTTPException(status_code=429, detail=L("rate_limited"))
    code = (body.code or "").strip()
    rec = await db.marketing_consents.find_one({"user_id": user["user_id"]})
    if not rec:
        raise HTTPException(status_code=400, detail=L("verify_invalid"))
    exp = rec.get("expires_at")
    if exp is not None and exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if not exp or exp < datetime.now(timezone.utc):
        await db.marketing_consents.delete_many({"user_id": user["user_id"]})
        raise HTTPException(status_code=400, detail=L("verify_invalid"))
    if rec.get("attempts", 0) >= 6:
        await db.marketing_consents.delete_many({"user_id": user["user_id"]})
        raise HTTPException(status_code=429, detail=L("rate_limited"))
    if _hash_token(code) != rec.get("code_hash"):
        await db.marketing_consents.update_one({"_id": rec["_id"]}, {"$inc": {"attempts": 1}})
        raise HTTPException(status_code=400, detail=L("verify_invalid"))
    ip = (request.client.host if request.client else "unknown")
    now = datetime.now(timezone.utc).isoformat()
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"consent_marketing": True,
                  "consent_marketing_confirmed_at": now,
                  "consent_marketing_ip": ip,
                  "consents_updated_at": now}},
    )
    await db.marketing_consents.delete_many({"user_id": user["user_id"]})
    fresh = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    return {"user": public_user(fresh)}


@api.post("/auth/resend-marketing-code")
async def resend_marketing_code(body: ResendVerificationBody, user: dict = Depends(get_current_user)):
    """Resend the marketing-consent confirmation code, mirroring
    resend_verification (same 3-per-15min rate limit)."""
    if user.get("consent_marketing", False):
        return {"ok": True}
    if _rate_limited(f"mktg:{user['user_id']}", 3, 900):
        raise HTTPException(status_code=429, detail=L("rate_limited"))
    await _issue_marketing_code(user["user_id"], user["email"], body.lang or "en")
    return {"ok": True, "message": L("verify_sent")}


# ----------------------------- Curriculum -----------------------------
@api.get("/curriculum")
async def curriculum(lang: str = "en", user: dict = Depends(get_current_user)):
    lang = norm_lang(lang)
    completed = set(user.get("completed_lessons", []))
    is_pro = compute_pro(user)["is_pro"]
    units_out = []
    prev_done = True  # first lesson always unlocked
    for u in UNITS:
        unit_pro = u["id"] in PRO_UNITS
        ut = loc_unit(u, lang)
        lessons_out = []
        for l in u["lessons"]:
            is_done = l["id"] in completed
            pro_locked = unit_pro and not is_pro
            unlocked = (prev_done or is_done) and not pro_locked
            lessons_out.append({
                "id": l["id"], "title": loc_lesson_title(l["id"], l["title"], lang),
                "icon": l["icon"], "xp": l["xp"],
                "completed": is_done, "unlocked": unlocked,
                "pro_locked": pro_locked,
                "perfect": l["id"] in set(user.get("perfect_lessons", [])),
            })
            prev_done = is_done
        units_out.append({
            "id": u["id"], "title": ut["title"], "subtitle": ut["subtitle"],
            "color": u["color"], "tier": u.get("tier", 1),
            "lessons": lessons_out, "pro": unit_pro,
        })
    total = len(LESSON_ORDER)
    return {
        "units": units_out,
        "total_lessons": total,
        "completed_count": len(completed),
        "is_pro": is_pro,
    }


@api.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: str, lang: str = "en", user: dict = Depends(get_current_user)):
    l = LESSON_MAP.get(lesson_id)
    if not l:
        raise HTTPException(status_code=404, detail=L("lesson_not_found"))
    if l["unit_id"] in PRO_UNITS and not compute_pro(user)["is_pro"]:
        raise HTTPException(status_code=403, detail=L("lesson_pro"))
    loc = loc_lesson_full(l, norm_lang(lang))
    return {
        "id": l["id"], "title": loc["title"], "icon": l["icon"], "xp": l["xp"],
        "unit_title": l["unit_title"], "unit_color": l["unit_color"],
        "cards": loc["cards"], "questions": loc["questions"],
    }


def evaluate_badges(u: dict) -> List[str]:
    earned = set(u.get("badges", []))
    new = []
    completed = u.get("completed_lessons", [])
    perfect = u.get("perfect_lessons", [])

    def award(bid):
        if bid not in earned:
            earned.add(bid)
            new.append(bid)

    if len(completed) >= 1:
        award("first_step")
    if u.get("streak", 0) >= 3:
        award("streak_3")
    if u.get("streak", 0) >= 7:
        award("streak_7")
    if u.get("streak", 0) >= 30:
        award("streak_30")
    if u.get("streak", 0) >= 100:
        award("streak_100")
    if len(perfect) >= 1:
        award("perfectionist")
    if len(completed) >= max(8, len(LESSON_ORDER) // 2):
        award("half_way")
    if len(completed) >= len(LESSON_ORDER):
        award("graduate")
    if level_for_xp(u.get("xp", 0)) >= 5:
        award("level_5")
    if u.get("xp", 0) >= 500:
        award("xp_500")
    u["badges"] = list(earned)
    return new


@api.post("/lessons/{lesson_id}/complete")
async def complete_lesson(lesson_id: str, body: CompleteBody, user: dict = Depends(get_current_user)):
    l = LESSON_MAP.get(lesson_id)
    if not l:
        raise HTTPException(status_code=404, detail=L("lesson_not_found"))

    completed = list(user.get("completed_lessons", []))
    perfect = list(user.get("perfect_lessons", []))
    first_time = lesson_id not in completed

    # XP: full reward first time, quarter reward for replays. Scale by accuracy.
    accuracy = body.correct / body.total if body.total else 0

    # Lightweight heuristic half-life memory model (Duolingo HLR-inspired, fixed
    # heuristics, no ML). Pure side-effect write — does not affect the response.
    mem = await db.lesson_memory.find_one({"user_id": user["user_id"], "lesson_id": lesson_id})
    now_dt = datetime.now(timezone.utc)
    if not mem:
        new_half_life = 1.0
    elif accuracy >= 0.6:
        new_half_life = min(60.0, mem.get("half_life_days", 1.0) * 2)
    else:
        new_half_life = max(0.5, mem.get("half_life_days", 1.0) / 2)
    await db.lesson_memory.update_one(
        {"user_id": user["user_id"], "lesson_id": lesson_id},
        {"$set": {"half_life_days": new_half_life, "last_seen_at": now_dt}},
        upsert=True,
    )

    base_xp = l["xp"]
    earned_xp = round(base_xp * (0.5 + 0.5 * accuracy))
    if not first_time:
        earned_xp = max(5, earned_xp // 4)

    is_perfect = body.correct == body.total and body.total > 0

    # Streak logic
    today = today_str()
    last = user.get("last_active")
    streak = user.get("streak", 0)
    if last != today:
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        if last == yesterday:
            streak += 1
        else:
            streak = 1

    # Daily XP
    daily_date = user.get("daily_date")
    daily_xp = user.get("daily_xp", 0)
    if daily_date != today:
        daily_xp = 0
    daily_xp += earned_xp

    new_xp = user.get("xp", 0) + earned_xp
    longest = max(user.get("longest_streak", 0), streak)

    if first_time:
        completed.append(lesson_id)
    if is_perfect and lesson_id not in perfect:
        perfect.append(lesson_id)

    updated = {
        **user,
        "xp": new_xp,
        "streak": streak,
        "longest_streak": longest,
        "completed_lessons": completed,
        "perfect_lessons": perfect,
        "daily_xp": daily_xp,
        "daily_date": today,
        "last_active": today,
    }
    new_badges = evaluate_badges(updated)

    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {
            "xp": new_xp, "streak": streak, "longest_streak": longest,
            "completed_lessons": completed, "perfect_lessons": perfect,
            "daily_xp": daily_xp, "daily_date": today, "last_active": today,
            "badges": updated["badges"],
        }},
    )

    return {
        "earned_xp": earned_xp,
        "first_time": first_time,
        "perfect": is_perfect,
        "new_badges": [BADGE_MAP[b] for b in new_badges],
        "user": public_user(updated),
    }


class PracticeBody(BaseModel):
    correct: int
    total: int
    tier: Optional[int] = 1
    lang: Optional[str] = "en"


@api.get("/practice")
async def practice_session(lang: str = "en", user: dict = Depends(get_current_user)):
    """Endless practice: 5 mixed questions drawn from the tiers the learner has
    reached. Difficulty (and XP reward) rises as the user levels up."""
    lang = norm_lang(lang)
    completed = set(user.get("completed_lessons", []))
    level = level_for_xp(user.get("xp", 0))
    # Higher level unlocks harder tiers; also unlock a tier once a lesson in it is done.
    max_tier = min(5, max(1, 1 + level // 3))
    for lid in completed:
        max_tier = max(max_tier, LESSON_MAP.get(lid, {}).get("tier", 1))
    max_tier = min(5, max_tier)

    # Heuristic half-life memory model: lessons the learner is likely to have
    # forgotten (low recall probability) are prioritized before the tier pool.
    due_lessons = []
    if completed:
        now_dt = datetime.now(timezone.utc)
        mem_records = await db.lesson_memory.find(
            {"user_id": user["user_id"], "lesson_id": {"$in": list(completed)}}
        ).to_list(1000)
        scored = []
        for m in mem_records:
            last_seen = m.get("last_seen_at")
            if last_seen is None:
                continue
            if last_seen.tzinfo is None:
                last_seen = last_seen.replace(tzinfo=timezone.utc)
            half_life = max(0.5, m.get("half_life_days", 1.0))
            days_elapsed = max(0.0, (now_dt - last_seen).total_seconds() / 86400)
            p = 2 ** (-days_elapsed / half_life)
            if p < 0.7:
                scored.append((p, m["lesson_id"]))
        scored.sort(key=lambda x: x[0])
        due_lessons = [lid for _, lid in scored if lid in LESSON_MAP]

    pool = [lid for lid, l in LESSON_MAP.items() if l["tier"] <= max_tier] or list(LESSON_MAP.keys())
    random.shuffle(pool)
    # Due-for-review lessons first (most-forgotten first), then the existing
    # tier-based pool exactly as before (skipping ids already covered above).
    due_set = set(due_lessons)
    ordered_pool = due_lessons + [lid for lid in pool if lid not in due_set]
    questions, used, tiers_used = [], set(), []
    for lid in ordered_pool:
        l = LESSON_MAP[lid]
        qs = loc_lesson_full(l, lang)["questions"]
        if not qs:
            continue
        q = random.choice(qs)
        if q["q"] in used:
            continue
        used.add(q["q"])
        questions.append({"q": q["q"], "options": q["options"], "answer": q["answer"],
                          "explain": q["explain"], "tier": l["tier"]})
        tiers_used.append(l["tier"])
        if len(questions) >= 5:
            break
    avg_tier = round(sum(tiers_used) / len(tiers_used)) if tiers_used else 1
    return {
        "questions": questions,
        "reward_xp": 15 + avg_tier * 5,
        "tier": avg_tier,
        "max_tier": max_tier,
        "practice_level": level,
    }


@api.post("/practice/complete")
async def practice_complete(body: PracticeBody, user: dict = Depends(get_current_user)):
    accuracy = body.correct / body.total if body.total else 0
    tier = max(1, min(5, body.tier or 1))
    earned_xp = max(5, round((15 + tier * 5) * (0.4 + 0.6 * accuracy)))

    today = today_str()
    last = user.get("last_active")
    streak = user.get("streak", 0)
    if last != today:
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        streak = streak + 1 if last == yesterday else 1

    daily_date = user.get("daily_date")
    daily_xp = user.get("daily_xp", 0)
    if daily_date != today:
        daily_xp = 0
    daily_xp += earned_xp

    new_xp = user.get("xp", 0) + earned_xp
    longest = max(user.get("longest_streak", 0), streak)
    practice_count = user.get("practice_count", 0) + 1

    updated = {
        **user, "xp": new_xp, "streak": streak, "longest_streak": longest,
        "daily_xp": daily_xp, "daily_date": today, "last_active": today,
        "practice_count": practice_count,
    }
    new_badges = evaluate_badges(updated)
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {
            "xp": new_xp, "streak": streak, "longest_streak": longest,
            "daily_xp": daily_xp, "daily_date": today, "last_active": today,
            "practice_count": practice_count, "badges": updated["badges"],
        }},
    )
    return {
        "earned_xp": earned_xp,
        "perfect": body.correct == body.total and body.total > 0,
        "new_badges": [BADGE_MAP[b] for b in new_badges],
        "user": public_user(updated),
    }


# ----------------------------- Duels (async quiz challenges) -----------------------------
class DuelCompleteBody(BaseModel):
    correct: int
    total: int


def _build_duel_question_set(max_tier: int, lang: str):
    """Draw a fixed 5-question set using the exact same tier/pool logic as
    practice_session (same max_tier, same pool filtering, same dedup-by-text
    approach), but also return the {lesson_id, tier, q_index} needed to
    re-localize the same fixed set for any player/language later."""
    pool = [lid for lid, l in LESSON_MAP.items() if l["tier"] <= max_tier] or list(LESSON_MAP.keys())
    random.shuffle(pool)
    items, questions, used = [], [], set()
    for lid in pool:
        l = LESSON_MAP[lid]
        qs = loc_lesson_full(l, lang)["questions"]
        if not qs:
            continue
        q_index = random.randrange(len(qs))
        q = qs[q_index]
        if q["q"] in used:
            continue
        used.add(q["q"])
        items.append({"lesson_id": lid, "tier": l["tier"], "q_index": q_index})
        questions.append({"q": q["q"], "options": q["options"], "answer": q["answer"],
                          "explain": q["explain"], "tier": l["tier"]})
        if len(questions) >= 5:
            break
    return items, questions


@api.post("/duels")
async def create_duel(lang: str = "en", user: dict = Depends(get_current_user)):
    """Create a fixed 5-question async duel that can be shared via duel_id and
    played later by a second user. No XP/reward coupling in this version."""
    lang = norm_lang(lang)
    completed = set(user.get("completed_lessons", []))
    level = level_for_xp(user.get("xp", 0))
    max_tier = min(5, max(1, 1 + level // 3))
    for lid in completed:
        max_tier = max(max_tier, LESSON_MAP.get(lid, {}).get("tier", 1))
    max_tier = min(5, max_tier)

    items, questions = _build_duel_question_set(max_tier, lang)

    duel_id = secrets.token_hex(4)
    now = datetime.now(timezone.utc)
    await db.duels.insert_one({
        "duel_id": duel_id,
        "creator_user_id": user["user_id"],
        "items": items,
        "creator_result": None,
        "opponent_user_id": None,
        "opponent_result": None,
        "created_at": now,
        "expires_at": now + timedelta(days=7),
    })
    return {"duel_id": duel_id, "questions": questions}


@api.get("/duels/{duel_id}")
async def get_duel(duel_id: str, lang: str = "en", user: dict = Depends(get_current_user)):
    """Fetch a duel's fixed question set, re-localized for the requesting
    user's language, plus whatever results exist so far."""
    lang = norm_lang(lang)
    duel = await db.duels.find_one({"duel_id": duel_id}, {"_id": 0})
    if not duel:
        raise HTTPException(status_code=404, detail="Duel not found or expired")
    exp = duel.get("expires_at")
    if exp is not None and exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if exp and exp < datetime.now(timezone.utc):
        raise HTTPException(status_code=404, detail="Duel not found or expired")

    questions = []
    for item in duel.get("items", []):
        l = LESSON_MAP.get(item["lesson_id"])
        if not l:
            continue
        qs = loc_lesson_full(l, lang)["questions"]
        qi = item.get("q_index", 0)
        if qi >= len(qs):
            continue
        q = qs[qi]
        questions.append({"q": q["q"], "options": q["options"], "answer": q["answer"],
                          "explain": q["explain"], "tier": item.get("tier", 1)})

    return {
        "duel_id": duel["duel_id"],
        "questions": questions,
        "creator_user_id": duel["creator_user_id"],
        "creator_result": duel.get("creator_result"),
        "opponent_user_id": duel.get("opponent_user_id"),
        "opponent_result": duel.get("opponent_result"),
    }


@api.post("/duels/{duel_id}/complete")
async def complete_duel(duel_id: str, body: DuelCompleteBody, user: dict = Depends(get_current_user)):
    """Store the calling user's result as creator_result (first player) or
    opponent_result (second, different player). No XP/streak/badge side
    effects in this version."""
    duel = await db.duels.find_one({"duel_id": duel_id})
    if not duel:
        raise HTTPException(status_code=404, detail="Duel not found or expired")
    exp = duel.get("expires_at")
    if exp is not None and exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if exp and exp < datetime.now(timezone.utc):
        raise HTTPException(status_code=404, detail="Duel not found or expired")

    now = datetime.now(timezone.utc)
    result = {"correct": body.correct, "total": body.total, "completed_at": now.isoformat()}

    if user["user_id"] == duel["creator_user_id"]:
        if duel.get("creator_result"):
            raise HTTPException(status_code=409, detail="You already played this duel")
        await db.duels.update_one({"duel_id": duel_id}, {"$set": {"creator_result": result}})
    else:
        existing_result = duel.get("opponent_result")
        existing_opponent_id = duel.get("opponent_user_id")
        if existing_result and existing_opponent_id == user["user_id"]:
            raise HTTPException(status_code=409, detail="You already played this duel")
        if existing_result and existing_opponent_id != user["user_id"]:
            raise HTTPException(status_code=409, detail="This duel already has two players")
        await db.duels.update_one(
            {"duel_id": duel_id},
            {"$set": {"opponent_user_id": user["user_id"], "opponent_result": result}},
        )

    fresh = await db.duels.find_one({"duel_id": duel_id}, {"_id": 0})
    return {
        "duel_id": fresh["duel_id"],
        "creator_user_id": fresh["creator_user_id"],
        "creator_result": fresh.get("creator_result"),
        "opponent_user_id": fresh.get("opponent_user_id"),
        "opponent_result": fresh.get("opponent_result"),
    }


# ----------------------------- Vouchers (discount code validation) -----------------------------
class VoucherValidateBody(BaseModel):
    code: str
    plan_id: str


@api.post("/vouchers/validate")
async def validate_voucher(body: VoucherValidateBody, user: dict = Depends(get_current_user)):
    """Validate a discount code for display purposes only. The purchase flow is
    still a placeholder (no real payment processor connected yet), so this does
    NOT redeem the code or change any price — it only checks and reports whether
    the code would currently apply."""
    code = body.code.strip().upper()
    doc = await db.discount_codes.find_one({"code": code}, {"_id": 0})
    if not doc:
        return {"valid": False, "reason": "not_found"}
    if not doc.get("active", False):
        return {"valid": False, "reason": "inactive"}
    valid_until = doc.get("valid_until")
    if valid_until is not None:
        if valid_until.tzinfo is None:
            valid_until = valid_until.replace(tzinfo=timezone.utc)
        if valid_until < datetime.now(timezone.utc):
            return {"valid": False, "reason": "expired"}
    max_redemptions = doc.get("max_redemptions")
    if max_redemptions is not None and doc.get("redemption_count", 0) >= max_redemptions:
        return {"valid": False, "reason": "limit_reached"}
    applicable_plan_ids = doc.get("applicable_plan_ids")
    if applicable_plan_ids is not None and body.plan_id not in applicable_plan_ids:
        return {"valid": False, "reason": "not_applicable"}
    return {"valid": True, "code": doc["code"], "discount_percent": doc.get("discount_percent", 0)}


@api.get("/progress")
async def progress(user: dict = Depends(get_current_user)):
    all_badges = [{**b, "earned": b["id"] in set(user.get("badges", []))} for b in BADGES]
    return {"user": public_user(user), "badges": all_badges, "total_lessons": len(LESSON_ORDER)}


@api.get("/badges")
async def badges_all(user: dict = Depends(get_current_user)):
    return {"badges": [{**b, "earned": b["id"] in set(user.get("badges", []))} for b in BADGES]}


# ----------------------------- Leaderboard -----------------------------
@api.get("/leaderboard")
async def leaderboard(user: dict = Depends(get_current_user)):
    top = await db.users.find({}, {"_id": 0}).sort("xp", -1).limit(50).to_list(50)
    rows = []
    my_rank = None
    for i, u in enumerate(top):
        row = {
            "rank": i + 1,
            "user_id": u["user_id"],
            "name": u.get("name") or "Investor",
            "picture": u.get("picture"),
            "xp": u.get("xp", 0),
            "level": level_for_xp(u.get("xp", 0)),
            "streak": u.get("streak", 0),
            "is_me": u["user_id"] == user["user_id"],
        }
        if row["is_me"]:
            my_rank = row["rank"]
        rows.append(row)
    return {"leaderboard": rows, "my_rank": my_rank}


# ----------------------------- Stocks -----------------------------
# In-memory quote cache with a short TTL. Finnhub free tier allows 60 calls/min,
# so we serve near-live quotes and refresh at most once per QUOTE_TTL seconds.
_quote_cache: dict = {}
QUOTE_TTL = 45  # seconds


async def finnhub_quote(symbol: str):
    """Fetch a live quote from Finnhub, falling back to a deterministic
    simulated quote when no key is set or the request fails."""
    if not FINNHUB_KEY:
        return fallback_quote(symbol)
    now = datetime.now(timezone.utc).timestamp()
    cached = _quote_cache.get(symbol)
    if cached and now - cached["_ts"] < QUOTE_TTL:
        return cached["data"]
    try:
        async with httpx.AsyncClient(timeout=10) as hc:
            r = await hc.get(
                "https://finnhub.io/api/v1/quote",
                params={"symbol": symbol},
                headers={"X-Finnhub-Token": FINNHUB_KEY},
            )
        q = r.json()
        price = float(q.get("c", 0) or 0)
        if price <= 0:
            raise ValueError("no price")
        change = float(q.get("d", 0) or 0)
        change_pct = float(q.get("dp", 0) or 0)
        out = {"symbol": symbol, "price": round(price, 2), "change": round(change, 2),
               "change_pct": round(change_pct, 2), "source": "finnhub"}
        _quote_cache[symbol] = {"_ts": now, "data": out}
        return out
    except Exception as e:
        logger.warning(f"Finnhub quote failed for {symbol}: {e}")
        return fallback_quote(symbol)


@api.get("/stocks")
async def list_stocks(category: Optional[str] = None, q: Optional[str] = None,
                      lang: str = "en", user: dict = Depends(get_current_user)):
    lang = norm_lang(lang)
    watchlist = set(user.get("watchlist", []))
    items = STOCKS
    if category and category != "All":
        items = [s for s in items if s["category"] == category]
    if q:
        ql = q.lower()
        items = [s for s in items if ql in s["symbol"].lower() or ql in s["name"].lower()]
    # Finnhub free tier = 60 calls/min, so we fetch live quotes for the whole list
    # concurrently (with a short TTL cache) instead of the old simulated values.
    quotes = await asyncio.gather(*[finnhub_quote(s["symbol"]) for s in items])
    out = []
    for s, quote in zip(items, quotes):
        out.append({
            "symbol": s["symbol"], "name": s["name"], "category": s["category"],
            "logo": f"https://logo.clearbit.com/{s['domain']}",
            "explain": loc_stock_explain(s["symbol"], s["explain"], lang),
            "in_watchlist": s["symbol"] in watchlist, **quote,
        })
    # Pin watchlisted stocks to the top, preserving relative order within groups.
    out.sort(key=lambda x: not x["in_watchlist"])
    return {"stocks": out, "categories": CATEGORIES}


@api.get("/stocks/{symbol}")
async def stock_detail(symbol: str, lang: str = "en", user: dict = Depends(get_current_user)):
    s = STOCK_MAP.get(symbol.upper())
    if not s:
        raise HTTPException(status_code=404, detail=L("stock_not_found"))
    quote = await finnhub_quote(s["symbol"])
    return {
        "symbol": s["symbol"], "name": s["name"], "category": s["category"],
        "logo": f"https://logo.clearbit.com/{s['domain']}",
        "explain": loc_stock_explain(s["symbol"], s["explain"], norm_lang(lang)),
        "history": fallback_history(s["symbol"], end_price=quote["price"]),
        "in_watchlist": s["symbol"] in set(user.get("watchlist", [])),
        **quote,
    }


@api.post("/watchlist/{symbol}/toggle")
async def toggle_watchlist(symbol: str, user: dict = Depends(get_current_user)):
    sym = symbol.upper()
    if sym not in STOCK_MAP:
        raise HTTPException(status_code=404, detail=L("stock_not_found"))
    watchlist = list(user.get("watchlist", []))
    if sym in watchlist:
        watchlist.remove(sym)
        in_watchlist = False
    else:
        watchlist.append(sym)
        in_watchlist = True
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"watchlist": watchlist}},
    )
    return {"symbol": sym, "in_watchlist": in_watchlist, "watchlist": watchlist}


# ----------------------------- AI Tutor (Claude Sonnet 4.6) -----------------------------
class ChatBody(BaseModel):
    message: str
    lang: Optional[str] = "en"


TUTOR_SYSTEM = (
    "You are Qapilo AI, a financial education assistant. Your sole purpose is education and "
    "building financial literacy.\n"
    "You explain concepts such as: stocks, ETFs, inflation, interest rates, risk, diversification, "
    "financial ratios, balance sheets, income statements, cash flow, market capitalization, "
    "historical crashes and bubbles, famous investors and general economic concepts.\n"
    "STRICT RULES — never break these:\n"
    "- Provide educational information only. Never provide personalized investment or financial advice.\n"
    "- Never recommend buying, selling or holding any security.\n"
    "- Never recommend specific stocks, ETFs, crypto, mutual funds, bonds or any investment product.\n"
    "- Never recommend portfolio allocations or how to split money across assets.\n"
    "- Never predict future stock prices or market direction; never generate buy, sell or hold signals.\n"
    "- Never promise, estimate or guarantee returns.\n"
    "- Never tailor investment suggestions to a user's age, income, savings, goals or risk tolerance.\n"
    "- Never invent live prices, news, earnings, ratios or market data. Only state a live price/news "
    "figure if it is given to you in a 'LIVE DATA' section below; otherwise say you don't have it.\n"
    "- Use real companies/securities ONLY as neutral educational examples, never as recommendations.\n"
    "- Always remain neutral and encourage users to do their own research and, for personal decisions, "
    "to consult a licensed financial professional. You never replace licensed financial advice.\n"
    "If the user asks what THEY should buy/sell/invest in, how to build/rate a portfolio, the 'best' "
    "stock, or to predict a price, do NOT answer with a recommendation or prediction. Instead, briefly "
    "explain, in neutral educational terms, how investors commonly evaluate such questions "
    "(e.g. fundamentals, diversification, time horizon, risk) so the user can research and decide.\n"
    "Keep answers concise (2-5 short paragraphs) and use relatable, everyday analogies.\n"
    "Explain every concept in simple, everyday language that a curious 10-year-old could follow: "
    "use short sentences, avoid unexplained jargon, and prefer concrete everyday comparisons over "
    "technical wording.\n"
    "The first time you use a financial term a beginner may not know (e.g. stock, share, dividend, "
    "ETF, IPO, valuation, P/E ratio, market capitalization, diversification, volatility, etc.), "
    "immediately follow it with a short plain-language definition in parentheses, inline in the same "
    "sentence — e.g. \"dividend (a small part of a company's profit paid out to people who own its "
    "stock)\". Do this inline, never as a separate glossary section. If the same term appears again "
    "later in the same reply, you do not need to define it again.\n"
    "This simplified, plain-language style with inline parenthetical definitions applies no matter "
    "which language you reply in — since you already reply entirely in the user's language, produce "
    "the equivalent simplified explanations and inline definitions naturally in that same language too.\n"
    "Never use Markdown syntax in your replies: no #, ## or ### headers, no **bold** or *italic* "
    "markers, no Markdown tables (no | column separators or --- divider rows), and no [link](url) "
    "syntax. Write in plain, natural paragraphs with simple line breaks instead. When comparing two "
    "or more things (e.g. a stock vs. an ETF), present it as short labeled lines instead of a table "
    "— one line per attribute, in the form \"Attribute: value for A, value for B\" — rather than a "
    "grid. For lists, use plain dashes or numbers followed by a space and plain text (e.g. \"- point "
    "one\"), never bold or nested Markdown formatting within list items. This no-Markdown, "
    "plain-text formatting rule applies in every language you reply in (German, English, Spanish), "
    "not just English.\n"
    "After you finish your main answer, add a new line containing exactly ===FOLLOWUPS=== and then, "
    "one per line below it, up to 3 short, topic-relevant follow-up questions the student could "
    "naturally ask next, in the same language as your reply. Do not number or bullet these lines and "
    "do not use any Markdown formatting on them — plain short questions only. Always include this "
    "marker and its follow-up questions after every normal educational answer you generate.\n"
    "Do NOT add your own disclaimer or 'not financial advice' note — the platform automatically "
    "appends the official educational disclaimer for you. "
    "Reply entirely in the user's language."
)

# Canonical, legally-standardized disclaimer appended to every investment-related answer.
DISCLAIMER_LINE = {
    "en": "This information is provided for educational purposes only and does not constitute financial or investment advice.",
    "de": "Diese Informationen dienen ausschließlich Bildungszwecken und stellen keine Finanz- oder Anlageberatung dar.",
    "es": "Esta información se proporciona únicamente con fines educativos y no constituye asesoramiento financiero ni de inversión.",
}


def append_disclaimer(reply: str, lang: str) -> str:
    """Deterministically ensure the localized educational disclaimer is present."""
    line = DISCLAIMER_LINE.get(lang, DISCLAIMER_LINE["en"])
    lowered = (reply or "").lower()
    # Skip if a disclaimer (any language) is already present to avoid duplication.
    markers = (
        "not financial advice", "not investment advice", "keine finanzberatung",
        "keine anlageberatung", "finanz- oder anlageberatung", "no es asesoramiento",
        "no constituye asesoramiento", "asesoramiento financiero",
        "educational purposes only", "bildungszwecken", "fines educativos",
        "not constitute financial",
    )
    if any(m in lowered for m in markers):
        return reply
    return f"{reply.rstrip()}\n\n_{line}_"

# Localized hard-refusal shown when a user asks for personalized advice / what to buy.
ADVICE_REFUSAL = {
    "en": (
        "I'm here to teach you *about* investing, but I can't tell you what to buy, sell, or do "
        "with your money — that would be personalized financial advice. I can, however, explain how "
        "stocks, ETFs, risk and diversification work so you can make your own informed decisions.\n\n"
        "_For educational purposes only—not financial advice._"
    ),
    "de": (
        "Ich bin hier, um dir Investieren *beizubringen*, aber ich kann dir nicht sagen, was du "
        "kaufen, verkaufen oder mit deinem Geld tun sollst – das wäre eine persönliche "
        "Finanzberatung. Ich kann dir aber erklären, wie Aktien, ETFs, Risiko und Diversifikation "
        "funktionieren, damit du selbst fundierte Entscheidungen triffst.\n\n"
        "_Nur zu Bildungszwecken – keine Finanzberatung._"
    ),
    "es": (
        "Estoy aquí para enseñarte *sobre* inversión, pero no puedo decirte qué comprar, vender o "
        "hacer con tu dinero: eso sería asesoramiento financiero personalizado. Sí puedo explicarte "
        "cómo funcionan las acciones, los ETF, el riesgo y la diversificación para que tomes tus "
        "propias decisiones informadas.\n\n"
        "_Solo con fines educativos, no es asesoramiento financiero._"
    ),
}

# Intent patterns (EN/DE/ES) that request personalized advice — refused outright.
# STRONG: always treated as advice, even if phrased as a question.
_ADVICE_PATTERNS = [
    r"(what|which|welche[nrs]?|qu[eé]|cu[aá]l).{0,40}(should i|do i|to)?\s*(buy|invest|kaufen|investieren|comprar|invertir)",
    r"(should i|shall i|soll ich|sollte ich|debo|deber[ií]a|tengo que).{0,25}(buy|sell|invest|kaufen|verkaufen|investieren|comprar|vender|invertir)",
    r"(i have|i've got|i got|ich habe|tengo|tengo unos).{0,30}(money|dollars?|euros?|\$|€|geld|dinero).{0,30}(invest|kaufen|investieren|invertir|do with|machen|hago|hacer)",
    r"how.{0,20}(become|get|getting|to be).{0,12}rich",
    r"(reich werden|wie werde ich reich|hacerme rico|volverme rico|hacerme millonario|ganar dinero r[aá]pido|get rich|become rich|make me rich|double my money|triple my money|verdoppeln|duplicar mi dinero)",
    r"(what.{0,12}do with my money|tell me what to do with|was soll ich mit meinem geld|qu[eé] hago con mi dinero|qu[eé] hacer con mi dinero|what to do with my (money|savings|cash))",
    r"(how|wie|c[oó]mo).{0,20}(buy|purchase|invest in|kaufe?|kaufen|comprar|compro|invertir en|invertir).{0,18}(stock|share|bitcoin|crypto|ethereum|gold|silver|etf|aktie|krypto|oro|plata|acci[oó]n|acciones)",
    r"(i want to|i wanna|i'd like to|i would like to|ich will|ich m[oö]chte|quiero|me gustar[ií]a).{0,18}(buy|invest|kaufen|investieren|comprar|invertir)",
    # Price / market prediction & signals.
    r"(predict|forecast|price target|prognos|vorhersage|voraussage|kursziel|predic|prediz|pron[oó]stic|precio objetivo)",
    r"(buy|sell|kauf|verkauf)\s*signal|se\u00f1al(es)?\s+de\s+(compra|venta)",
    # Allocation / how much to invest personally.
    r"(how much|wie viel|cu[aá]nto).{0,25}(invest|allocate|put in|investieren|anlegen|invertir|poner)",
    r"\ballocat|\bwie soll ich.{0,15}(aufteilen|verteilen)",
]

# SOFT: personalized/imperative requests to produce a pick/portfolio. Skipped when the
# message is clearly an educational question (see _EDU_LEADIN) so we still teach concepts.
_ADVICE_SOFT_PATTERNS = [
    r"(build|create|make|generate|design|give me|rate|analyze|analyse|review|optimize|optimise|erstelle?|erstellen|bewerte?|bewerten|analysiere?|crea|constru[iy]e?|arma|genera|generar|optimiza|analiza|eval[uú]a|califica).{0,25}(a |my |me a |mein[e]?[nrs]?|mi |un[a]? )?(portfolio|portefeuille|depot|portafolio|cartera)",
    r"(recommend|suggest|pick|give me|gib mir|tell me|which is|what'?s|what is|empfiehl|empfehle|welche[nrs]?|ist das beste|nenne? mir|recomienda|sugiere|dame|cu[aá]l es|dime).{0,20}(best|top|beste[nrs]?|mejor(es)?).{0,18}(stock|share|etf|crypto|coin|fund|investment|aktie|krypto|fonds|acci[oó]n|acciones|inversi[oó]n)",
]

# Educational lead-ins: "what is / how does / explain …" — let these reach the tutor so it
# can teach the concept instead of hard-refusing.
_EDU_LEADIN = re.compile(
    r"^\s*(what\s+is|what'?s|whats|how\s+(do|does|is|are|can|would|might)|why|when|who|explain|"
    r"define|tell me about|difference between|was\s+ist|was\s+sind|wie\s+(funktioniert|funktionieren|"
    r"kann|wird|bewerten)|erkl[aä]r|warum|unterschied|qu[eé]\s+es|qu[eé]\s+son|c[oó]mo\s+(funciona|se|"
    r"eval[uú]an)|explica|por\s+qu[eé]|diferencia)",
    re.IGNORECASE,
)

_ADVICE_RE = [re.compile(p, re.IGNORECASE) for p in _ADVICE_PATTERNS]
_ADVICE_SOFT_RE = [re.compile(p, re.IGNORECASE) for p in _ADVICE_SOFT_PATTERNS]


def is_advice_seeking(text: str) -> bool:
    if any(rx.search(text) for rx in _ADVICE_RE):
        return True
    # Soft patterns are advice unless the user is clearly asking an educational question.
    if _EDU_LEADIN.match(text or ""):
        return False
    return any(rx.search(text) for rx in _ADVICE_SOFT_RE)

# Keywords that indicate the user wants current / real-time information.
_REALTIME_HINTS = (
    "price", "current", "now", "today", "latest", "recent", "news", "ipo", "earnings",
    "quote", "worth", "2024", "2025", "2026", "this week", "this year", "trading at",
    "how much", "market cap", "up or down", "performing",
)


async def tavily_news(query: str, max_results: int = 5):
    """Fetch fresh web/news snippets from Tavily. Returns a list of {title,url,content}."""
    if not TAVILY_KEY:
        return []
    try:
        async with httpx.AsyncClient(timeout=15) as hc:
            r = await hc.post(
                "https://api.tavily.com/search",
                headers={"Authorization": f"Bearer {TAVILY_KEY}"},
                json={
                    "query": query, "topic": "news", "search_depth": "basic",
                    "time_range": "month", "max_results": max_results,
                    "include_answer": False, "include_raw_content": False,
                },
            )
        return r.json().get("results", []) if r.status_code == 200 else []
    except Exception as e:
        logger.warning(f"Tavily search failed: {e}")
        return []


def _detect_symbols(text: str):
    """Find stock symbols/company names from our universe mentioned in the text."""
    tokens = set(re.findall(r"[A-Za-z]+", text.upper()))
    low = text.lower()
    found = []
    for s in STOCKS:
        first_word = s["name"].split()[0].lower()
        name_hit = len(first_word) > 3 and re.search(r"\b" + re.escape(first_word) + r"\b", low)
        if s["symbol"] in tokens or name_hit:
            found.append(s["symbol"])
    return found[:4]


async def gather_realtime_context(text: str) -> str:
    """Build a LIVE DATA block with current quotes and recent news when the
    question looks like it needs up-to-date information."""
    low = text.lower()
    wants_realtime = any(h in low for h in _REALTIME_HINTS)
    symbols = _detect_symbols(text)
    if not wants_realtime and not symbols:
        return ""

    parts = []
    if symbols:
        quotes = await asyncio.gather(*[finnhub_quote(sym) for sym in symbols])
        lines = [
            f"- {q['symbol']}: ${q['price']} ({'+' if q['change'] >= 0 else ''}{q['change']}, "
            f"{q['change_pct']}%) [source: {q['source']}]"
            for q in quotes
        ]
        parts.append("Current stock prices:\n" + "\n".join(lines))

    if wants_realtime:
        results = await tavily_news(text)
        if results:
            news = "\n".join(
                f"- {r.get('title','')}: {(r.get('content') or '')[:280]} ({r.get('url','')})"
                for r in results
            )
            parts.append("Recent news snippets:\n" + news)

    if not parts:
        return ""
    return "LIVE DATA (use this for current facts):\n" + "\n\n".join(parts) + "\n\n"


async def tutor_used_today(user_id: str) -> int:
    start = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return await db.chat_messages.count_documents(
        {"user_id": user_id, "role": "user", "day": start}
    )


@api.get("/tutor/status")
async def tutor_status(user: dict = Depends(get_current_user)):
    is_pro = compute_pro(user)["is_pro"]
    used = await tutor_used_today(user["user_id"])
    return {
        "is_pro": is_pro,
        "used_today": used,
        "limit": None if is_pro else FREE_TUTOR_DAILY_LIMIT,
        "remaining": None if is_pro else max(0, FREE_TUTOR_DAILY_LIMIT - used),
        "configured": bool(EMERGENT_LLM_KEY),
    }


@api.get("/tutor/history")
async def tutor_history(user: dict = Depends(get_current_user)):
    msgs = await db.chat_messages.find(
        {"user_id": user["user_id"]}, {"_id": 0, "role": 1, "content": 1, "created_at": 1}
    ).sort("created_at", 1).to_list(200)
    return {"messages": msgs}


@api.post("/tutor/chat")
async def tutor_chat(body: ChatBody, user: dict = Depends(get_current_user)):
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=503, detail=L("tutor_not_configured"))
    text = body.message.strip()
    if not text:
        raise HTTPException(status_code=400, detail=L("message_empty"))

    lang = norm_lang(body.lang)
    is_pro = compute_pro(user)["is_pro"]

    # Hard guardrail: refuse personalized-advice questions ("what should I buy",
    # "how do I get rich", "how to buy bitcoin/gold", etc.) with only the disclaimer.
    if is_advice_seeking(text):
        refusal = ADVICE_REFUSAL.get(lang, ADVICE_REFUSAL["en"])
        now = datetime.now(timezone.utc)
        day = now.strftime("%Y-%m-%d")
        await db.chat_messages.insert_many([
            {"user_id": user["user_id"], "role": "user", "content": text,
             "day": day, "created_at": now.isoformat()},
            {"user_id": user["user_id"], "role": "assistant", "content": refusal,
             "day": day, "created_at": (now + timedelta(milliseconds=1)).isoformat()},
        ])
        used_now = await tutor_used_today(user["user_id"])
        return {
            "reply": refusal,
            "remaining": None if is_pro else max(0, FREE_TUTOR_DAILY_LIMIT - used_now),
            "is_pro": is_pro,
            "follow_up_questions": [],
        }

    used = await tutor_used_today(user["user_id"])
    if not is_pro and used >= FREE_TUTOR_DAILY_LIMIT:
        raise HTTPException(
            status_code=402,
            detail=L("tutor_limit"),
        )

    # Build compact recent context transcript
    recent = await db.chat_messages.find(
        {"user_id": user["user_id"]}, {"_id": 0, "role": 1, "content": 1}
    ).sort("created_at", -1).to_list(8)
    recent.reverse()
    transcript = ""
    for m in recent:
        who = "Student" if m["role"] == "user" else "Tutor"
        transcript += f"{who}: {m['content']}\n"

    live_context = await gather_realtime_context(text)
    prompt = (
        (f"Recent conversation:\n{transcript}\n" if transcript else "")
        + live_context
        + f"Student: {text}"
    )

    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"tutor_{user['user_id']}",
        system_message=TUTOR_SYSTEM + f"\n\nAlways reply in {LANG_NAMES.get(norm_lang(body.lang), 'English')}.",
    ).with_model("anthropic", CLAUDE_MODEL)

    try:
        raw_reply = await chat.send_message(UserMessage(text=prompt))
    except Exception as e:
        logger.error(f"Tutor error: {e}")
        raise HTTPException(status_code=502, detail=L("tutor_unavailable"))

    # Split the model's follow-up-question suggestions out of the main answer.
    followups_marker = "===FOLLOWUPS==="
    if followups_marker in raw_reply:
        answer_part, _, followups_part = raw_reply.partition(followups_marker)
    else:
        answer_part, followups_part = raw_reply, ""
    follow_up_questions = [ln.strip() for ln in followups_part.splitlines() if ln.strip()][:3]

    # Deterministically guarantee the localized educational disclaimer is present.
    reply = append_disclaimer(answer_part, lang)

    now = datetime.now(timezone.utc)
    day = now.strftime("%Y-%m-%d")
    await db.chat_messages.insert_many([
        {"user_id": user["user_id"], "role": "user", "content": text,
         "day": day, "created_at": now.isoformat()},
        {"user_id": user["user_id"], "role": "assistant", "content": reply,
         "day": day, "created_at": (now + timedelta(milliseconds=1)).isoformat()},
    ])
    used_after = used + 1
    return {
        "reply": reply,
        "remaining": None if is_pro else max(0, FREE_TUTOR_DAILY_LIMIT - used_after),
        "is_pro": is_pro,
        "follow_up_questions": follow_up_questions,
    }


# ----------------------------- PayPal Pro Subscription -----------------------------
class SubscribeBody(BaseModel):
    return_base: Optional[str] = None


def paypal_configured() -> bool:
    return bool(PAYPAL_CLIENT_ID and PAYPAL_SECRET)


async def paypal_token() -> str:
    auth = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_SECRET}".encode()).decode()
    async with httpx.AsyncClient(timeout=30) as hc:
        r = await hc.post(
            f"{PAYPAL_BASE}/v1/oauth2/token",
            headers={"Authorization": f"Basic {auth}",
                     "Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "client_credentials"},
        )
    if r.status_code != 200:
        logger.error(f"PayPal token error: {r.text}")
        raise HTTPException(status_code=502, detail=L("paypal_auth_failed"))
    return r.json()["access_token"]


async def ensure_plan() -> str:
    cfg = await db.config.find_one({"_id": "paypal_plan"})
    if cfg and cfg.get("plan_id") and cfg.get("price") == PRO_PRICE and cfg.get("mode") == PAYPAL_MODE:
        return cfg["plan_id"]

    token = await paypal_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=30) as hc:
        pr = await hc.post(f"{PAYPAL_BASE}/v1/catalogs/products", headers=headers, json={
            "name": "Qapilo Pro",
            "description": "Unlimited AI Tutor and advanced stock lessons",
            "type": "SERVICE", "category": "EDUCATIONAL_AND_TEXTBOOKS",
        })
        if pr.status_code not in (200, 201):
            logger.error(f"PayPal product error: {pr.text}")
            raise HTTPException(status_code=502, detail=L("paypal_product_failed"))
        product_id = pr.json()["id"]

        plan_body = {
            "product_id": product_id,
            "name": "Qapilo Pro Monthly",
            "description": f"7-day free trial, then ${PRO_PRICE}/month",
            "billing_cycles": [
                {
                    "frequency": {"interval_unit": "DAY", "interval_count": TRIAL_DAYS},
                    "tenure_type": "TRIAL", "sequence": 1, "total_cycles": 1,
                    "pricing_scheme": {"fixed_price": {"value": "0", "currency_code": "USD"}},
                },
                {
                    "frequency": {"interval_unit": "MONTH", "interval_count": 1},
                    "tenure_type": "REGULAR", "sequence": 2, "total_cycles": 0,
                    "pricing_scheme": {"fixed_price": {"value": PRO_PRICE, "currency_code": "USD"}},
                },
            ],
            "payment_preferences": {
                "auto_bill_outstanding": True,
                "setup_fee": {"value": "0", "currency_code": "USD"},
                "setup_fee_failure_action": "CONTINUE",
                "payment_failure_threshold": 2,
            },
        }
        pl = await hc.post(f"{PAYPAL_BASE}/v1/billing/plans", headers=headers, json=plan_body)
        if pl.status_code not in (200, 201):
            logger.error(f"PayPal plan error: {pl.text}")
            raise HTTPException(status_code=502, detail=L("paypal_plan_failed"))
        plan_id = pl.json()["id"]

    await db.config.update_one(
        {"_id": "paypal_plan"},
        {"$set": {"plan_id": plan_id, "product_id": product_id, "price": PRO_PRICE, "mode": PAYPAL_MODE}},
        upsert=True,
    )
    return plan_id


@api.get("/pro/plan")
async def pro_plan(user: dict = Depends(get_current_user)):
    return {
        "price": PRO_PRICE,
        "currency": "USD",
        "trial_days": TRIAL_DAYS,
        "paypal_configured": paypal_configured(),
        "features": [
            "Unlimited AI Tutor chat",
            "Advanced units: Fundamental Analysis & Smart Investing",
            "Support the app's growth",
        ],
        **compute_pro(user),
    }


@api.post("/subscription/create")
async def subscription_create(body: SubscribeBody, request: Request,
                              user: dict = Depends(get_current_user)):
    if not paypal_configured():
        raise HTTPException(status_code=503, detail=L("payments_not_configured"))
    plan_id = await ensure_plan()
    base = (body.return_base or str(request.base_url)).rstrip("/")
    return_url = f"{base}/api/subscription/return"
    cancel_url = f"{base}/api/subscription/return?cancel=1"

    token = await paypal_token()
    async with httpx.AsyncClient(timeout=30) as hc:
        r = await hc.post(
            f"{PAYPAL_BASE}/v1/billing/subscriptions",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={
                "plan_id": plan_id,
                "subscriber": {"email_address": user.get("email"),
                               "name": {"given_name": user.get("name") or "Qapilo", "surname": "User"}},
                "application_context": {
                    "brand_name": "Qapilo",
                    "user_action": "SUBSCRIBE_NOW",
                    "return_url": return_url,
                    "cancel_url": cancel_url,
                },
            },
        )
    if r.status_code not in (200, 201):
        logger.error(f"PayPal subscription error: {r.text}")
        raise HTTPException(status_code=502, detail=L("sub_start_failed"))
    data = r.json()
    approve = next((l["href"] for l in data.get("links", []) if l["rel"] == "approve"), None)
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"subscription_id": data["id"], "subscription_status": data.get("status")}},
    )
    return {"subscription_id": data["id"], "approval_url": approve}


@api.get("/subscription/return")
async def subscription_return():
    from fastapi.responses import HTMLResponse
    html = """<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>body{background:#09090B;color:#FAFAFA;font-family:sans-serif;display:flex;height:100vh;
    align-items:center;justify-content:center;text-align:center;margin:0}
    .c{max-width:320px;padding:24px}.d{width:64px;height:64px;border-radius:16px;background:#10B981;
    margin:0 auto 16px}</style></head><body><div class="c"><div class="d"></div>
    <h2>All set!</h2><p>You can close this window and return to Qapilo.</p></div></body></html>"""
    return HTMLResponse(content=html)


@api.post("/subscription/activate")
async def subscription_activate(body: dict, user: dict = Depends(get_current_user)):
    sub_id = body.get("subscription_id") or user.get("subscription_id")
    if not sub_id:
        raise HTTPException(status_code=400, detail=L("no_sub_to_activate"))
    if not paypal_configured():
        raise HTTPException(status_code=503, detail=L("payments_not_configured"))
    token = await paypal_token()
    async with httpx.AsyncClient(timeout=30) as hc:
        r = await hc.get(f"{PAYPAL_BASE}/v1/billing/subscriptions/{sub_id}",
                         headers={"Authorization": f"Bearer {token}"})
    if r.status_code != 200:
        logger.error(f"PayPal get sub error: {r.text}")
        raise HTTPException(status_code=502, detail=L("sub_verify_failed"))
    status = r.json().get("status")
    active = status in ("ACTIVE", "APPROVED")
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"pro_active": active, "subscription_status": status, "subscription_id": sub_id}},
    )
    fresh = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if active and fresh.get("email"):
        asyncio.create_task(email.send_and_log(
            db, "subscription_activated", "en", fresh["email"], fresh["user_id"]))
    return {"activated": active, "status": status, "user": public_user(fresh)}


@api.get("/subscription/status")
async def subscription_status(user: dict = Depends(get_current_user)):
    sub_id = user.get("subscription_id")
    if sub_id and paypal_configured():
        try:
            token = await paypal_token()
            async with httpx.AsyncClient(timeout=30) as hc:
                r = await hc.get(f"{PAYPAL_BASE}/v1/billing/subscriptions/{sub_id}",
                                 headers={"Authorization": f"Bearer {token}"})
            if r.status_code == 200:
                status = r.json().get("status")
                active = status in ("ACTIVE", "APPROVED")
                await db.users.update_one(
                    {"user_id": user["user_id"]},
                    {"$set": {"pro_active": active, "subscription_status": status}},
                )
                user = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
        except Exception as e:
            logger.warning(f"sub status refresh failed: {e}")
    return {"user": public_user(user)}


@api.post("/subscription/cancel")
async def subscription_cancel(user: dict = Depends(get_current_user)):
    sub_id = user.get("subscription_id")
    if sub_id and paypal_configured():
        try:
            token = await paypal_token()
            async with httpx.AsyncClient(timeout=30) as hc:
                await hc.post(
                    f"{PAYPAL_BASE}/v1/billing/subscriptions/{sub_id}/cancel",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    json={"reason": "User requested cancellation"},
                )
        except Exception as e:
            logger.warning(f"cancel failed: {e}")
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"pro_active": False, "subscription_status": "CANCELLED"}},
    )
    fresh = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    if fresh.get("email"):
        asyncio.create_task(email.send_and_log(
            db, "subscription_cancelled", "en", fresh["email"], fresh["user_id"]))
    return {"user": public_user(fresh)}


@api.get("/account/export")
async def account_export(user: dict = Depends(get_current_user)):
    """GDPR data portability: return all stored personal data for the user."""
    chats = await db.chat_messages.find(
        {"user_id": user["user_id"]}, {"_id": 0, "role": 1, "content": 1, "created_at": 1}
    ).sort("created_at", 1).to_list(5000)
    profile = {k: v for k, v in user.items()
               if k not in ("_id", "password", "hashed_password", "password_hash")}
    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "data_controller": "Qapilo",
        "profile": profile,
        "chat_history": chats,
    }


@api.delete("/account")
async def account_delete(user: dict = Depends(get_current_user)):
    """GDPR right to erasure: cancel any active subscription and permanently
    delete the user and all associated personal data."""
    sub_id = user.get("subscription_id")
    if sub_id and paypal_configured():
        try:
            token = await paypal_token()
            async with httpx.AsyncClient(timeout=30) as hc:
                await hc.post(
                    f"{PAYPAL_BASE}/v1/billing/subscriptions/{sub_id}/cancel",
                    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                    json={"reason": "Account deletion"},
                )
        except Exception as e:
            logger.warning(f"sub cancel on delete failed: {e}")
    await db.chat_messages.delete_many({"user_id": user["user_id"]})
    # Send the completion email BEFORE removing the address (deletion is immediate).
    if user.get("email"):
        try:
            await email.send_and_log(
                db, "account_deleted", "en", user["email"], None)
        except Exception:
            logger.warning("account_deleted email failed")
    await db.password_resets.delete_many({"user_id": user["user_id"]})
    await db.users.delete_one({"user_id": user["user_id"]})
    return {"deleted": True}


class UpdateAccountBody(BaseModel):
    name: str


@api.patch("/account")
async def account_update(body: UpdateAccountBody, user: dict = Depends(get_current_user)):
    """GDPR right to rectification: let the user correct their display name."""
    name = body.name.strip()[:60]
    if not name:
        raise HTTPException(status_code=400, detail=L("message_empty"))
    await db.users.update_one({"user_id": user["user_id"]}, {"$set": {"name": name}})
    updated = await db.users.find_one({"user_id": user["user_id"]})
    return {"user": public_user(updated)}


@api.delete("/tutor/history")
async def clear_tutor_history(user: dict = Depends(get_current_user)):
    """Delete all of the user's AI Tutor chat messages."""
    res = await db.chat_messages.delete_many({"user_id": user["user_id"]})
    return {"deleted": True, "count": res.deleted_count}


@api.post("/auth/forgot-password")
async def forgot_password(body: ForgotPasswordBody, request: Request):
    """Start a password reset. Always returns a neutral response (no account
    enumeration). Only password accounts actually receive an email."""
    ip = (request.client.host if request.client else "unknown")
    lang = body.lang or "en"
    if _rate_limited(f"fp_email:{body.email.lower()}", 3, 900) or _rate_limited(f"fp_ip:{ip}", 12, 3600):
        raise HTTPException(status_code=429, detail=L("rate_limited"))
    user = await db.users.find_one({"email": body.email.lower()})
    if user and user.get("hashed_password"):
        raw = secrets.token_urlsafe(32)
        # Invalidate older unused tokens for this user, then store only the hash.
        await db.password_resets.delete_many({"user_id": user["user_id"]})
        await db.password_resets.insert_one({
            "user_id": user["user_id"],
            "token_hash": _hash_token(raw),
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_TTL_MIN),
            "used": False,
        })
        ctx = {"ttl": RESET_TOKEN_TTL_MIN, "token": raw}
        if QAPILO_APP_URL:
            ctx["link"] = f"{QAPILO_APP_URL}/reset-password?token={raw}"
        asyncio.create_task(email.send_and_log(
            db, "password_reset", lang, user["email"], user["user_id"], ctx))
    return {"ok": True, "message": L("reset_sent")}


@api.post("/auth/reset-password")
async def reset_password(body: ResetPasswordBody):
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail=L("weak_password"))
    rec = await db.password_resets.find_one({"token_hash": _hash_token(body.token), "used": False})
    if not rec:
        raise HTTPException(status_code=400, detail=L("reset_invalid"))
    exp = rec.get("expires_at")
    if exp is not None and exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if not exp or exp < datetime.now(timezone.utc):
        await db.password_resets.delete_one({"_id": rec["_id"]})
        raise HTTPException(status_code=400, detail=L("reset_invalid"))
    import time
    await db.users.update_one(
        {"user_id": rec["user_id"]},
        {"$set": {"hashed_password": pwd_context.hash(body.new_password),
                  "sessions_invalid_before": int(time.time())}},
    )
    # Single-use: remove all reset records for this user.
    await db.password_resets.delete_many({"user_id": rec["user_id"]})
    return {"ok": True, "message": L("reset_ok")}


@api.post("/support/request")
async def support_request(body: SupportBody, request: Request):
    """Store a support request, email the user a confirmation, and forward to the
    configured support inbox if one is set. No secrets/tokens are stored or sent."""
    category = (body.category or "").strip()[:40]
    subject = (body.subject or "").strip()[:120]
    message = (body.message or "").strip()[:4000]
    if not category or not subject or not message:
        raise HTTPException(status_code=400, detail=L("support_invalid"))
    # Basic header-injection guard for the subject/category.
    if any(c in subject + category for c in ("\r", "\n")):
        raise HTTPException(status_code=400, detail=L("support_invalid"))
    ip = (request.client.host if request.client else "unknown")
    if _rate_limited(f"sup_ip:{ip}", 5, 3600):
        raise HTTPException(status_code=429, detail=L("rate_limited"))

    # Identify user if signed in (optional).
    user = None
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        try:
            uid = jwt.decode(auth.split(" ", 1)[1].strip(), JWT_SECRET, algorithms=[JWT_ALG]).get("sub")
            user = await db.users.find_one({"user_id": uid})
        except Exception:
            user = None
    reply_email = (user.get("email") if user else None) or (body.reply_email or None)
    lang = body.lang or "en"
    ref = f"QS-{secrets.token_hex(4).upper()}"

    await db.support_requests.insert_one({
        "ref": ref,
        "user_ref": user["user_id"] if user else None,
        "category": category,
        "subject": subject,
        "message": message,
        "reply_email": reply_email,
        "language": lang,
        "created_at": datetime.now(timezone.utc),
        "status": "received",
    })
    if reply_email:
        asyncio.create_task(email.send_and_log(
            db, "support_received", lang, reply_email,
            user["user_id"] if user else None,
            {"ref": ref, "category": category, "subj": subject}))
    # Forward to support inbox only if configured (owner-provided; never invented).
    if SUPPORT_EMAIL:
        asyncio.create_task(email.send_and_log(
            db, "support_forwarded", lang, SUPPORT_EMAIL, None,
            {"ref": ref, "category": category, "subj": subject,
             "frm": reply_email or "n/a", "lng": lang, "msg": message},
            reply_to=reply_email))
        logger.info(f"support forwarded ref={ref}")
    return {"ok": True, "ref": ref, "message": L("support_ok")}


app.include_router(api)


@app.middleware("http")
async def language_middleware(request: Request, call_next):
    set_lang_from_header(request.headers.get("accept-language", ""))
    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
