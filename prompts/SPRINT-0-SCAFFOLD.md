# Sprint 0 — Project Scaffolding & Foundation

> **Goal**: Set up the project skeleton so every team member can `git clone`, install deps, and run locally.
> **Estimated effort**: 1 session (~2–3 hours of vibe coding)
> **Prerequisites**: Read `MASTER.md` for architecture, schema, and conventions.

---

## Context

Read the file `prompts/MASTER.md` first — it contains the full project structure, database schema, tech stack, and coding conventions. This sprint implements the skeleton described there.

---

## Tasks

### Task 0.1 — Initialize Flask Project

Create the project directory structure exactly as specified in MASTER.md. Set up:

1. `run.py` — entry point:
```python
from app import create_app
app = create_app()
if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

2. `app/__init__.py` — Flask app factory:
   - Create Flask app
   - Load config from `app/config.py` (use env var `FLASK_ENV` to pick Dev/Prod/Test)
   - Initialize extensions: SQLAlchemy, Flask-Migrate, Flask-Login, Flask-WTF CSRF
   - Register all Blueprints (auth, dashboard, ingestion, analysis, plan, history, reporting, admin)
   - Create DB tables on first run

3. `app/config.py` — three config classes:
   - `DevelopmentConfig`: SQLite, debug=True
   - `ProductionConfig`: PostgreSQL (from `DATABASE_URL` env var), debug=False
   - `TestingConfig`: SQLite in-memory, testing=True

4. `requirements.txt`:
```
Flask==3.0.*
Flask-SQLAlchemy==3.1.*
Flask-Migrate==4.0.*
Flask-Login==0.6.*
Flask-WTF==1.2.*
WTForms==3.1.*
python-dotenv==1.0.*
werkzeug>=3.0
psycopg2-binary==2.9.*
requests==2.31.*
pytest==8.0.*
gunicorn==21.2.*
```

5. `.env.example`:
```
FLASK_ENV=development
SECRET_KEY=change-me-to-a-random-string
DATABASE_URL=postgresql://user:pass@localhost:5432/cardsmart
FX_API_KEY=your-exchangerate-api-key
```

6. `.gitignore` — include: `.env`, `__pycache__/`, `*.pyc`, `instance/`, `migrations/`, `.pytest_cache/`, `*.db`

### Task 0.2 — Create All SQLAlchemy Models

Create every model file under `app/models/` as defined in MASTER.md schema section:
- `user.py` — User model with password hashing methods:
  - `set_password(password)` → stores hash
  - `check_password(password)` → returns bool
  - `is_admin` property → returns `self.role == 'admin'`
- `transaction.py` — Transaction model
- `card.py` — Card model
- `recommendation.py` — RecommendationRun model
- `plan.py` — PlanCommit model
- `system_event.py` — SystemEvent model

Create `app/models/__init__.py` that imports all models so Alembic can discover them.

### Task 0.3 — Create Blueprint Stubs

For each route module in `app/routes/`, create a minimal Blueprint with a single placeholder route:

```python
# Example: app/routes/auth.py
from flask import Blueprint, render_template
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login')
def login():
    return render_template('auth/login.html')

@auth_bp.route('/register')
def register():
    return render_template('auth/register.html')
