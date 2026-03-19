# CardSmart — AI Coding Master Prompt

> This file defines the project-wide context, architecture, conventions, and database schema.
> Every sprint prompt imports this file as foundational context.
> 适用于任何 AI coding agent (Codex, Claude Code, Cursor, Copilot, etc.)

---

## Project Overview

**CardSmart** is a personalized credit card recommendation system for a FinTech 512 course project at Duke University. It helps users maximize rewards based on their real spending behavior and goals.

**Core idea:** Users upload transaction data → system categorizes spend → computes expected annual value for each credit card → recommends the best 1–3 cards with explainable reasoning and interactive sensitivity analysis.

This is NOT a real financial product. All "buy/sell" actions are simulated internal transactions (saving/removing a card plan). No real money, no real credit applications.

---

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Backend | **Python 3.11+ / Flask** | Course standard. Use Blueprints for modular routes. |
| Frontend | **Vanilla HTML/CSS/JS** | Jinja2 templates. No React. Use Bootstrap 5 for responsive layout. |
| Database | **PostgreSQL** (prod) / **SQLite** (local dev) | Use SQLAlchemy ORM. 50 pts for PostgreSQL. |
| Charting | **Plotly.js** | Course recommends Plotly. 3 chart types + 1 custom interaction. |
| API Integration | **REST/JSON** | At least one external API (e.g., ExchangeRate-API for FX). |
| Hosting | **Duke VCM** | Ubuntu VM, auto-start on reboot via systemd. |
| Version Control | **GitLab** | Course uses GitLab, not GitHub. |
| Testing | **pytest** | Unit + integration tests. |

---

## Project File Structure

```
cardsmart/
├── app/
│   ├── __init__.py              # Flask app factory, register blueprints
│   ├── config.py                # Config classes (Dev, Prod, Test)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py              # User model (normal + admin)
│   │   ├── transaction.py       # Imported transaction records
│   │   ├── card.py              # Credit card catalog definitions
│   │   ├── recommendation.py    # Recommendation run results
│   │   ├── plan.py              # Committed plans (buy/sell events)
│   │   └── system_event.py      # History / audit log entries
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # Register, login, logout
│   │   ├── dashboard.py         # Authenticated home / dashboard
│   │   ├── ingestion.py         # File upload + API sync
│   │   ├── analysis.py          # Analysis pages (informed decision + current data)
│   │   ├── plan.py              # Buy/sell (commit/remove plan)
│   │   ├── history.py           # History screen
│   │   ├── reporting.py         # Reports + export
│   │   └── admin.py             # Admin console
│   ├── services/
│   │   ├── __init__.py
│   │   ├── recommendation_engine.py  # Core calculation logic
│   │   ├── category_mapper.py        # MCC / description → category
│   │   ├── fx_service.py             # External FX API client
│   │   └── export_service.py         # CSV/JSON export generation
│   ├── templates/
│   │   ├── base.html            # Base layout (nav, footer)
│   │   ├── home.html            # Unauthenticated home (#1)
│   │   ├── auth/
│   │   │   ├── register.html    # Registration (#2)
│   │   │   └── login.html       # Login (#3)
│   │   ├── dashboard.html       # Authenticated dashboard (#4)
│   │   ├── analysis/
│   │   │   ├── decision.html    # Informed decision (#5)
│   │   │   └── current.html     # Current data (#6)
│   │   ├── plan/
│   │   │   └── commit.html      # Buy/sell confirmation (#7)
│   │   ├── history.html         # History (#8)
│   │   ├── reporting.html       # Reports (#9)
│   │   └── admin/
│   │       ├── users.html       # Admin: user list
│   │       ├── events.html      # Admin: system transactions
│   │       └── analytics.html   # Admin: cross-account analysis
│   └── static/
│       ├── css/
│       │   └── style.css        # Custom styles (supplement Bootstrap)
│       ├── js/
│       │   ├── charts.js        # Plotly chart rendering
│       │   ├── slider.js        # CPP slider interaction
│       │   └── main.js          # Common JS utilities
│       └── data/
│           └── demo_transactions.csv  # Bundled demo dataset
├── migrations/                  # Flask-Migrate / Alembic
├── tests/
│   ├── conftest.py              # Fixtures (test client, test DB, seed data)
│   ├── test_auth.py
│   ├── test_ingestion.py
│   ├── test_recommendation.py
│   ├── test_plan.py
│   ├── test_history.py
│   ├── test_reporting.py
│   └── test_admin.py
├── seed_data/
│   ├── cards.json               # Initial card catalog (10-15 popular cards)
│   ├── demo_transactions.csv    # Demo user spend data
│   └── demo_transactions.json   # Same data, JSON format (2nd file structure)
├── docs/
│   ├── proposal.md
│   └── prototypes/
├── requirements.txt
├── .env.example                 # Template for env vars (never commit .env)
├── .gitignore
├── run.py                       # Entry point: python run.py
├── Dockerfile                   # (Sprint 4 optional)
├── docker-compose.yml           # (Sprint 4 optional)
├── .gitlab-ci.yml               # (Sprint 4 optional)
└── README.md
```

