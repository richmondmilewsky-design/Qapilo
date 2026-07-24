"""Curated stock universe with plain-English explanations.

Live quotes come from Finnhub when FINNHUB_API_KEY is set; otherwise a
deterministic pseudo-live fallback is generated so the app is always functional.
Note: Finnhub's free tier does not include candle/history data, so the price
chart uses the deterministic fallback_history series.
"""
import hashlib
import math
from datetime import datetime, timezone

STOCKS = [
    {"symbol": "AAPL", "name": "Apple Inc.", "category": "Tech", "domain": "apple.com", "base": 212.5,
     "explain": "Makes the iPhone, Mac and services like the App Store — one of the most valuable companies on Earth."},
    {"symbol": "MSFT", "name": "Microsoft", "category": "Tech", "domain": "microsoft.com", "base": 448.2,
     "explain": "Sells Windows, Office and Azure cloud computing, and is a major force in enterprise AI."},
    {"symbol": "GOOGL", "name": "Alphabet", "category": "Tech", "domain": "google.com", "base": 178.9,
     "explain": "Parent of Google Search and YouTube; earns most of its money from online advertising."},
    {"symbol": "AMZN", "name": "Amazon", "category": "Retail", "domain": "amazon.com", "base": 197.4,
     "explain": "The e-commerce giant that also runs AWS, the world's largest cloud platform."},
    {"symbol": "NVDA", "name": "NVIDIA", "category": "Tech", "domain": "nvidia.com", "base": 128.6,
     "explain": "Designs the GPUs that power gaming and the AI boom — chips everyone wants right now."},
    {"symbol": "META", "name": "Meta Platforms", "category": "Tech", "domain": "meta.com", "base": 512.3,
     "explain": "Owns Facebook, Instagram and WhatsApp, funding big bets on AI and the metaverse with ad revenue."},
    {"symbol": "TSLA", "name": "Tesla", "category": "Auto", "domain": "tesla.com", "base": 246.8,
     "explain": "Leading electric-vehicle maker also working on batteries, solar and self-driving software."},
    {"symbol": "F", "name": "Ford Motor", "category": "Auto", "domain": "ford.com", "base": 11.2,
     "explain": "Century-old automaker famous for trucks like the F-150, now pushing into electric vehicles."},
    {"symbol": "JPM", "name": "JPMorgan Chase", "category": "Finance", "domain": "jpmorganchase.com", "base": 214.5,
     "explain": "The largest US bank, handling everything from checking accounts to Wall Street deal-making."},
    {"symbol": "V", "name": "Visa", "category": "Finance", "domain": "visa.com", "base": 275.1,
     "explain": "Runs the payment network behind billions of card swipes, taking a tiny fee on each one."},
    {"symbol": "KO", "name": "Coca-Cola", "category": "Retail", "domain": "coca-cola.com", "base": 62.4,
     "explain": "Sells soft drinks worldwide and is a classic steady dividend-paying stock."},
    {"symbol": "MCD", "name": "McDonald's", "category": "Retail", "domain": "mcdonalds.com", "base": 291.7,
     "explain": "Global fast-food chain that earns heavily from franchising and real estate."},
    {"symbol": "DIS", "name": "Walt Disney", "category": "Media", "domain": "disney.com", "base": 96.3,
     "explain": "Entertainment powerhouse behind theme parks, Marvel, Star Wars and Disney+ streaming."},
    {"symbol": "NFLX", "name": "Netflix", "category": "Media", "domain": "netflix.com", "base": 685.9,
     "explain": "The streaming pioneer with hundreds of millions of subscribers worldwide."},
    {"symbol": "SPY", "name": "S&P 500 ETF", "category": "ETF", "domain": "ssga.com", "base": 548.2,
     "explain": "A single fund that tracks 500 top US companies — instant diversification in one buy."},
    {"symbol": "QQQ", "name": "Nasdaq-100 ETF", "category": "ETF", "domain": "invesco.com", "base": 478.6,
     "explain": "Tracks 100 of the biggest non-financial Nasdaq names — very tech-heavy exposure."},
]

STOCK_MAP = {s["symbol"]: s for s in STOCKS}
CATEGORIES = ["All", "Tech", "Auto", "Finance", "Retail", "Media", "ETF"]


def _seed(symbol: str, salt: str = "") -> float:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    h = hashlib.md5(f"{symbol}-{day}-{salt}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF  # 0..1


def fallback_quote(symbol: str):
    s = STOCK_MAP[symbol]
    base = s["base"]
    change_pct = (_seed(symbol) - 0.5) * 6.0  # -3%..+3%
    price = round(base * (1 + change_pct / 100), 2)
    change = round(price - base, 2)
    return {
        "symbol": symbol,
        "price": price,
        "change": change,
        "change_pct": round(change_pct, 2),
        "source": "simulated",
    }


def fallback_history(symbol: str, points: int = 30, end_price: float | None = None):
    """Generate a smooth pseudo-random price history ending near the current price.

    If end_price is provided (e.g. a live quote), the series is shifted so its
    last point matches it, keeping the chart visually consistent with the header.
    """
    s = STOCK_MAP[symbol]
    base = s["base"]
    series = []
    val = base * (0.9 + _seed(symbol, "start") * 0.1)
    for i in range(points):
        drift = (_seed(symbol, f"d{i}") - 0.45) * base * 0.03
        wave = math.sin(i / 4.0) * base * 0.01
        val = max(base * 0.6, val + drift + wave)
        series.append(round(val, 2))
    target = end_price if end_price else fallback_quote(symbol)["price"]
    # shift the whole series so it ends exactly at the target price
    shift = target - series[-1]
    series = [round(max(base * 0.4, v + shift), 2) for v in series]
    series[-1] = round(target, 2)
    return series
