import os
import uuid
import base64
import asyncio
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

from content import UNITS, LESSON_MAP, LESSON_ORDER, BADGES, BADGE_MAP
from stocks import STOCKS, STOCK_MAP, CATEGORIES, fallback_quote, fallback_history
from content_i18n import UNIT_T, LESSON_T, STOCK_T, norm_lang
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

JWT_SECRET = os.environ.get("JWT_SECRET", "change-me-dev-secret")
JWT_ALG = "HS256"
JWT_EXPIRES_DAYS = 30
FINNHUB_KEY = os.environ.get("FINNHUB_API_KEY", "").strip()
DAILY_GOAL_XP = 50

# --- Monetization / AI config ---
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "").strip()
CLAUDE_MODEL = "claude-sonnet-4-6"
TRIAL_DAYS = 7
PRO_UNITS = {"u4", "u5"}  # advanced units gated behind Pro
FREE_TUTOR_DAILY_LIMIT = 3
PAYPAL_CLIENT_ID = os.environ.get("PAYPAL_CLIENT_ID", "").strip()
PAYPAL_SECRET = os.environ.get("PAYPAL_SECRET", "").strip()
PAYPAL_MODE = os.environ.get("PAYPAL_MODE", "sandbox").strip()
PRO_PRICE = os.environ.get("PRO_PRICE", "4.99").strip()
PAYPAL_BASE = (
    "https://api-m.paypal.com" if PAYPAL_MODE == "live" else "https://api-m.sandbox.paypal.com"
)

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


class LoginBody(BaseModel):
    email: EmailStr
    password: str


class GoogleBody(BaseModel):
    session_id: str


class CompleteBody(BaseModel):
    correct: int
    total: int


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


def loc_lesson_full(l: dict, lang: str) -> dict:
    """Return localized title, cards and questions. Answer indices come from the
    English source (l) so translated option order must match."""
    t = LESSON_T.get(lang, {}).get(l["id"])
    if not t:
        return {"title": l["title"], "cards": l["cards"], "questions": l["questions"]}
    questions = []
    for i, q in enumerate(l["questions"]):
        tq = t["questions"][i]
        questions.append({"q": tq["q"], "options": tq["options"],
                          "answer": q["answer"], "explain": tq["explain"]})
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
    now = datetime.now(timezone.utc)
    trial_end = _parse_dt(u.get("trial_ends_at"))
    sub_active = u.get("pro_active", False)
    in_trial = bool(trial_end and now < trial_end)
    is_pro = sub_active or in_trial
    trial_days_left = 0
    if trial_end and now < trial_end:
        trial_days_left = (trial_end - now).days + 1
    source = "subscription" if sub_active else ("trial" if in_trial else "free")
    return {
        "is_pro": is_pro,
        "pro_source": source,
        "in_trial": in_trial,
        "trial_days_left": trial_days_left,
        "trial_ends_at": u.get("trial_ends_at"),
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
        "accepted_terms": u.get("accepted_terms", False),
        **compute_pro(u),
    }


async def get_current_user(request: Request) -> dict:
    auth = request.headers.get("Authorization", "")
    if not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def ensure_indexes():
    await db.users.create_index("email", unique=True, sparse=True)
    await db.users.create_index("user_id", unique=True)


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
        raise HTTPException(status_code=400, detail="Email already registered")
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
        "trial_ends_at": (datetime.now(timezone.utc) + timedelta(days=TRIAL_DAYS)).isoformat(),
        "pro_active": False, "subscription_id": None, "subscription_status": None,
        "accepted_terms": False,
    }
    await db.users.insert_one(user)
    return {"token": make_token(user["user_id"]), "user": public_user(user)}


@api.post("/auth/login")
async def login(body: LoginBody):
    user = await db.users.find_one({"email": body.email.lower()})
    dummy = pwd_context.hash("dummy-timing-guard")
    if not user or not user.get("hashed_password"):
        pwd_context.verify(body.password, dummy)
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not pwd_context.verify(body.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"token": make_token(user["user_id"]), "user": public_user(user)}


@api.post("/auth/google")
async def google_auth(body: GoogleBody):
    async with httpx.AsyncClient(timeout=20) as hc:
        r = await hc.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": body.session_id},
        )
    if r.status_code != 200:
        raise HTTPException(status_code=401, detail="Google session invalid")
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
            "trial_ends_at": (datetime.now(timezone.utc) + timedelta(days=TRIAL_DAYS)).isoformat(),
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


@api.get("/auth/me")
async def me(user: dict = Depends(get_current_user)):
    return {"user": public_user(user)}


@api.post("/auth/logout")
async def logout(user: dict = Depends(get_current_user)):
    return {"ok": True}


@api.post("/auth/accept-terms")
async def accept_terms(user: dict = Depends(get_current_user)):
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"accepted_terms": True,
                  "terms_accepted_at": datetime.now(timezone.utc).isoformat()}},
    )
    fresh = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
    return {"user": public_user(fresh)}


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
            "color": u["color"], "lessons": lessons_out, "pro": unit_pro,
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
        raise HTTPException(status_code=404, detail="Lesson not found")
    if l["unit_id"] in PRO_UNITS and not compute_pro(user)["is_pro"]:
        raise HTTPException(status_code=403, detail="This lesson requires TradeQuest Pro")
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
    if len(perfect) >= 1:
        award("perfectionist")
    if len(completed) >= 8:
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
        raise HTTPException(status_code=404, detail="Lesson not found")

    completed = list(user.get("completed_lessons", []))
    perfect = list(user.get("perfect_lessons", []))
    first_time = lesson_id not in completed

    # XP: full reward first time, quarter reward for replays. Scale by accuracy.
    accuracy = body.correct / body.total if body.total else 0
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
            "explain": loc_stock_explain(s["symbol"], s["explain"], lang), **quote,
        })
    return {"stocks": out, "categories": CATEGORIES}


