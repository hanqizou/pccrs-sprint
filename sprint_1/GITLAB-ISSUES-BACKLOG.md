# CardSmart — GitLab Issues Backlog

> Complete project backlog organized by Sprint. Each issue includes title, description, labels, and suggested assignee.
> Create these issues on GitLab as your Project Backlog.

---

## Labels Setup (Create These Labels in GitLab First)

Go to GitLab → Issues → Labels → New Label and create the following:

| Label | Suggested Color | Purpose |
|-------|----------------|---------|
| `sprint-0` | #6699cc | Sprint 0 issues |
| `sprint-1` | #0075ca | Sprint 1 issues |
| `sprint-2` | #009933 | Sprint 2 issues |
| `sprint-3` | #d93f0b | Sprint 3 issues |
| `sprint-4` | #7057ff | Sprint 4 issues |
| `feature` | #0e8a16 | New feature |
| `bug` | #d73a4a | Bug fix |
| `infra` | #f9d0c4 | Infrastructure / DevOps |
| `docs` | #0075ca | Documentation |
| `test` | #bfdadc | Testing related |
| `ui` | #c5def5 | Frontend / UI |
| `backend` | #e4e669 | Backend logic |
| `admin` | #fbca04 | Admin functionality |
| `priority-high` | #b60205 | High priority |
| `priority-medium` | #ff9f1c | Medium priority |
| `priority-low` | #c2e0c6 | Low priority |

---

## Milestones Setup

Go to GitLab → Issues → Milestones and create:

| Milestone | Due Date (adjust to your course schedule) |
|-----------|------|
| Sprint 0 — Scaffold | Week 1 end |
| Sprint 1 — Auth & Ingestion | Week 3 end |
| Sprint 2 — Recommendation & Charts | Week 5 end |
| Sprint 3 — Plan, History, Admin | Week 7 end |
| Sprint 4 — Deploy & Polish | Week 9 end |

---

## Sprint 0 Issues — Project Scaffolding

### Issue #1: Initialize Flask project structure
- **Labels:** `sprint-0`, `infra`, `priority-high`
- **Assignee:** Person A
- **Milestone:** Sprint 0
- **Description:**
```
Create the full project directory structure as defined in MASTER.md:
- run.py (entry point)
- app/__init__.py (app factory with Blueprint registration)
- app/config.py (Dev/Prod/Test configs)
- requirements.txt
- .env.example
- .gitignore

**Acceptance Criteria:**
- [ ] `python run.py` starts Flask dev server on port 5000
- [ ] Config loads correctly from env vars
- [ ] All extensions initialized (SQLAlchemy, Flask-Login, Flask-WTF, Flask-Migrate)
```

### Issue #2: Create all SQLAlchemy models
- **Labels:** `sprint-0`, `backend`, `priority-high`
- **Assignee:** Person A
- **Milestone:** Sprint 0
- **Description:**
```
Create 6 model files under app/models/:
- User (with password hashing methods)
- Transaction
- Card
- RecommendationRun
- PlanCommit
- SystemEvent

Schema details in MASTER.md.

**Acceptance Criteria:**
- [ ] All models importable from app.models
- [ ] flask db migrate creates correct tables
- [ ] flask db upgrade applies without error
```

### Issue #3: Create Blueprint stubs for all route modules
- **Labels:** `sprint-0`, `backend`, `priority-high`
- **Assignee:** Person A
- **Milestone:** Sprint 0
- **Description:**
```
Create 8 Blueprint modules under app/routes/:
auth, dashboard, ingestion, analysis, plan, history, reporting, admin

Each has a placeholder route returning a template.
All registered in app/__init__.py.

**Acceptance Criteria:**
- [ ] Every route returns 200 (placeholder page)
- [ ] No 404s for any nav link
```

### Issue #4: Create base template and all placeholder pages
- **Labels:** `sprint-0`, `ui`, `priority-high`
- **Assignee:** Person D
- **Milestone:** Sprint 0
- **Description:**
```
Create templates/base.html with:
- Bootstrap 5 CDN
- Plotly.js CDN
- Navigation bar (auth-aware: different links for logged-in vs anonymous users)
- Admin links visible only to admin users
- Flash messages area
- Footer

Create all 12+ template files with placeholder content.

**Acceptance Criteria:**
- [ ] Nav shows correct links based on auth state
- [ ] All pages extend base.html correctly
- [ ] Bootstrap styles load properly
```