---

## Database Schema (SQLAlchemy Models)

### User
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    display_name = db.Column(db.String(100))
    role = db.Column(db.String(20), default='normal')  # 'normal' | 'admin'
    is_active = db.Column(db.Boolean, default=True)
    preference_mode = db.Column(db.String(20), default='travel')  # 'travel' | 'cashback'
    preferred_partners = db.Column(db.JSON, default=list)  # e.g., ["hyatt", "united"]
    fee_tolerance = db.Column(db.Integer, default=550)  # max annual fee willing to pay
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
```

### Transaction (imported spend data)
```python
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    import_id = db.Column(db.String(64), nullable=False)  # hash of source file/API call
    date = db.Column(db.Date, nullable=False)
    merchant = db.Column(db.String(255))
    amount = db.Column(db.Float, nullable=False)  # in USD
    original_amount = db.Column(db.Float)  # before FX conversion
    original_currency = db.Column(db.String(3), default='USD')
    category = db.Column(db.String(50), nullable=False)  # e.g., 'dining', 'travel', 'groceries'
    mcc_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Card (credit card catalog)
```python
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.String(50), unique=True, nullable=False)  # e.g., 'chase-sapphire-preferred'
    name = db.Column(db.String(100), nullable=False)
    issuer = db.Column(db.String(50))  # e.g., 'Chase', 'Amex'
    annual_fee = db.Column(db.Float, default=0)
    base_reward_rate = db.Column(db.Float, default=1.0)  # base points per dollar
    category_multipliers = db.Column(db.JSON, default=dict)
    # e.g., {"dining": 4, "travel": 3, "groceries": 1, "gas": 1}
    credits = db.Column(db.JSON, default=dict)
    # e.g., {"travel": 300, "dining": 120, "streaming": 60}
    credit_utilization_rate = db.Column(db.Float, default=0.8)  # conservative assumption
    transfer_partners = db.Column(db.JSON, default=dict)
    # e.g., {"hyatt": {"ratio": 1.0, "cpp": 2.0}, "united": {"ratio": 1.0, "cpp": 1.5}}
    category_caps = db.Column(db.JSON, default=dict)
    # e.g., {"dining": {"max_annual": 25000}} — cap on bonus category
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
```

