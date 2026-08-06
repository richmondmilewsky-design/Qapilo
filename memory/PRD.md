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
- **Curriculum:** 50 units / 150 lessons across 5 difficulty tiers (Beginner→Pro), fully trilingual (EN/DE/ES). Generated via Claude (generate_curriculum.py) into curriculum_data.json, loaded by curriculum.py. Free tiers = u1-u20; Pro = u21-u50. Endless Practice mode (/practice) recycles questions with rising difficulty + scaled XP.
- **AI Tutor real-time:** injects live Finnhub prices (auto-detects tickers/company names) and, when TAVILY_API_KEY is set, recent Tavily news snippets, then Claude answers with a mandatory "not financial advice" disclaimer. Works without Tavily (prices + disclaimer) — news activates once key added.
- Google OAuth cannot be automated in tests (Emergent-managed).

## Fix — Iteration 13 (2026-06): Keyboard overlap on form screens
- Wrapped root `_layout.tsx` with `KeyboardProvider` (react-native-keyboard-controller@1.18.5).
- Replaced RN `KeyboardAvoidingView`+`ScrollView` with `KeyboardAwareScrollView` (bottomOffset=24) on auth, forgot-password, reset-password, support screens so focused inputs stay above the keyboard on small devices (iPhone 12 / Android). Logic, design, texts unchanged. Web-preview E2E passed (13/13); native on-device validation still recommended.

## Feature — Iteration 14 (2026-06): Auth UX polish
- Password fields (auth + reset-password) now have an eye toggle to show/hide text.
- Keyboard "next" chaining: Enter jumps Name→Email→Password (auth) and Code→Password (reset); Enter on password submits.
- Friendly welcome toast on Learn screen after email/password login/signup ("Welcome back/Welcome, {name}!"), one-shot via AsyncStorage key `qapilo_welcome`, EN/DE/ES. AuthContext login/signup now return the User. Frontend E2E 8/8 passed (iteration_14).

## Feature — Iteration 15 (2026-06): Password strength + Stay signed in
- Signup: live password-strength meter (3 bars + Weak/Medium/Strong), score = length>=8 + mixed case + digit + symbol. Hidden in login mode / when empty.
- Auth: "Stay signed in" toggle (default ON). Writes AsyncStorage `tq_remember`; when OFF, AuthContext drops the persisted SecureStore token on next cold app launch (device-only behavior). Localized EN/DE/ES. Frontend E2E passed (iteration_15).
