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

## Backlog / Remaining
- **P1:** Add real Alpha Vantage key to enable live quotes (env `ALPHA_VANTAGE_API_KEY`).
- **P1:** Watchlist / favorite stocks; link stocks to relevant lessons.
- **P2:** Weekly leaderboard reset, friends leaderboard, push reminders (only on request).
- **P2:** More lesson types (fill-in-blank, match pairs), spaced repetition review.

## Test Credentials
See `/app/memory/test_credentials.md` (demo@tradequest.app / demo123).

## Notes
- Stock quotes/history are SIMULATED (deterministic) until an Alpha Vantage key is added.
- Google OAuth cannot be automated in tests (Emergent-managed).