### Issue #5: Create seed data files (cards + demo transactions)
- **Labels:** `sprint-0`, `backend`, `priority-medium`
- **Assignee:** Person B
- **Milestone:** Sprint 0
- **Description:**
```
Create:
1. seed_data/cards.json — 10-15 popular credit cards with realistic data
2. seed_data/demo_transactions.csv — ~200 transactions over 6 months (CSV format)
3. seed_data/demo_transactions.json — same data in JSON format (second file structure)
4. seed_data/seed_db.py — script to load cards + create demo user + admin user

**Acceptance Criteria:**
- [ ] cards.json contains 10+ cards with multipliers, fees, transfer partners
- [ ] CSV and JSON contain the same transactions in different formats
- [ ] seed_db.py populates DB without errors
- [ ] Admin user created: admin@cardsmart.com / admin123
```

### Issue #6: Set up pytest framework and smoke tests
- **Labels:** `sprint-0`, `test`, `priority-medium`
- **Assignee:** Person E
- **Milestone:** Sprint 0
- **Description:**
```
Create:
- tests/conftest.py with fixtures (client, db_session, logged_in_client, admin_client)
- tests/test_smoke.py — test every route returns expected status code

**Acceptance Criteria:**
- [ ] pytest runs without errors
- [ ] All routes return 200 or 302 (auth redirect)
```

---

## Sprint 1 Issues — Auth, Ingestion & Card Catalog

### Issue #7: Implement home page for unauthenticated users (Screen #1)
- **Labels:** `sprint-1`, `ui`, `feature`, `priority-high`
- **Assignee:** Person D
- **Milestone:** Sprint 1
- **Description:**
```
Core Requirement Screen #1 (10 pts).

Design and build the landing page for unauthenticated users:
- Hero section with value proposition
- Feature highlights (3 key benefits)
- CTA buttons: "Get Started" → Register, "Log In" → Login
- If user is already logged in, redirect to /dashboard
- Must be visually DISTINCT from the authenticated dashboard

**Acceptance Criteria:**
- [ ] GET / unauthenticated → 200, shows hero + CTA
- [ ] GET / authenticated → 302 redirect to /dashboard
- [ ] Visually distinct from dashboard
- [ ] Paper prototype reviewed by TA
- [ ] Test cases documented
```

### Issue #8: Implement user registration (Screen #2)
- **Labels:** `sprint-1`, `feature`, `backend`, `priority-high`
- **Assignee:** Person A
- **Milestone:** Sprint 1
- **Description:**
```
Core Requirement Screen #2 (25 pts).

Registration page with:
- Form: email, password, confirm_password, display_name
- Validation: email format, password min 8 chars, passwords must match, no duplicate email
- Password hashed with werkzeug (bcrypt)
- On success: create User, auto-login, redirect to /dashboard
- Log SystemEvent: type='user_register'
- CSRF protection via Flask-WTF

**Acceptance Criteria:**
- [ ] Valid registration → account created, redirected to dashboard
- [ ] Duplicate email → error message
- [ ] Invalid email format → error message
- [ ] Passwords don't match → error message
- [ ] Password stored as hash, never plaintext
- [ ] pytest tests pass
```

### Issue #9: Implement user login/logout (Screen #3)
- **Labels:** `sprint-1`, `feature`, `backend`, `priority-high`
- **Assignee:** Person A
- **Milestone:** Sprint 1
- **Description:**
```
Core Requirement Screen #3 (25 pts).

Login page with:
- Form: email, password
- Flask-Login session management
- Generic error: "Invalid email or password" (do not reveal which field is wrong)
- Logout route: GET /auth/logout → clear session, redirect to /
- Update User.last_login timestamp on successful login
- Disabled users (is_active=False) cannot log in

**Acceptance Criteria:**
- [ ] Valid login → redirect to /dashboard
- [ ] Wrong password → generic error message
- [ ] Non-existent email → same generic error
- [ ] Logout clears session
- [ ] Disabled user cannot login
- [ ] pytest tests pass
```

### Issue #10: Implement CSV file upload (Data Integration — Format A)
- **Labels:** `sprint-1`, `feature`, `backend`, `priority-high`
- **Assignee:** Person B
- **Milestone:** Sprint 1
- **Description:**
```
Core Requirement Data Integration (50 pts — partial).

Upload page for CSV transactions:
- Accept .csv with columns: date, merchant, amount, category
- Validate: required columns exist, date is parseable, amount is numeric and > 0
- Compute SHA256 hash of file content → import_id for idempotency
- Store transactions in the Transaction table
- Log SystemEvent: type='import'

**Acceptance Criteria:**
- [ ] Valid CSV → transactions in DB + SystemEvent logged
- [ ] Missing columns → error with specific column names listed
- [ ] Duplicate upload → rejected with "Already imported"
- [ ] Empty file → rejected
- [ ] Negative or non-numeric amount → rejected
```