```

Do this for ALL 8 route modules: auth, dashboard, ingestion, analysis, plan, history, reporting, admin.

### Task 0.4 — Create Base Template + Placeholder Pages

1. `templates/base.html`:
   - HTML5 boilerplate
   - Bootstrap 5 CDN (CSS + JS)
   - Plotly.js CDN: `<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>`
   - Navigation bar with links to all 9+ screens
   - Show different nav items based on auth state (use `current_user.is_authenticated`)
   - Show admin links only if `current_user.is_admin`
   - Flash messages display area
   - Footer with "CardSmart — FINTECH 512"
   - Block tags: `{% block title %}`, `{% block content %}`

2. Create every template file listed in the project structure with minimal content:
   ```html
   {% extends "base.html" %}
   {% block title %}Page Name{% endblock %}
   {% block content %}
   <h1>Page Name</h1>
   <p>Coming soon — Sprint N</p>
   {% endblock %}
   ```

3. `static/css/style.css` — minimal custom styles (empty or basic overrides).

### Task 0.5 — Seed Data Files

1. Create `seed_data/cards.json` with 10–15 credit cards. Example entry:
```json
{
  "card_id": "chase-sapphire-preferred",
  "name": "Chase Sapphire Preferred",
  "issuer": "Chase",
  "annual_fee": 95,
  "base_reward_rate": 1.0,
  "category_multipliers": {
    "dining": 3,
    "travel": 2,
    "online_shopping": 1,
    "groceries": 1
  },
  "credits": {},
  "credit_utilization_rate": 1.0,
  "transfer_partners": {
    "hyatt": {"ratio": 1.0, "cpp": 2.0},
    "united": {"ratio": 1.0, "cpp": 1.5},
    "southwest": {"ratio": 1.0, "cpp": 1.4}
  },
  "category_caps": {}
}
```

Include these cards (use realistic but approximate data):
- Chase Sapphire Preferred ($95, dining 3x, travel 2x)
- Chase Sapphire Reserve ($550, dining 3x, travel 3x, $300 travel credit)
- Amex Gold ($250, dining 4x, groceries 4x, $120 dining credit, $120 Uber credit)
- Amex Platinum ($695, flights 5x, hotels via Amex Travel 5x, $200 airline credit, $200 hotel credit, $200 Uber credit)
- Citi Double Cash ($0, flat 2% everything)
- Capital One Venture X ($395, travel 2x, $300 travel credit)
- Chase Freedom Unlimited ($0, dining 3x, drugstores 3x, flat 1.5x)
- Chase Freedom Flex ($0, rotating 5x quarterly categories, dining 3x, drugstores 3x)
- US Bank Altitude Go ($0, dining 4x, groceries 2x)
- Citi Premier ($95, travel 3x, dining 3x, groceries 3x, gas 3x)
- Capital One Savor One ($0, dining 3x, entertainment 3x, groceries 3x)
- Wells Fargo Autograph ($0, dining 3x, travel 3x, gas 3x)

2. Create `seed_data/demo_transactions.csv`:
```csv
date,merchant,amount,category
2025-09-01,Chipotle,14.50,dining
2025-09-02,Whole Foods,87.30,groceries
...
```
Generate ~200 rows over 6 months (Sep 2025 – Feb 2026). Category distribution:
- dining: 25% (~$800/mo)
- groceries: 20% (~$600/mo)
- travel: 15% (~$450/mo)
- online_shopping: 15% (~$450/mo)
- gas: 8% (~$240/mo)
- entertainment: 7% (~$210/mo)
- utilities: 5% (~$150/mo)
- other: 5% (~$150/mo)
Total monthly spend: ~$3,000

3. Create `seed_data/demo_transactions.json` — same data in JSON format:
```json
{
  "transactions": [
    {
      "date": "2025-09-01",
      "description": "Chipotle Mexican Grill",
      "amount_cents": 1450,
      "mcc_code": "5812"
    },
    ...
  ]
}
```
This second format satisfies the "two distinct file structures" requirement.

4. Create a seed script `seed_data/seed_db.py`:
   - Load cards.json → insert into Card table
   - Optionally create a demo user + import demo transactions
   - Create one admin user (email: `admin@cardsmart.com`, password: `admin123`)

### Task 0.6 — Database Migration Setup

1. Initialize Flask-Migrate: `flask db init`
2. Create initial migration: `flask db migrate -m "initial schema"`
3. Apply migration: `flask db upgrade`

### Task 0.7 — Verify Everything Runs

1. `python run.py` should start the Flask dev server on port 5000.
2. Visiting `http://localhost:5000/` should show the home page with navigation.
3. Every nav link should resolve to a placeholder page (no 404s).
4. `python seed_data/seed_db.py` should populate the database with cards + demo data.

### Task 0.8 — Initial Tests

Create `tests/conftest.py` with:
- A `client` fixture using the test config (SQLite in-memory)
- A `db_session` fixture that creates tables, seeds minimal data, and rolls back after each test
- A `logged_in_client` fixture that registers + logs in a test user
- An `admin_client` fixture that registers + logs in an admin user

Create `tests/test_smoke.py`:
- Test that every route returns 200 or proper redirect (302 for auth-required pages)
- Test that home page renders without errors

---

## Definition of Done (Sprint 0)

- [ ] `python run.py` starts without errors
- [ ] All 9+ screens are reachable (placeholder content OK)
- [ ] Navigation shows correct links based on auth state
- [ ] Database tables are created correctly
- [ ] Seed data script populates cards + demo data
- [ ] `pytest` passes all smoke tests
- [ ] `.env.example` exists, `.env` is gitignored
- [ ] Code is committed to GitLab