@api.get("/stocks/{symbol}")
async def stock_detail(symbol: str, lang: str = "en", user: dict = Depends(get_current_user)):
    s = STOCK_MAP.get(symbol.upper())
    if not s:
        raise HTTPException(status_code=404, detail="Stock not found")
    quote = await finnhub_quote(s["symbol"])
    return {
        "symbol": s["symbol"], "name": s["name"], "category": s["category"],
        "logo": f"https://logo.clearbit.com/{s['domain']}",
        "explain": loc_stock_explain(s["symbol"], s["explain"], norm_lang(lang)),
        "history": fallback_history(s["symbol"], end_price=quote["price"]),
        **quote,
    }


# ----------------------------- AI Tutor (Claude Sonnet 4.6) -----------------------------
class ChatBody(BaseModel):
    message: str
    lang: Optional[str] = "en"


TUTOR_SYSTEM = (
    "You are Quest, a friendly stock-market tutor inside a beginner learning app called TradeQuest. "
    "Explain investing and stock concepts in plain, simple English for total beginners. "
    "Keep answers concise (2-5 short paragraphs max), use relatable analogies, and avoid jargon "
    "unless you define it. Never give personalized financial advice or specific buy/sell "
    "recommendations — remind users you're educational only when they ask what to buy. "
    "Stay on topics related to stocks, markets, personal finance and investing basics."
)


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
        raise HTTPException(status_code=503, detail="AI Tutor is not configured")
    text = body.message.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Message is empty")

    is_pro = compute_pro(user)["is_pro"]
    used = await tutor_used_today(user["user_id"])
    if not is_pro and used >= FREE_TUTOR_DAILY_LIMIT:
        raise HTTPException(
            status_code=402,
            detail="You've used your free AI Tutor messages for today. Upgrade to Pro for unlimited chat.",
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
    prompt = (f"Recent conversation:\n{transcript}\n" if transcript else "") + f"Student: {text}"

    chat = LlmChat(
        api_key=EMERGENT_LLM_KEY,
        session_id=f"tutor_{user['user_id']}",
        system_message=TUTOR_SYSTEM + f"\n\nAlways reply in {LANG_NAMES.get(norm_lang(body.lang), 'English')}.",
    ).with_model("anthropic", CLAUDE_MODEL)

    try:
        reply = await chat.send_message(UserMessage(text=prompt))
    except Exception as e:
        logger.error(f"Tutor error: {e}")
        raise HTTPException(status_code=502, detail="The AI Tutor is unavailable right now")

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
        raise HTTPException(status_code=502, detail="PayPal authentication failed")
    return r.json()["access_token"]


async def ensure_plan() -> str:
    cfg = await db.config.find_one({"_id": "paypal_plan"})
    if cfg and cfg.get("plan_id") and cfg.get("price") == PRO_PRICE and cfg.get("mode") == PAYPAL_MODE:
        return cfg["plan_id"]

    token = await paypal_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=30) as hc:
        pr = await hc.post(f"{PAYPAL_BASE}/v1/catalogs/products", headers=headers, json={
            "name": "TradeQuest Pro",
            "description": "Unlimited AI Tutor and advanced stock lessons",
            "type": "SERVICE", "category": "EDUCATIONAL_AND_TEXTBOOKS",
        })
        if pr.status_code not in (200, 201):
            logger.error(f"PayPal product error: {pr.text}")
            raise HTTPException(status_code=502, detail="Could not create PayPal product")
        product_id = pr.json()["id"]

        plan_body = {
            "product_id": product_id,
            "name": "TradeQuest Pro Monthly",
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
            raise HTTPException(status_code=502, detail="Could not create PayPal plan")
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
        raise HTTPException(status_code=503, detail="Payments are not configured yet")
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
                               "name": {"given_name": user.get("name") or "TradeQuest", "surname": "User"}},
                "application_context": {
                    "brand_name": "TradeQuest",
                    "user_action": "SUBSCRIBE_NOW",
                    "return_url": return_url,
                    "cancel_url": cancel_url,
                },
            },
        )
    if r.status_code not in (200, 201):
        logger.error(f"PayPal subscription error: {r.text}")
        raise HTTPException(status_code=502, detail="Could not start subscription")
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
    <h2>All set!</h2><p>You can close this window and return to TradeQuest.</p></div></body></html>"""
    return HTMLResponse(content=html)


@api.post("/subscription/activate")
async def subscription_activate(body: dict, user: dict = Depends(get_current_user)):
    sub_id = body.get("subscription_id") or user.get("subscription_id")
    if not sub_id:
        raise HTTPException(status_code=400, detail="No subscription to activate")
    if not paypal_configured():
        raise HTTPException(status_code=503, detail="Payments are not configured yet")
    token = await paypal_token()
    async with httpx.AsyncClient(timeout=30) as hc:
        r = await hc.get(f"{PAYPAL_BASE}/v1/billing/subscriptions/{sub_id}",
                         headers={"Authorization": f"Bearer {token}"})
    if r.status_code != 200:
        logger.error(f"PayPal get sub error: {r.text}")
        raise HTTPException(status_code=502, detail="Could not verify subscription")
    status = r.json().get("status")
    active = status in ("ACTIVE", "APPROVED")
    await db.users.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"pro_active": active, "subscription_status": status, "subscription_id": sub_id}},
    )
    fresh = await db.users.find_one({"user_id": user["user_id"]}, {"_id": 0})
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
    return {"user": public_user(fresh)}


app.include_router(api)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