### Issue #11: Implement JSON file upload (Data Integration — Format B)
- **Labels:** `sprint-1`, `feature`, `backend`, `priority-high`
- **Assignee:** Person B
- **Milestone:** Sprint 1
- **Description:**
```
Core Requirement Data Integration (50 pts — partial).

Upload page for JSON transactions:
- Accept .json with structure: { "transactions": [{ "date", "description", "amount_cents", "mcc_code" }] }
- Map mcc_code → category via category_mapper service
- Convert amount_cents → dollars (divide by 100)
- Same idempotency and validation logic as CSV

**Acceptance Criteria:**
- [ ] Valid JSON → transactions in DB
- [ ] MCC codes mapped to correct categories
- [ ] amount_cents correctly converted (1450 → $14.50)
- [ ] Invalid structure → helpful error message
```

### Issue #12: Build MCC category mapper service
- **Labels:** `sprint-1`, `backend`, `priority-medium`
- **Assignee:** Person B
- **Milestone:** Sprint 1
- **Description:**
```
Create app/services/category_mapper.py:
- Dictionary mapping MCC code ranges to categories
- 5812-5814 → dining, 5411 → groceries, 4511 → travel (airlines), etc.
- Fallback to 'other' for unknown codes
- Used by JSON import to categorize transactions

**Acceptance Criteria:**
- [ ] Common MCC codes mapped correctly
- [ ] Unknown MCC → 'other'
- [ ] Unit tests cover all major categories
```

### Issue #13: Integrate ExchangeRate REST API (FX Service)
- **Labels:** `sprint-1`, `feature`, `backend`, `priority-high`
- **Assignee:** Person B
- **Milestone:** Sprint 1
- **Description:**
```
Core Requirement Data Integration — REST/JSON API (50 pts — partial).

Create app/services/fx_service.py:
- Fetch rates from ExchangeRate API (REST/JSON endpoint)
- Cache rates (24-hour TTL) to avoid hitting free-tier limit
- On file import: convert foreign currency transactions to USD
- Handle API errors gracefully: use cached rates if API is unavailable, or warn user
- Display "Last FX update" timestamp on ingestion page

**Acceptance Criteria:**
- [ ] API call returns rates and caches them
- [ ] Cached rates used when API is unavailable
- [ ] Foreign transactions converted correctly
- [ ] API key stored in .env, never in code
```

### Issue #14: Build admin card catalog CRUD
- **Labels:** `sprint-1`, `admin`, `feature`, `priority-medium`
- **Assignee:** Person E
- **Milestone:** Sprint 1
- **Description:**
```
Admin interface for managing the card knowledge base:
- GET /admin/cards — list all cards
- GET/POST /admin/cards/new — create new card
- GET/POST /admin/cards/<id>/edit — edit existing card
- Only accessible to admin users (role check on every route)
- Validate: multiplier >= 0, annual_fee >= 0, card_id unique
- Log SystemEvent on create/update

**Acceptance Criteria:**
- [ ] Admin can list, create, and edit cards
- [ ] Normal user → 403 Forbidden
- [ ] Invalid data → validation error
- [ ] SystemEvent logged for each admin action
```

### Issue #15: Build minimal dashboard (Screen #4 — Sprint 1 version)
- **Labels:** `sprint-1`, `ui`, `feature`, `priority-medium`
- **Assignee:** Person D
- **Milestone:** Sprint 1
- **Description:**
```
Core Requirement Screen #4 (50 pts — Sprint 1 minimal version, expanded in Sprint 2).

Authenticated dashboard showing:
- Welcome message with user's display name
- Quick stats (if data exists): total transactions, date range, top 3 categories by spend
- "No data yet" state with CTA to upload transactions
- Links to: Import Data, Run Recommendation, View History
- Must be visually DISTINCT from the unauthenticated home page

**Acceptance Criteria:**
- [ ] Requires authentication (@login_required)
- [ ] Shows correct stats when data exists
- [ ] Shows helpful empty state when no data
- [ ] Visually distinct from home page
```

