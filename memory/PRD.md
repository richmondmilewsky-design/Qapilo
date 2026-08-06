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

## Fix — Iteration 16 (2026-06): Opaque modal/overlay backgrounds
- Modal cards were translucent (surfaceSecondary = rgba white 0.05) causing background bleed-through / unreadable text. Added opaque theme tokens `elevated`/`elevatedSecondary` and applied to all overlays: language picker (I18nContext), AI Tutor first-use notice (tutor.tsx), settings data-export sheet (settings.tsx). Backdrops darkened to 0.75. Verified via screenshots — text now crisp.

## Features — Iteration 16 (2026-06): Biometric login, Streak celebration, Email verification
- Biometric quick sign-in (expo-local-authentication, device-only): opt-in prompt after first password login, then Face ID/Touch ID button on auth screen. Face ID permission added to app.json.
- Streak celebration overlay on first login of day (streak>=1), once/day.
- Non-blocking email verification: 6-digit code emailed on password signup; amber banner + code-entry modal on Learn; endpoints /auth/verify-email + /auth/resend-verification; public_user + /auth/me expose email_verified. All EN/DE/ES.

## Features — Iteration 17 (2026-06): Verify reminder + Streak milestones
- Gentle 2nd email-verification reminder: unverified users whose account is >3 days old see a one-time reminder modal on Learn (throttled to once/3 days via tq_verify_reminded). public_user now exposes created_at.
- Streak milestones (7/30/100): special trophy celebration overlay ("Milestone reached! / New badge unlocked") shown once per milestone (tq_streak_milestone_<n>). New badges streak_30 & streak_100 added + awarded in evaluate_badges. Daily/milestone celebrations unified into one overlay. Backend 12/12 + frontend all pass (iteration_17).

## Foundation — Iteration 18 (2026-06): Free usage phase (no payment)
- Central access function: backend/server.py `compute_pro(u)` (~L233), spread into public_user → on every user object & /auth/me.
- Free phase active until 30 days (FREE_TRIAL_DAYS) OR level 30 (FREE_LEVEL_LIMIT). Subscription (pro_active) = premium always.
- Fields: reused trial_ends_at, pro_active, subscription_status, xp→level (xp_into_level), created_at; added stored trial_started_at (signup/google/apple) + trial_ends_at now = signup+30d. New derived/exposed: trial_status (active|ended|premium), trial_end_reason (time|level|null), current_level, free_level_limit.
- PayPal TRIAL_DAYS(7) intentionally untouched (no payment change). Internal status only — full paywall is a later step.

## Feature — Iteration 19 (2026-06): Premium paywall (UI + status wiring, no billing)
- New central product config: frontend/src/constants/plans.ts (PLANS with prices/trials/features — single source, no hardcoded prices in UI).
- Rewrote app/paywall.tsx: title/subtitle, Free vs Premium comparison, 4 offers (Individual yearly=default & "Most popular", Family, Lite w/ ads, Monthly), single-select, adaptive CTA (trial->"Start free trial", monthly->"Unlock Premium"), Cancel anytime, Restore purchases (real /subscription/status), Privacy/Terms links, scrollable. Purchases are clearly-marked PLACEHOLDERS (no StoreKit/Play billing yet).
- Appearance wired to status: app/index.tsx gate redirects to /paywall when trial_status==='ended' && !is_pro (after terms+experience). Dismissible (close -> tabs) since billing is placeholder.
- public_user fix: now returns experience_level (was missing). Added trial_status etc. to frontend User type. All strings EN/DE/ES.

## Curriculum — Blueprint expansion (2026-06): 50 → 200 units
- Rewrote backend/curriculum_blueprint.py only. Clean rebuild: 200 units (u1–u200), 3 lessons each (l1–l600), 10 tiers × 20 units.
- Tiers: 1 Geld verstehen · 2 Persönliche Finanzen · 3 Investieren lernen · 4 Aktien verstehen · 5 ETFs & Anlageklassen · 6 Unternehmen analysieren · 7 Portfolio & Psychologie · 8 Märkte & Makro · 9 Professionelles Investieren · 10 Investment Mastery.
- Reused existing old-50 content, moved to correct tiers (money→T1, personal finance→T2, investing basics→T3, stocks→T4, funds→T5, fundamental analysis→T6, portfolio/psychology→T7, professional→T9).
- IDs are new authoritative version; old lesson IDs not preserved (no production progress to keep).
- NOT changed: curriculum_data.json (still old content, cards/quizzes NOT regenerated), curriculum.py, generate_curriculum.py, API, frontend, DB, PRO_UNITS, progress logic.
- TIER_META already had 10 tiers; build_units_spec assigns tier by position (i-1)//20+1.
- Structural verify passed: 200 units, 600 lessons, 10 tiers×20, unit/lesson IDs unique & contiguous, all units 3 lessons, dependent files parse OK.
- NEXT (deferred, on user request only): generate cards/quizzes/translations into curriculum_data.json for the new 200-unit structure.
