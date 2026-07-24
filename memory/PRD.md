# TradeQuest — Product Requirements Document

## Original Problem Statement
Build a Duolingo-style app for learning Stocks — lessons, XP, streaks, basic stock education, and an explanation of each stock.

## User Choices
- Starter content (agent-generated lessons)
- Full gamification: XP, streaks, daily goals, levels, badges, leaderboard
- Stocks Explorer with live data (Alpha Vantage; simulated fallback when no key)
- Auth: BOTH JWT email/password AND Emergent-managed Google social login
- Visual: Clean & modern fintech (dark, emerald + amber accents)

## Architecture
- **Frontend:** Expo SDK 54, expo-router (file-based), custom fonts (Barlow Condensed + Manrope), react-native-gifted-charts + react-native-svg, expo-blur glass header, expo-haptics. Auth state via AuthContext; JWT stored in expo-secure-store.
- **Backend:** FastAPI + Motor (MongoDB). Own JWT for both password & Google users. Curriculum/stocks are static Python modules (`content.py`, `stocks.py`).
- **DB collections:** `users` (progress, xp, streak, badges embedded).

## Core Requirements (static)
- Gamified learning path (winding nodes, unlock progression)
- Lesson player: teaching cards + MCQ quizzes with instant feedback
- XP scaled by accuracy, levels (100 XP/level), daily goal, streaks, 8 badges
- Leaderboard ranked by XP (+ seeded demo bots)
- Stocks Explorer: search, category chips, plain-English explainers, price/chart detail

## Implemented (2026-06)
- Auth: signup/login/me/logout + Google OAuth exchange (Emergent). ✅ 15/15 backend tests pass.
- Curriculum: 5 units, 15 lessons with lock/unlock logic. ✅
- Lesson completion: XP + streak + daily goal + badge awards. ✅ (verified end-to-end in UI)
- Progress, Badges, Leaderboard, Stocks list/detail (simulated quotes). ✅
- Full dark fintech UI across 4 tabs + lesson + stock detail. ✅

## Implemented — Iteration 2 (2026-06): AI Tutor + Monetization
- **Google sign-in hardened:** web redirect-return parsing + mobile cold-start deep links (Linking.getInitialURL + url listener). ✅
- **AI Tutor (Claude Sonnet 4.6 via Emergent LLM key):** `POST /api/tutor/chat`, history, status; new "AI Tutor" tab with chat UI (react-native-keyboard-controller). Free tier 3 msgs/day, Pro unlimited. ✅ (real Claude replies verified)
- **7-day free Pro trial:** every new user gets full Pro for 7 days (no card); `is_pro`/`pro_source` computed. ✅
- **PayPal monthly Pro ($4.99):** product+plan (7-day trial cycle + monthly), subscription create/approve/activate/status/cancel via PayPal REST. Paywall screen + profile pro-banner + pro-locked advanced units (u4/u5) routing to paywall. ✅ backend graceful when keys unset. ⚠️ NEEDS real PayPal sandbox Client ID + Secret to complete live approval flow.
- Backend tests: 26/26 pytest passing.

## Backlog / Remaining
- **P0 (to finish PayPal):** user must supply PAYPAL_CLIENT_ID + PAYPAL_SECRET (sandbox) in backend/.env; then test full approval flow.
- **P1:** Add real Alpha Vantage key for live quotes.
- **P1:** Watchlist / favorite stocks; link stocks to relevant lessons; PayPal webhook for auto-renew/expiry sync.
- **P2:** Streaming tutor responses; weekly leaderboard reset.

## Test Credentials
See `/app/memory/test_credentials.md` (demo@tradequest.app / demo123).

## Implemented — Iteration 5 (2026-06): Watchlist
- **Watchlist:** users can star favorite stocks (star toggle on Explore cards + stock detail top bar). Watchlisted stocks are pinned to the top of the Explorer under a "Watchlist" section (rest under "All Stocks"). Stored as `user.watchlist` array. Endpoint: `POST /api/watchlist/{symbol}/toggle`; `in_watchlist` flag added to `/api/stocks` and `/api/stocks/{symbol}`. Localized (EN/DE/ES). ✅ 11/11 backend tests + frontend E2E pass.

## Notes
- Live stock quotes come from **Finnhub** (FINNHUB_API_KEY set; free tier 60 calls/min). Both the Stocks list and detail screens show live prices with a 45s TTL cache. Price charts use a deterministic simulated history since Finnhub's free tier excludes candle data. Falls back to simulated quotes if the key is unset/request fails.
- Google OAuth cannot be automated in tests (Emergent-managed).