### Issue #16: Write Sprint 1 tests
- **Labels:** `sprint-1`, `test`, `priority-medium`
- **Assignee:** Person A + Person B
- **Milestone:** Sprint 1
- **Description:**
```
Complete test suites for Sprint 1 features:
- tests/test_auth.py — register, login, logout, validation, disabled user
- tests/test_ingestion.py — CSV upload, JSON upload, duplicate detection, FX conversion
- tests/test_admin.py — card CRUD, role check (403 for non-admin)

**Acceptance Criteria:**
- [ ] pytest passes all tests
- [ ] Auth: 5+ test cases
- [ ] Ingestion: 6+ test cases
- [ ] Admin: 4+ test cases
```

### Issue #17: Sprint 1 paper prototypes and test case documentation
- **Labels:** `sprint-1`, `docs`, `priority-high`
- **Assignee:** Person D (draw) + all (review)
- **Milestone:** Sprint 1
- **Description:**
```
For each screen implemented in Sprint 1, create:
1. Paper prototype (hand-drawn sketch or digital wireframe)
2. Test case documentation (list of test scenarios)

Screens: Home (#1), Register (#2), Login (#3), Dashboard (#4)

Required by Core Requirements: 5 pts per screen for prototype + 5 pts for test cases.

**Acceptance Criteria:**
- [ ] 4 paper prototypes created and photographed/scanned
- [ ] Test cases documented per screen
- [ ] Prototypes shown to TA for review
- [ ] Files saved in docs/prototypes/
```

### Issue #18: Sprint 1 Status Report
- **Labels:** `sprint-1`, `docs`, `priority-high`
- **Assignee:** Person E (compile) + all (contribute)
- **Milestone:** Sprint 1
- **Description:**
```
Complete the Sprint 1 Status Report using the template in prompts/SPRINT-STATUS-REPORT-TEMPLATE.md:
1. List of GitLab issues opened/closed during the sprint
2. UML class diagram (initial version — all 6 models)
3. Sprint review paragraph
4. Sprint retrospective paragraph
5. Sprint planning paragraph (plan for Sprint 2)
6. Additional comments/concerns

**Acceptance Criteria:**
- [ ] All 6 sections completed
- [ ] UML diagram includes all models with relationships
- [ ] Report committed to docs/reports/sprint-1-status-report.md
- [ ] Submitted on Canvas (if required)
```

---

## Sprint 2 Issues — Recommendation Engine & Charts

### Issue #19: Implement recommendation engine service
- **Labels:** `sprint-2`, `backend`, `feature`, `priority-high`
- **Assignee:** Person C
- **Milestone:** Sprint 2
- **Description:**
```
Core product logic. Create app/services/recommendation_engine.py:
- Aggregate spend by category (annualized)
- Compute net annual value per card: (rewards - annual fee + credits)
- Handle travel vs cashback mode, transfer partner valuations
- Apply category caps
- Return top 3 cards with: net_value, drivers, break_even
- Must be DETERMINISTIC (same input → same output)

**Acceptance Criteria:**
- [ ] Known input → verified correct output (manual calculation check)
- [ ] Dining-heavy spender → dining bonus card ranks highest
- [ ] $0 fee cards beat high-fee cards for low spenders
- [ ] fee_tolerance filter works
- [ ] 0 transactions → empty result, no crash
- [ ] Deterministic: run twice → identical results
```

### Issue #20: Build Analysis: Informed Decision page (Screen #5)
- **Labels:** `sprint-2`, `ui`, `feature`, `priority-high`
- **Assignee:** Person C + Person D
- **Milestone:** Sprint 2
- **Description:**
```
Core Requirement Screen #5 (25 pts).

The main recommendation page:
- Preferences panel: mode, partners, fee tolerance, CPP slider
- Results: top 3 cards side-by-side with net value + drivers
- Explanation panel: natural-language reasoning
- Charts (see Issues #23, #24, #25)
- "Commit Plan" button (wired up in Sprint 3)
- AJAX update on slider/preference change

**Acceptance Criteria:**
- [ ] Generates recommendations from user's data
- [ ] Shows top 3 cards with breakdown
- [ ] Explanation panel is readable and accurate
- [ ] Stores RecommendationRun in DB
- [ ] SystemEvent logged
```

### Issue #21: Build Analysis: Current Data page (Screen #6)
- **Labels:** `sprint-2`, `ui`, `feature`, `priority-high`
- **Assignee:** Person D
- **Milestone:** Sprint 2
- **Description:**
```
Core Requirement Screen #6 (25 pts).

User's spending analysis page:
- Spend by category bar chart
- Monthly trend line chart
- Summary stats: total spend, average monthly, top category
- Current committed cards (if any from previous plan commits)

**Acceptance Criteria:**
- [ ] Charts render with user's real data
- [ ] Summary stats are accurate
- [ ] Empty state handled gracefully
```

