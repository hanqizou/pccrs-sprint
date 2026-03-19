# Sprint 1 — Authentication, Data Ingestion & Card Catalog

> **Goal**: Users can register, log in, upload transactions, and admin can manage the card catalog.
> **Core Req points targeted**: UI #1–#3 (60 pts) + Data Integration (50 pts) + partial Admin
> **Prerequisites**: Sprint 0 completed. Read `MASTER.md` for schema and conventions.

---

## Context

Read `prompts/MASTER.md` for the full schema, conventions, and project structure. Sprint 0 should already have the skeleton in place — this sprint fills in the real functionality for authentication and data ingestion.

---

## Tasks

### Task 1.1 — Home Page for Unauthenticated Users (Screen #1, 10 pts)

**Route**: `GET /`

**Requirements**:
- If user is NOT logged in: show marketing/intro page
  - Hero section: "CardSmart — 让你的消费数据帮你选卡" / "Turn your spending into an optimized card strategy"
  - Brief feature list (3 key benefits)
  - CTA buttons: "Get Started" → Register, "Log In" → Login
- If user IS logged in: redirect to `/dashboard`
- Must be visually **distinct** from the authenticated dashboard (Core Req: "must be distinct from Home page")

**Test cases**:
- GET / while not logged in → 200, contains "Get Started"
- GET / while logged in → 302 redirect to /dashboard

### Task 1.2 — Registration Page (Screen #2, 25 pts)

**Route**: `GET/POST /auth/register`

**Requirements**:
- Form fields: email, password, confirm_password, display_name
- Validation:
  - Email format validation (use WTForms EmailValidator)
  - Password minimum 8 characters
  - Passwords must match
  - Duplicate email → "Email already in use" error
- On success: create User, hash password, log them in, redirect to /dashboard
- Log a SystemEvent: type='user_register'
- CSRF protection via Flask-WTF

**Test cases**:
- Valid registration → 302 to /dashboard, user exists in DB
- Duplicate email → 200, error message displayed
- Invalid email format → 200, error message
- Passwords don't match → 200, error message
- Password too short → 200, error message

### Task 1.3 — Login Page (Screen #3, 25 pts)

**Route**: `GET/POST /auth/login`

**Requirements**:
- Form fields: email, password
- On valid credentials: log in via Flask-Login, redirect to /dashboard
- On invalid: generic "Invalid email or password" (don't reveal which is wrong — security best practice)
- Add logout route: `GET /auth/logout` → log out, redirect to /
- Update `User.last_login` timestamp on successful login

**Test cases**:
- Valid login → 302 to /dashboard
- Wrong password → 200, "Invalid email or password"
- Non-existent email → 200, "Invalid email or password" (same message!)
- Logout → 302 to /, session cleared

### Task 1.4 — Data Ingestion: File Upload (Screen part of Dashboard, 50 pts target)

**Route**: `GET /ingestion` (upload form), `POST /ingestion/upload` (process file)

**Requirements**:

**CSV Upload (Format A):**
- Accept `.csv` file with columns: `date, merchant, amount, category`
- Parse with Python `csv` module or `pandas`
- Validate:
  - Required columns exist
  - `date` is parseable
  - `amount` is numeric and > 0
  - `category` is one of known categories (or map to 'other')
- On missing columns → reject with "Missing columns: [list]"

**JSON Upload (Format B):**
- Accept `.json` file with structure:
```json
{
  "transactions": [
    {"date": "2025-09-01", "description": "...", "amount_cents": 1450, "mcc_code": "5812"}
  ]
}
```
- Map `mcc_code` → category using a lookup dictionary in `services/category_mapper.py`
- `amount_cents` → convert to dollars (divide by 100)

**Idempotency:**
- Compute SHA256 hash of file content → `import_id`
- If `import_id` already exists for this user → reject with "This file has already been imported"

**Post-import:**
- Store all transactions in the Transaction table
- Create SystemEvent: type='import', summary="Imported N transactions from [filename]"
- Flash success message: "Successfully imported {N} transactions"
- Redirect to /dashboard or /analysis/current

**Test cases**:
- Valid CSV upload → transactions appear in DB, SystemEvent logged
- Valid JSON upload → same
- Missing required columns → 400/200 with error message
- Duplicate file upload → rejected with "already imported"
- Empty file → rejected with "No transactions found"
- Invalid amount (negative, non-numeric) → rejected with specific error

### Task 1.5 — Data Ingestion: REST API Integration

**Route**: `POST /ingestion/fx-sync`

**Requirements**:
- Call ExchangeRate API: `GET https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD`
- Store latest rates in a cache (DB table or in-memory dict with timestamp)
- On file import, if `original_currency != 'USD'`, convert using cached FX rate
- Display "Last FX update: {timestamp}" on the ingestion page
- Handle API errors gracefully: if API is down, use last cached rates; if no cache exists, warn user

**Service**: `app/services/fx_service.py`
```python
class FXService:
    def get_rate(self, currency: str) -> float:
        """Return USD exchange rate for given currency. Use cache if fresh."""
        ...
    def sync_rates(self) -> dict:
        """Fetch latest rates from API. Return rates dict."""
        ...
```

**Test cases**:
- Mock API response → rates stored correctly
- API down + cache exists → use cached rates
- API down + no cache → return error message
- Convert EUR transaction → amount_usd = amount_eur * rate

### Task 1.6 — Card Catalog Admin (partial Admin functionality)

**Route**: `GET /admin/cards` (list), `GET/POST /admin/cards/new` (create), `GET/POST /admin/cards/<id>/edit` (edit)

**Requirements**:
- Only accessible to admin users (`@login_required` + role check)
- List all cards in catalog with: name, issuer, annual fee, # of bonus categories
- Create new card form: all fields from Card model
- Edit existing card: pre-filled form, update on submit
- Validate: multiplier >= 0, annual_fee >= 0, card_id unique
- Log SystemEvent on create/update: type='admin_update_card'

**Test cases**:
- Normal user accessing /admin/cards → 403 Forbidden
- Admin creates card → card appears in DB
- Admin edits card → changes persisted
- Invalid multiplier (negative) → rejected with error

### Task 1.7 — Dashboard Stub (Screen #4 minimal, 50 pts — fully built in Sprint 2)

**Route**: `GET /dashboard`

**Requirements** (minimal for Sprint 1, expanded in Sprint 2):
- Require authentication (`@login_required`)
- Show: welcome message with user's name
- Show: quick stats if data exists (total transactions imported, date range, top 3 categories by spend)
- Show: "No data yet — upload your transactions to get started!" if no transactions
- Links to: Import Data, Run Recommendation, View History

---

## Definition of Done (Sprint 1)

- [ ] Users can register, log in, and log out
- [ ] Passwords are hashed, never stored in plaintext
- [ ] CSV upload works: parses, validates, stores transactions
- [ ] JSON upload works: parses, validates, maps MCC → category, stores transactions
- [ ] Duplicate file detection works (idempotent import)
- [ ] FX API integration works (fetches rates, converts currencies)
- [ ] Admin can create/edit cards in the catalog
- [ ] Non-admin users cannot access admin routes
- [ ] SystemEvent records created for imports and admin actions
- [ ] All test cases pass
- [ ] Code committed to GitLab
