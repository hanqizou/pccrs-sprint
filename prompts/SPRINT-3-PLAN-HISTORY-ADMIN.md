# Sprint 3 — Buy/Sell, History, Reporting & Admin Console

> **Goal**: Complete the remaining required screens + full admin functionality.
> **Core Req points targeted**: UI #7 Buy/Sell (50 pts) + #8 History (40 pts) + #9 Reporting (50 pts) + Admin (100 pts)
> **Prerequisites**: Sprint 2 completed (recommendations working). Read `MASTER.md`.

---

## Context

Read `prompts/MASTER.md` for schema and conventions. At this point users can register, upload data, and get recommendations. This sprint adds the transactional layer (commit/remove plans), history tracking, reporting, and the complete admin console.

---

## Tasks

### Task 3.1 — Buy/Sell: Commit/Remove Plan (Screen #7, 50 pts)

This is the "transaction" screen — users "buy" (commit to a card plan) or "sell" (remove a card).

**Routes**:
- `POST /plan/commit` — save a card plan (Buy action)
- `POST /plan/remove` — remove a card from plan (Sell action)
- `GET /plan/current` — view current committed plan

**Commit Plan (Buy):**
```
POST /plan/commit
Body: { "rec_run_id": "...", "card_ids": ["chase-sapphire-preferred", "amex-gold"] }
```
1. Validate that rec_run_id belongs to current user
2. Create PlanCommit record: action='commit', card_ids=[...]
3. Create SystemEvent: type='plan_commit', summary="Committed plan: CSP + Amex Gold"
4. Show confirmation page with:
   - Cards in the plan
   - Combined estimated annual value
   - "Your plan has been saved!" success message
5. Transaction must be atomic — if DB write fails, no partial state

**Remove Plan (Sell):**
```
POST /plan/remove
Body: { "card_id": "chase-sapphire-preferred", "reason": "Found a better option" }
```
1. Create PlanCommit record: action='remove', card_ids=["chase-sapphire-preferred"]
2. Create SystemEvent: type='plan_remove'
3. Flash message: "Removed Chase Sapphire Preferred from your plan"

**Current Plan View:**
- Show all currently committed cards (latest commit minus removals)
- For each card: name, annual fee, estimated value
- Action: "Remove" button per card
- Action: "Run New Recommendation" to compare current plan vs. optimal

**Test cases**:
- Commit plan → PlanCommit record in DB, SystemEvent logged
- Remove card → PlanCommit with action='remove', SystemEvent logged
- Commit with invalid rec_run_id → 400 error
- DB failure simulation → no partial state (transaction rolled back)
- Commit → view current plan → cards appear

### Task 3.2 — History Screen (Screen #8, 40 pts)

**Route**: `GET /history`

**Requirements**:
- Query SystemEvent table for current user, ordered by created_at DESC
- Display as a filterable table:

| Column | Content |
|--------|---------|
| Date/Time | formatted timestamp |
| Type | Import / Recommendation / Plan Commit / Plan Remove |
| Summary | e.g., "Imported 214 transactions from statement.csv" |
| Status | Success / Failed (color-coded) |
| Details | Expandable or click-to-view |

**Filters** (form at top):
- Date range: start date — end date (date pickers)
- Event type: dropdown (All / Import / Recommendation / Plan Commit / Plan Remove)
- Search: text search across summary field

**Detail view** (when user clicks a row):
- Full details JSON displayed in readable format
- If type='rec_run': link to recommendation results
- If type='import': show transaction count + date range imported
- If type='plan_commit': show cards committed

**Pagination**: if > 20 events, paginate (20 per page)

**Test cases**:
- User with 5 events → all 5 displayed
- Filter by type='import' → only import events shown
- Filter by date range → only matching events shown
- Empty history → "No activity yet" message
- Pagination: 25 events → page 1 shows 20, page 2 shows 5

### Task 3.3 — Reporting Functionality (Screen #9, 50 pts)

**Route**: `GET /reporting`, `GET /reporting/export/<report_type>`

**Requirements**:

**Report Dashboard** (`GET /reporting`):
- Show available reports as cards:
  1. **Spend by Category** — annual breakdown with amounts and percentages
  2. **Card Value Comparison** — estimated value for all cards based on user's data
  3. **Plan History** — all commits/removals with dates
  4. **Recommendation History** — all rec runs with top results