### Issue #22: Enhance dashboard with recommendation preview (Screen #4 full)
- **Labels:** `sprint-2`, `ui`, `feature`, `priority-medium`
- **Assignee:** Person D
- **Milestone:** Sprint 2
- **Description:**
```
Expand the Sprint 1 dashboard to show:
- Top recommended card name + estimated value (if a recommendation exists)
- "Run Recommendation" CTA
- Spend snapshot summary

**Acceptance Criteria:**
- [ ] Dashboard shows recommendation preview if one exists
- [ ] Still shows upload CTA if no data
```

### Issue #23: Implement bar chart — Spend by Category (Chart 1/3)
- **Labels:** `sprint-2`, `ui`, `feature`, `priority-high`
- **Assignee:** Person D
- **Milestone:** Sprint 2
- **Description:**
```
Core Requirement Charting (25 pts per chart type).

Plotly.js bar chart on Analysis: Current Data page:
- X-axis: categories, Y-axis: annualized spend ($)
- Color-coded bars
- Hover tooltip shows exact amount + percentage of total

**Acceptance Criteria:**
- [ ] Chart renders correctly with real data
- [ ] Hover tooltip works
- [ ] Responsive on different screen widths
```

### Issue #24: Implement line chart — Monthly Trend (Chart 2/3)
- **Labels:** `sprint-2`, `ui`, `feature`, `priority-high`
- **Assignee:** Person D
- **Milestone:** Sprint 2
- **Description:**
```
Core Requirement Charting (25 pts per chart type).

Plotly.js line chart:
- X-axis: months, Y-axis: monthly spend or cumulative rewards
- Lines + markers

**Acceptance Criteria:**
- [ ] Chart renders with monthly aggregated data
- [ ] Handles fewer than 3 months of data gracefully
```

### Issue #25: Implement scatter plot — Card Value vs Fee (Chart 3/3)
- **Labels:** `sprint-2`, `ui`, `feature`, `priority-high`
- **Assignee:** Person D
- **Milestone:** Sprint 2
- **Description:**
```
Core Requirement Charting (25 pts per chart type).

Plotly.js scatter plot on Informed Decision page:
- X-axis: annual fee ($), Y-axis: net annual value ($)
- All cards as small dots, recommended cards as large highlighted dots
- Hover shows card name + net value

**Acceptance Criteria:**
- [ ] All cards plotted
- [ ] Recommended cards visually distinct
- [ ] Hover tooltip works
```

### Issue #26: Implement CPP slider custom interaction
- **Labels:** `sprint-2`, `ui`, `feature`, `priority-high`
- **Assignee:** Person D + Person C
- **Milestone:** Sprint 2
- **Description:**
```
Core Requirement Charting — custom interaction (required for full 75 pts; minus 10 pts if missing).

Cents-per-point slider on Informed Decision page:
- Range: 0.5 to 3.0 cpp, step 0.1
- On change: AJAX call to /api/recommend with updated CPP value
- Backend recomputes rankings and returns JSON
- Frontend updates: card rankings, all charts, explanation panel

**Acceptance Criteria:**
- [ ] Slider fires AJAX request (debounced ~300ms)
- [ ] Rankings update without page reload
- [ ] Charts re-render with new data
- [ ] Explanation text updates accordingly
```

### Issue #27: Build JSON API endpoint for AJAX recommendations
- **Labels:** `sprint-2`, `backend`, `feature`, `priority-high`
- **Assignee:** Person B
- **Milestone:** Sprint 2
- **Description:**
```
POST /api/recommend — JSON API for the frontend AJAX calls.

Accepts: { mode, preferred_partners, fee_tolerance, cpp_override }
Returns: { recommendations: [...], spend_by_category: [...], run_id }

Saves RecommendationRun + SystemEvent to database.

**Acceptance Criteria:**
- [ ] Returns valid JSON with expected fields
- [ ] RecommendationRun saved to DB
- [ ] Handles missing or invalid parameters gracefully
```

### Issue #28: Sprint 2 tests + paper prototypes + status report
- **Labels:** `sprint-2`, `test`, `docs`, `priority-medium`
- **Assignee:** All
- **Milestone:** Sprint 2
- **Description:**
```
- tests/test_recommendation.py — engine tests (known inputs, edge cases, determinism)
- Paper prototypes for Screens #5 and #6
- Sprint 2 Status Report (all 6 sections)
```