### RecommendationRun
```python
class RecommendationRun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    run_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid4()))
    preferences_snapshot = db.Column(db.JSON)  # preferences at time of run
    results = db.Column(db.JSON)
    # e.g., [{"card_id": "...", "estimated_value": 920, "drivers": [...], "rank": 1}, ...]
    top_card_id = db.Column(db.String(50))
    total_estimated_value = db.Column(db.Float)
    cpp_assumption = db.Column(db.Float, default=1.5)  # cents-per-point used
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### PlanCommit (buy/sell transaction)
```python
class PlanCommit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    txn_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid4()))
    rec_run_id = db.Column(db.String(36), db.ForeignKey('recommendation_run.run_id'))
    action = db.Column(db.String(10), nullable=False)  # 'commit' (buy) | 'remove' (sell)
    card_ids = db.Column(db.JSON, nullable=False)  # list of card_ids in plan
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### SystemEvent (history / audit log)
```python
class SystemEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_type = db.Column(db.String(30), nullable=False)
    # Types: 'import', 'rec_run', 'plan_commit', 'plan_remove',
    #        'admin_disable_user', 'admin_reset_password', 'admin_update_card'
    summary = db.Column(db.String(500))
    details = db.Column(db.JSON)
    status = db.Column(db.String(10), default='success')  # 'success' | 'failed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## Coding Conventions

1. **Flask Blueprints**: every route module registers as a Blueprint. Import and register in `app/__init__.py`.
2. **Environment variables**: store secrets (DB URL, API keys) in `.env`. Load with `python-dotenv`. Never commit `.env`.
3. **Password hashing**: use `werkzeug.security.generate_password_hash` / `check_password_hash`.
4. **Session auth**: use Flask-Login for session management. `@login_required` decorator on protected routes.
5. **Form validation**: use WTForms with CSRF protection.
6. **Error handling**: every route should handle errors gracefully; return user-friendly messages, never raw tracebacks.
7. **Atomic transactions**: use `db.session` context; rollback on failure. Never leave partial state.
8. **Idempotent imports**: hash the uploaded file content → `import_id`. If `import_id` already exists for this user, reject with "Already imported" message.
9. **Testing**: each module has a corresponding `test_*.py`. Use pytest fixtures for test client and seeded DB.
10. **No hardcoded card rules**: all card data lives in the `Card` table. The recommendation engine reads from DB, not from code constants.

---

## The 9 Required Screens (Core Requirements, 300 pts)

| # | Screen | Route | Template | Points |
|---|--------|-------|----------|--------|
| 1 | Home (unauthenticated) | `GET /` | `home.html` | 10 |
| 2 | Register | `GET/POST /auth/register` | `auth/register.html` | 25 |
| 3 | Login | `GET/POST /auth/login` | `auth/login.html` | 25 |
| 4 | Dashboard (authenticated) | `GET /dashboard` | `dashboard.html` | 50 |
| 5 | Analysis: Informed Decision | `GET /analysis/decision` | `analysis/decision.html` | 25 |
| 6 | Analysis: Current Data | `GET /analysis/current` | `analysis/current.html` | 25 |
| 7 | Buy/Sell (Commit Plan) | `POST /plan/commit`, `POST /plan/remove` | `plan/commit.html` | 50 |
| 8 | History | `GET /history` | `history.html` | 40 |
| 9 | Reporting | `GET /reporting` | `reporting.html` | 50 |

---

## Recommendation Engine Logic (Core Algorithm)

```
For each card C in catalog:
    annual_value = 0
    For each category K in user's spend:
        multiplier = C.category_multipliers.get(K, C.base_reward_rate)
        category_spend = sum of user transactions in K over 12 months
        # Apply cap if exists
        if K in C.category_caps:
            category_spend = min(category_spend, C.category_caps[K]['max_annual'])
        points_earned = category_spend * multiplier

        # Value depends on redemption mode
        if user.preference_mode == 'travel' and C.transfer_partners:
            best_partner = max cpp among preferred partners
            value = points_earned * best_partner.cpp / 100
        else:
            value = points_earned * default_cpp / 100

        annual_value += value

    # Add credits (with utilization assumption)
    for credit_name, credit_amount in C.credits.items():
        annual_value += credit_amount * C.credit_utilization_rate

    # Subtract annual fee
    net_value = annual_value - C.annual_fee

    # Store: card_id, net_value, drivers (top contributing categories)

Sort by net_value descending → return top 3
```

---

## External API Integration

### ExchangeRate API (FX Rates)

- **Endpoint**: `GET https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD`
- **Purpose**: normalize foreign-currency transactions to USD
- **Response**: JSON with `conversion_rates` object
- **Usage**: on file import, if `original_currency != 'USD'`, multiply by FX rate
- **Fallback**: if API is down, use last-cached rates or reject foreign transactions with warning

This satisfies: "integrate data from at least one source using REST/JSON web API" (50 pts).

---

## Seed Data Requirements

### Card Catalog (seed_data/cards.json)
Include 10–15 popular cards with real-world-inspired data:
- Chase Sapphire Preferred, Chase Sapphire Reserve
- Amex Gold, Amex Platinum
- Citi Double Cash, Citi Premier
- Capital One Venture X
- Chase Freedom Unlimited, Chase Freedom Flex
- US Bank Altitude Go
- Wells Fargo Autograph

### Demo Transactions (seed_data/demo_transactions.csv + .json)
Generate ~200 synthetic transactions over 6 months:
- Categories: dining, groceries, travel, gas, online_shopping, entertainment, utilities, other
- Realistic distribution: dining 25%, groceries 20%, travel 15%, online 15%, etc.
- Monthly total: ~$3,000–$5,000

---

## Important Course-Specific Notes

1. **Duke VCM deployment**: the app must run on `https://vcmXXX.vm.duke.edu` and auto-start on reboot.
2. **No real PII**: use synthetic data. Do not ask users for bank credentials.
3. **Paper prototypes first**: each screen needs a paper prototype reviewed by TA before implementation.
4. **Test cases per screen**: each screen needs documented test cases (5 pts each).
5. **API keys in env vars**: never commit API keys to GitLab. Use `.env` + `.gitignore`.
6. **PostgreSQL for full marks**: SQLite gets 25 pts, PostgreSQL gets 50 pts.
