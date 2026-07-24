import os
import uuid
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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

JWT_SECRET = os.environ.get("JWT_SECRET", "change-me-dev-secret")
JWT_ALG = "HS256"
JWT_EXPIRES_DAYS = 30
ALPHA_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY", "").strip()
DAILY_GOAL_XP = 50

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


# ----------------------------- Curriculum -----------------------------
@api.get("/curriculum")
async def curriculum(user: dict = Depends(get_current_user)):
    completed = set(user.get("completed_lessons", []))
    units_out = []
    prev_done = True  # first lesson always unlocked
    for u in UNITS:
        lessons_out = []
        for l in u["lessons"]:
            is_done = l["id"] in completed
            unlocked = prev_done or is_done
            lessons_out.append({
                "id": l["id"], "title": l["title"], "icon": l["icon"], "xp": l["xp"],
                "completed": is_done, "unlocked": unlocked,
                "perfect": l["id"] in set(user.get("perfect_lessons", [])),
            })
            prev_done = is_done
        units_out.append({
            "id": u["id"], "title": u["title"], "subtitle": u["subtitle"],
            "color": u["color"], "lessons": lessons_out,
        })
    total = len(LESSON_ORDER)
    return {
        "units": units_out,
        "total_lessons": total,
        "completed_count": len(completed),
    }


@api.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: str, user: dict = Depends(get_current_user)):
    l = LESSON_MAP.get(lesson_id)
    if not l:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return {
        "id": l["id"], "title": l["title"], "icon": l["icon"], "xp": l["xp"],
        "unit_title": l["unit_title"], "unit_color": l["unit_color"],
        "cards": l["cards"], "questions": l["questions"],
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
_quote_cache: dict = {}


async def av_quote(symbol: str):
    if not ALPHA_KEY:
        return fallback_quote(symbol)
    cache_key = f"{symbol}-{today_str()}"
    if cache_key in _quote_cache:
        return _quote_cache[cache_key]
    try:
        async with httpx.AsyncClient(timeout=10) as hc:
            r = await hc.get("https://www.alphavantage.co/query", params={
                "function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": ALPHA_KEY,
            })
        q = r.json().get("Global Quote", {})
        price = float(q.get("05. price", 0) or 0)
        if price <= 0:
            raise ValueError("no price")
        change = float(q.get("09. change", 0) or 0)
        change_pct = float((q.get("10. change percent", "0") or "0").replace("%", ""))
        out = {"symbol": symbol, "price": round(price, 2), "change": round(change, 2),
               "change_pct": round(change_pct, 2), "source": "alphavantage"}
        _quote_cache[cache_key] = out
        return out
    except Exception as e:
        logger.warning(f"AV quote failed for {symbol}: {e}")
        return fallback_quote(symbol)


@api.get("/stocks")
async def list_stocks(category: Optional[str] = None, q: Optional[str] = None,
                      user: dict = Depends(get_current_user)):
    items = STOCKS
    if category and category != "All":
        items = [s for s in items if s["category"] == category]
    if q:
        ql = q.lower()
        items = [s for s in items if ql in s["symbol"].lower() or ql in s["name"].lower()]
    out = []
    for s in items:
        quote = await av_quote(s["symbol"])
        out.append({
            "symbol": s["symbol"], "name": s["name"], "category": s["category"],
            "logo": f"https://logo.clearbit.com/{s['domain']}",
            "explain": s["explain"], **quote,
        })
    return {"stocks": out, "categories": CATEGORIES}


@api.get("/stocks/{symbol}")
async def stock_detail(symbol: str, user: dict = Depends(get_current_user)):
    s = STOCK_MAP.get(symbol.upper())
    if not s:
        raise HTTPException(status_code=404, detail="Stock not found")
    quote = await av_quote(s["symbol"])
    return {
        "symbol": s["symbol"], "name": s["name"], "category": s["category"],
        "logo": f"https://logo.clearbit.com/{s['domain']}",
        "explain": s["explain"],
        "history": fallback_history(s["symbol"]),
        **quote,
    }


app.include_router(api)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