---

## Sprint 3 Issues — Plan, History, Reporting & Admin

### Issue #29: Implement Commit/Remove Plan — Buy/Sell (Screen #7)
- **Labels:** `sprint-3`, `backend`, `feature`, `priority-high`
- **Assignee:** Person C
- **Milestone:** Sprint 3
- **Description:**
```
Core Requirement Screen #7 (50 pts).

POST /plan/commit — save a card plan (Buy action)
POST /plan/remove — remove a card from plan (Sell action)
GET /plan/current — view currently committed plan

Transactions must be atomic: both PlanCommit record and SystemEvent must succeed or neither persists.

**Acceptance Criteria:**
- [ ] Commit creates PlanCommit record + SystemEvent
- [ ] Remove creates PlanCommit (action='remove') + SystemEvent
- [ ] Invalid rec_run_id → 400 error
- [ ] DB failure → full rollback, no partial state
- [ ] Current plan view shows correct cards
```

### Issue #30: Implement History screen (Screen #8)
- **Labels:** `sprint-3`, `ui`, `feature`, `priority-high`
- **Assignee:** Person D
- **Milestone:** Sprint 3
- **Description:**
```
Core Requirement Screen #8 (40 pts).

GET /history — filterable table of all SystemEvents for the current user:
- Columns: timestamp, type, summary, status
- Filters: date range picker, event type dropdown, text search
- Click row → detail view with full event information
- Pagination (20 per page)

**Acceptance Criteria:**
- [ ] All events displayed correctly
- [ ] Filters work (type, date range, search)
- [ ] Pagination works with 20+ events
- [ ] Empty state handled with helpful message
```

### Issue #31: Implement Reporting functionality (Screen #9)
- **Labels:** `sprint-3`, `ui`, `feature`, `priority-high`
- **Assignee:** Person B
- **Milestone:** Sprint 3
- **Description:**
```
Core Requirement Screen #9 (50 pts).

GET /reporting — report dashboard with 4 report types
GET /reporting/export/<type>?format=csv|json — downloadable exports

Reports:
1. Spend by Category — annual breakdown with amounts and percentages
2. Card Value Comparison — estimated value for all cards based on user data
3. Plan History — all commits/removals with dates
4. Recommendation History — all rec runs with top results

**Acceptance Criteria:**
- [ ] 4 report types visible on page
- [ ] CSV export downloads valid CSV with correct headers
- [ ] JSON export downloads valid JSON
- [ ] Empty data → empty report, no crash
```

### Issue #32: Admin — View all users (20 pts)
- **Labels:** `sprint-3`, `admin`, `feature`, `priority-high`
- **Assignee:** Person E
- **Milestone:** Sprint 3
- **Description:**
```
Core Requirement Administrative Functionality (20 pts).

GET /admin/users — list all registered users:
- Table columns: ID, Email, Display Name, Role, Status (Active/Disabled), Created, Last Login, # Transactions, # Rec Runs
- Search box to filter by email or name
- Sortable columns
- Admin-only access (403 for non-admin)

**Acceptance Criteria:**
- [ ] All users listed with correct stats
- [ ] Search filter works
- [ ] Non-admin user → 403
```

### Issue #33: Admin — Disable user accounts (20 pts)
- **Labels:** `sprint-3`, `admin`, `feature`, `priority-high`
- **Assignee:** Person E
- **Milestone:** Sprint 3
- **Description:**
```
Core Requirement Administrative Functionality (20 pts).

POST /admin/users/<id>/toggle — toggle user is_active status:
- Disabled users cannot log in
- Log SystemEvent: type='admin_disable_user' or 'admin_enable_user'
- Flash confirmation message

**Acceptance Criteria:**
- [ ] Toggle changes is_active in DB
- [ ] Disabled user cannot log in
- [ ] SystemEvent logged
- [ ] Non-admin → 403
```

### Issue #34: Admin — Reset user passwords (20 pts)
- **Labels:** `sprint-3`, `admin`, `feature`, `priority-high`
- **Assignee:** Person E
- **Milestone:** Sprint 3
- **Description:**
```
Core Requirement Administrative Functionality (20 pts).

POST /admin/users/<id>/reset-password:
- Generate random 12-character temporary password
- Hash and store the new password
- Log SystemEvent: type='admin_reset_password'
- Display temporary password ONCE to admin

**Acceptance Criteria:**
- [ ] New password generated and hashed
- [ ] Temporary password displayed to admin
- [ ] SystemEvent logged
- [ ] Non-admin → 403
```