- Each report card has: preview (small table/chart) + "Export CSV" + "Export JSON" buttons

**Export endpoints**:
```
GET /reporting/export/spend-by-category?format=csv
GET /reporting/export/spend-by-category?format=json
GET /reporting/export/card-value?format=csv
GET /reporting/export/plan-history?format=csv
GET /reporting/export/recommendation-history?format=json
```

**Service**: `app/services/export_service.py`
```python
class ExportService:
    def spend_by_category(self, user_id) -> list[dict]:
        """Return [{category, amount, pct, avg_monthly}, ...]"""
    def card_value_comparison(self, user_id) -> list[dict]:
        """Return [{card_name, net_value, annual_fee, top_driver}, ...]"""
    def plan_history(self, user_id) -> list[dict]:
        """Return [{date, action, cards, rec_run_id}, ...]"""
    def to_csv(self, data, filename) -> Response:
        """Return Flask Response with CSV download headers"""
    def to_json(self, data, filename) -> Response:
        """Return Flask Response with JSON download headers"""
```

**CSV format** — set `Content-Type: text/csv` and `Content-Disposition: attachment; filename="report.csv"`

**Test cases**:
- Export spend-by-category CSV → valid CSV content, correct headers
- Export card-value JSON → valid JSON, contains expected fields
- User with no data → empty report (not crash)
- Report page shows all 4 report types

### Task 3.4 — Admin Console: User Management (60 pts: 20 each for view/disable/reset)

**Routes**:
- `GET /admin/users` — list all users
- `POST /admin/users/<id>/toggle` — enable/disable user
- `POST /admin/users/<id>/reset-password` — reset user's password

**All admin routes must check**: `current_user.is_authenticated and current_user.role == 'admin'`
If not admin → return 403.

**View All Users** (`GET /admin/users`):
- Table with columns: ID, Email, Display Name, Role, Status (Active/Disabled), Created, Last Login, # Transactions, # Rec Runs
- Search box: filter by email/name
- Sort by any column

**Disable User** (`POST /admin/users/<id>/toggle`):
- Toggle `user.is_active`
- Disabled users cannot log in (check in login route)
- Log SystemEvent: type='admin_disable_user' or 'admin_enable_user'
- Flash: "User {email} has been disabled/enabled"

**Reset Password** (`POST /admin/users/<id>/reset-password`):
- Generate random temporary password (12 chars, alphanumeric)
- Set `user.password_hash` to hash of temp password
- Log SystemEvent: type='admin_reset_password'
- Display temp password ONCE to admin: "Temporary password for {email}: {temp_pw}"
- Flash warning: "User must change password on next login" (note: actual forced password change is optional)

### Task 3.5 — Admin Console: System Transactions (20 pts)

**Route**: `GET /admin/events`

**Requirements**:
- Same layout as user History but shows ALL users' events
- Additional column: User (email)
- Filters: all the same as user history + user filter dropdown
- Admin can see events from any user + admin-specific events

### Task 3.6 — Admin Console: Cross-Account Analysis (20 pts)

**Route**: `GET /admin/analytics`

**Requirements**:
Display system-wide analytics:

1. **Top Spend Categories** (across all users):
   - Aggregated bar chart: which categories have the most total spend
2. **Most Recommended Cards**:
   - Which cards appear most often in top-3 recommendations across all users
   - Display as ranked list or bar chart
3. **User Activity Stats**:
   - Total registered users
   - Active users (logged in within last 30 days)
   - Total transactions imported
   - Total recommendation runs
4. **Error/Failure Rates** (optional):
   - Count of failed imports, failed rec runs

This can reuse the Plotly charts with different data.

---

## Definition of Done (Sprint 3)

- [ ] Users can commit a plan (Buy) and remove cards (Sell)
- [ ] Transactions are atomic (no partial state on failure)
- [ ] History screen shows all events with filters and pagination
- [ ] Reporting page offers 4 report types with CSV and JSON export
- [ ] Admin can view all users
- [ ] Admin can disable/enable user accounts
- [ ] Admin can reset user passwords
- [ ] Admin can view system-wide transactions
- [ ] Admin can view cross-account analytics
- [ ] Non-admin users get 403 on all admin routes
- [ ] All SystemEvents are properly logged
- [ ] All tests pass
- [ ] Code committed to GitLab
