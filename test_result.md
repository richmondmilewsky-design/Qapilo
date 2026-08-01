#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: "Duolingo-style stock learning app. Recent changes: (1) multi-language i18n (English/German/Spanish) across backend endpoints (lang query param) and all frontend screens; (2) migrated live stock data from Alpha Vantage to Finnhub API."

backend:
  - task: "Finnhub live stock quotes migration"
    implemented: true
    working: "NA"
    file: "server.py, stocks.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "Replaced Alpha Vantage av_quote with finnhub_quote (GET /quote, X-Finnhub-Token header, 45s TTL cache). /api/stocks now returns LIVE quotes for all symbols concurrently (source='finnhub'). /api/stocks/{symbol} returns live quote + deterministic history ending at live price. Finnhub free tier excludes candle data so history stays simulated. Verified via curl: AAPL price 321.66 source finnhub."

  - task: "i18n localized backend endpoints (lang=en|de|es)"
    implemented: true
    working: "NA"
    file: "server.py, content_i18n.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "All content endpoints accept lang param and return localized curriculum/lessons/stock explanations. Needs E2E verification that en/de/es all return correct localized content and no endpoint regressions."

frontend:
  - task: "i18n frontend (language switcher, localized UI across all screens)"
    implemented: true
    working: "NA"
    file: "src/i18n/*, all app/ screens, components/LanguageButton.tsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
        - working: "NA"
          agent: "main"
          comment: "expo-localization auto-detect + manual LanguageButton in header. Hardcoded strings replaced with useI18n() keys across all screens. Needs E2E: verify switching languages updates UI + backend content, core flows (learn path, lesson quiz, stocks explorer, AI tutor, paywall) still work."

metadata:
  created_by: "main_agent"
  version: "1.1"
  test_sequence: 3
  run_ui: true

test_plan:
  current_focus:
    - "Finnhub live stock quotes migration"
    - "i18n localized backend endpoints (lang=en|de|es)"
    - "i18n frontend (language switcher, localized UI across all screens)"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
    - agent: "main"
      message: "COMMS & PRIVACY SPRINT. NEW backend: (1) transactional email via Emergent-managed Resend in email_service.py (provider-agnostic send_and_log + EN/DE/ES templates: password_reset, account_deleted, support_received, support_forwarded, subscription_activated/cancelled, trial_started; minimal delivery log in email_events with TTL retention). (2) Password reset: POST /api/auth/forgot-password (neutral response, rate-limited by email+IP), POST /api/auth/reset-password (sha256-hashed one-time token, TTL from RESET_TOKEN_TTL_MIN, single-use, invalidates older, sets sessions_invalid_before to invalidate old JWTs, min 8-char pw). (3) POST /api/support/request (category/subject/message/optional reply_email, header-injection guard, rate-limited, stores in support_requests w/ TTL, confirmation email + forward to QAPILO_SUPPORT_EMAIL if set). (4) Emails hooked into signup(trial), subscription activate/cancel, account delete (sends before erasing email). NEW frontend screens: /forgot-password, /reset-password (reads ?token= or manual code), /support; 'Forgot password?' link on /auth; 'Contact support' row in /settings. Unsplash cover in profile.tsx replaced with local brand gradient (removed only remote decorative image; Clearbit logos unchanged per owner). Env added: EMERGENT_EMAIL_KEY, EMAIL_FROM_NAME=Qapilo, QAPILO_SUPPORT_EMAIL(empty placeholder), QAPILO_APP_URL(empty), RESET_TOKEN_TTL_MIN=30, *_RETENTION_DAYS. NOTE: real email delivery to test.app/resend test addresses is blocked by proxy deliverability (422) — real recipient domains deliver; email send never blocks the request. Already verified via curl: neutral forgot response (unknown==known), token hash-only storage, invalid/weak/valid/reused reset, old-JWT invalidation, login old fails/new works, support ref + missing-fields 400, forgot rate-limit 429, all templates render EN/DE/ES. Please E2E test frontend: /forgot-password neutral confirm, /reset-password invalid+valid (inject a token via DB if needed), /support submit shows ref, settings 'Contact support' navigation, and re-confirm the backend endpoints. No analytics/crash/notification systems exist (push intentionally skipped)."

comms_privacy_sprint:
  backend:
    - task: "Transactional email + password reset + support endpoints"
      implemented: true
      working: true
      file: "server.py, email_service.py, errors_i18n.py"
      priority: "high"
      needs_retesting: false
  frontend:
    - task: "forgot-password / reset-password / support screens + settings row + auth link; Unsplash cover removed"
      implemented: true
      working: "NA"
      file: "app/forgot-password.tsx, app/reset-password.tsx, app/support.tsx, app/auth.tsx, app/settings.tsx, app/(tabs)/profile.tsx"
      priority: "high"
      needs_retesting: true (1) Onboarding /agreement now has two required checkboxes (Terms of Service + financial disclaimer) that must BOTH be checked to enable 'Agree & Continue', plus three OPTIONAL toggles (analytics, product improvements, marketing emails) default OFF. Submits to POST /api/auth/accept-terms with body {accepted_terms, accepted_disclaimer, consent_analytics, consent_product, consent_marketing}. Backend returns 400 (consent_required, localized) if either required flag is false. (2) NEW endpoint PATCH /api/auth/consents to update the 3 optional consents anytime (GDPR withdrawal). (3) Settings screen has a new 'Consents' section with 3 Switch rows that call PATCH and update the user. Consent flags added to public_user + account export. Verified backend via python requests: signup defaults false, 400 on missing required, accept persists all flags, patch updates, export includes flags. Please E2E test: agreement checkbox gating + optional toggles + submit; settings consent switches persist. Test creds in /app/memory/test_credentials.md or sign up new."

new_feature_consent_split:
  backend:
    - task: "Split consent endpoints (accept-terms body + PATCH /auth/consents)"
      implemented: true
      working: true
      file: "server.py, errors_i18n.py"
      priority: "high"
      needs_retesting: false
  frontend:
    - task: "Agreement screen two-block consent + Settings consent management"
      implemented: true
      working: "NA"
      file: "app/agreement.tsx, app/settings.tsx, src/i18n/translations.ts"
      priority: "high"
      needs_retesting: true