### Issue #35: Admin — View system transactions (20 pts)
- **Labels:** `sprint-3`, `admin`, `feature`, `priority-high`
- **Assignee:** Person E
- **Milestone:** Sprint 3
- **Description:**
```
Core Requirement Administrative Functionality (20 pts).

GET /admin/events — global event ledger showing ALL users' SystemEvents:
- Same layout as user History but includes events from all users
- Additional column: User (email)
- Filters: date range, event type, user dropdown
- Admin-only access

**Acceptance Criteria:**
- [ ] Shows events from all users
- [ ] User column displays correctly
- [ ] Filters work including user filter
- [ ] Non-admin → 403
```

### Issue #36: Admin — Cross-account analysis (20 pts)
- **Labels:** `sprint-3`, `admin`, `feature`, `priority-high`
- **Assignee:** Person E
- **Milestone:** Sprint 3
- **Description:**
```
Core Requirement Administrative Functionality (20 pts).

GET /admin/analytics — system-wide analytics dashboard:
1. Top Spend Categories across all users (aggregated bar chart)
2. Most Recommended Cards (ranked list or bar chart)
3. User Activity Stats: total users, active users (last 30 days), total transactions, total rec runs
4. Error/Failure Rates (optional)

**Acceptance Criteria:**
- [ ] All analytics sections display correctly
- [ ] Charts render with real aggregated data
- [ ] Non-admin → 403
```

### Issue #37: Sprint 3 tests + paper prototypes + status report
- **Labels:** `sprint-3`, `docs`, `test`, `priority-medium`
- **Assignee:** All
- **Milestone:** Sprint 3
- **Description:**
```
- tests/test_plan.py — commit, remove, atomic rollback
- tests/test_history.py — display, filter, pagination
- tests/test_reporting.py — CSV export, JSON export
- tests/test_admin.py — all 5 admin functions + role checks
- Paper prototypes for Screens #7, #8, #9, Admin Console
- Sprint 3 Status Report (all 6 sections)
```

---

## Sprint 4 Issues — Deploy & Polish

### Issue #38: Migrate to PostgreSQL (50 pts)
- **Labels:** `sprint-4`, `infra`, `priority-high`
- **Assignee:** Person E
- **Milestone:** Sprint 4
- **Description:**
```
Switch from SQLite to PostgreSQL for production deployment.
- Install PostgreSQL on VCM
- Create database and user
- Update DATABASE_URL in .env
- Run migrations and seed data
- Verify all functionality works on PostgreSQL

**Acceptance Criteria:**
- [ ] PostgreSQL running on VCM
- [ ] All migrations applied successfully
- [ ] App functions identically to SQLite version
```

### Issue #39: Deploy to Duke VCM (25 pts)
- **Labels:** `sprint-4`, `infra`, `priority-high`
- **Assignee:** Person E
- **Milestone:** Sprint 4
- **Description:**
```
Set up production deployment on Duke VCM:
- Clone repo, create virtualenv, install dependencies
- Configure Gunicorn as WSGI server
- Configure Nginx as reverse proxy
- Set up .env with production secrets

**Acceptance Criteria:**
- [ ] App accessible at https://vcmXXX.vm.duke.edu
- [ ] Gunicorn serving the Flask app
- [ ] Nginx reverse proxy configured
```

### Issue #40: Configure auto-start on VCM reboot (25 pts)
- **Labels:** `sprint-4`, `infra`, `priority-high`
- **Assignee:** Person E
- **Milestone:** Sprint 4
- **Description:**
```
Create systemd service for automatic startup:
- App starts automatically when VM reboots
- Test by rebooting VCM and verifying the site comes back up

**Acceptance Criteria:**
- [ ] systemd service file created and enabled
- [ ] After reboot, site is accessible without manual intervention
```

### Issue #41: Set up GitLab CI/CD pipeline (40 pts)
- **Labels:** `sprint-4`, `infra`, `priority-medium`
- **Assignee:** Person E
- **Milestone:** Sprint 4
- **Description:**
```
Create .gitlab-ci.yml with 4 stages:
1. Build: install dependencies (10 pts)
2. Test: run pytest suite (10 pts)
3. SAST: run GitLab SAST tooling (10 pts)
4. Deploy: auto-deploy to VCM on main branch (10 pts)

**Acceptance Criteria:**
- [ ] Pipeline runs on every commit
- [ ] Build stage installs all dependencies
- [ ] Test stage runs and reports pytest results
- [ ] SAST stage completes
- [ ] Deploy stage updates VCM on main branch pushes
```

### Issue #42: Security analysis — DFD + STRIDE (15 pts)
- **Labels:** `sprint-4`, `docs`, `priority-medium`
- **Assignee:** Person A
- **Milestone:** Sprint 4
- **Description:**
```
Create docs/security/threat_model.md:
1. Data Flow Diagram (DFD) for CardSmart system
2. STRIDE analysis for each DFD element:
   - Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege

**Acceptance Criteria:**
- [ ] DFD covers all system components
- [ ] STRIDE analysis completed for each element
- [ ] Mitigations documented
```

### Issue #43: Security analysis — Semgrep + OWASP ZAP (10 pts)
- **Labels:** `sprint-4`, `infra`, `priority-low`
- **Assignee:** Person E
- **Milestone:** Sprint 4
- **Description:**
```
Run SAST and DAST scans:
1. Semgrep: run against codebase, save report (5 pts)
2. OWASP ZAP: run baseline scan against deployed site, save report (5 pts)
Fix any critical findings.

**Acceptance Criteria:**
- [ ] Semgrep report generated in docs/security/
- [ ] ZAP report generated in docs/security/
- [ ] Critical findings addressed
```

### Issue #44: Containerization — Dockerfile + docker-compose (25 pts)
- **Labels:** `sprint-4`, `infra`, `priority-medium`
- **Assignee:** Person E
- **Milestone:** Sprint 4
- **Description:**
```
1. Create Dockerfile to build the app image (15 pts)
2. Create docker-compose.yml with app + PostgreSQL services (10 pts)
   - Volume for database persistence

**Acceptance Criteria:**
- [ ] docker build succeeds
- [ ] docker-compose up starts app + DB
- [ ] App accessible at localhost:8000
```

### Issue #45: System architecture C4 diagrams (20 pts)
- **Labels:** `sprint-4`, `docs`, `priority-medium`
- **Assignee:** Person C
- **Milestone:** Sprint 4
- **Description:**
```
Create C4 model diagrams in docs/architecture/:
1. System Context diagram (5 pts)
2. Container diagram (5 pts)
3. Component diagram (5 pts)
4. Code diagram (5 pts)

**Acceptance Criteria:**
- [ ] All 4 diagrams created
- [ ] Diagrams accurately reflect the system
```

### Issue #46: UI/UX polish and final testing
- **Labels:** `sprint-4`, `ui`, `priority-medium`
- **Assignee:** Person D
- **Milestone:** Sprint 4
- **Description:**
```
Final polish pass:
- Consistent styling across all pages (Bootstrap theme)
- Flash messages styled as alerts (green/red/yellow)
- Loading spinners for AJAX requests
- Empty state messages on every page
- Custom 404 and 500 error pages
- Test coverage > 70% on services and routes

**Acceptance Criteria:**
- [ ] All pages have consistent styling
- [ ] Error pages exist for 404 and 500
- [ ] pytest coverage report generated
```

### Issue #47: Sprint 4 status report + final documentation
- **Labels:** `sprint-4`, `docs`, `priority-high`
- **Assignee:** All
- **Milestone:** Sprint 4
- **Description:**
```
Final deliverables:
- Sprint 4 Status Report (all 6 sections)
- README.md updated with: project overview, setup instructions, team members, tech stack
- All docs organized in docs/ directory
- Final UML class diagram updated

**Acceptance Criteria:**
- [ ] Status report complete
- [ ] README has setup instructions that a TA can follow
- [ ] All documentation committed to GitLab
```

---

## Summary — Issue Count by Sprint

| Sprint | Issues | Core Points Targeted |
|--------|--------|----------------------|
| Sprint 0 | #1 – #6 (6 issues) | 0 (foundation) |
| Sprint 1 | #7 – #18 (12 issues) | 60 (UI) + 50 (Data Integration) = 110 |
| Sprint 2 | #19 – #28 (10 issues) | 100 (UI) + 75 (Charts) = 175 |
| Sprint 3 | #29 – #37 (9 issues) | 140 (UI) + 100 (Admin) = 240 |
| Sprint 4 | #38 – #47 (10 issues) | 50 (Infra) + 50 (DB) + extras = 210 |
| **Total** | **47 issues** | **735 pts** |
