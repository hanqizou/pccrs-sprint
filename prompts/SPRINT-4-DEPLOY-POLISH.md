# Sprint 4 — Deployment, CI/CD, Security & Polish

> **Goal**: Deploy to Duke VCM, add optional items for bonus points, polish UI/UX, final testing.
> **Core Req points targeted**: Infrastructure (50 pts) + Database upgrade (50 pts) + CI/CD (40 pts) + Security (25 pts) + Containerization (25 pts) + System Architecture (20 pts)
> **Prerequisites**: Sprints 0–3 completed. All core functionality working locally.

---

## Context

Read `prompts/MASTER.md` for conventions. The app is fully functional locally. This sprint focuses on production deployment, optional bonus items, and overall polish. Prioritize items by point value — stop when you've hit 650+ total.

---

## Tasks (Ordered by Priority / Point Value)

### Task 4.1 — PostgreSQL Migration (50 pts vs 25 pts for SQLite)

**Current**: app works on SQLite locally.
**Target**: switch to PostgreSQL for production (50 pts).

1. Install PostgreSQL on VCM (or use Duke-provided DB service)
2. Create database: `createdb cardsmart`
3. Create user: `createuser -P cardsmart_user`
4. Update `.env` on VCM:
```
DATABASE_URL=postgresql://cardsmart_user:password@localhost:5432/cardsmart
```
5. Verify SQLAlchemy connects correctly
6. Run migrations: `flask db upgrade`
7. Run seed script
8. Test: all functionality works on PostgreSQL

**Gotchas**:
- SQLite uses `AUTOINCREMENT`, PostgreSQL uses `SERIAL` — SQLAlchemy handles this if you use `db.Integer, primary_key=True`
- JSON columns: PostgreSQL has native JSON support, SQLite stores as text — SQLAlchemy handles this transparently
- Test with both: keep `TestingConfig` on SQLite for fast tests, `ProductionConfig` on PostgreSQL

### Task 4.2 — Duke VCM Deployment (25 pts on VCM + 25 pts for auto-start)

1. **Reserve a VCM instance** at https://vcm.duke.edu/
2. **SSH into VCM**, set up environment:
```bash
sudo apt update && sudo apt install -y python3-pip python3-venv postgresql nginx
```
3. **Clone repo** from GitLab
4. **Create virtualenv** and install deps:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
5. **Set up .env** with production config
6. **Run migrations + seed data**
7. **Configure Gunicorn** as the WSGI server:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```
8. **Configure Nginx** as reverse proxy:
```nginx
server {
    listen 80;
    server_name vcmXXX.vm.duke.edu;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    location /static {
        alias /path/to/cardsmart/app/static;
    }
}
```
9. **Auto-start on reboot** — create systemd service:
```ini
# /etc/systemd/system/cardsmart.service
[Unit]
Description=CardSmart Flask App
After=network.target postgresql.service

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/cardsmart
Environment="PATH=/home/ubuntu/cardsmart/venv/bin"
EnvironmentFile=/home/ubuntu/cardsmart/.env
ExecStart=/home/ubuntu/cardsmart/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
Restart=always

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable cardsmart
sudo systemctl start cardsmart
sudo systemctl enable nginx
```
10. **Test auto-start**: `sudo reboot`, wait, verify site is up

### Task 4.3 — CI/CD Pipeline (40 pts)

Create `.gitlab-ci.yml`:

```yaml
stages:
  - build
  - test
  - sast
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

# 10 pts: build release on every commit
build:
  stage: build
  image: python:3.11
  script:
    - python -m venv venv
    - source venv/bin/activate
    - pip install -r requirements.txt
  artifacts:
    paths:
      - venv/
  cache:
    paths:
      - .cache/pip/

# 10 pts: run test suite
test:
  stage: test
  image: python:3.11
  dependencies:
    - build
  script:
    - source venv/bin/activate
    - pip install pytest
    - pytest tests/ -v --tb=short
  artifacts:
    reports:
      junit: report.xml

# 10 pts: GitLab SAST tooling
sast:
  stage: sast
  include:
    - template: Security/SAST.gitlab-ci.yml

# 10 pts: auto-deploy to VCM
deploy:
  stage: deploy
  only:
    - main
  script:
    - apt-get update && apt-get install -y openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | ssh-add -
    - ssh -o StrictHostKeyChecking=no ubuntu@vcmXXX.vm.duke.edu "cd ~/cardsmart && git pull && source venv/bin/activate && pip install -r requirements.txt && flask db upgrade && sudo systemctl restart cardsmart"
```

**Setup required**:
- Add `SSH_PRIVATE_KEY` as GitLab CI/CD variable (Settings → CI/CD → Variables)
- Ensure VCM allows SSH from GitLab runner

### Task 4.4 — Security Analysis (25 pts)

**4.4a — DFD + STRIDE Threat Model (15 pts)**

Create `docs/security/threat_model.md`:

1. **Data Flow Diagram (DFD)** — draw using Mermaid or ASCII:
   - External entities: User (browser), External FX API
   - Processes: Flask App (auth, ingestion, recommendation, admin)
   - Data stores: PostgreSQL DB, FX Rate Cache
   - Data flows: HTTP requests, API calls, DB queries

2. **STRIDE Analysis** — for each DFD element:
   - **S**poofing: can someone impersonate a user? → mitigated by hashed passwords + session auth
   - **T**ampering: can data be modified in transit? → mitigated by HTTPS on VCM
   - **R**epudiation: can user deny actions? → mitigated by SystemEvent audit log
   - **I**nformation Disclosure: can data leak? → mitigated by no PII, env vars for secrets
   - **D**enial of Service: can the system be overwhelmed? → mitigated by rate limiting (optional)
   - **E**levation of Privilege: can normal user become admin? → mitigated by role checks on all admin routes

**4.4b — Semgrep SAST (5 pts)**

```bash
pip install semgrep
semgrep --config auto app/ --output docs/security/semgrep_report.json --json
```
Fix any high-severity findings. Save report.

**4.4c — OWASP ZAP (5 pts)**

```bash
# Run ZAP against deployed site
docker run -t owasp/zap2docker-stable zap-baseline.py -t https://vcmXXX.vm.duke.edu > docs/security/zap_report.txt
```
Save report, fix any critical findings.

### Task 4.5 — Containerization (25 pts)

**Dockerfile** (15 pts):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:create_app()"]
```

**docker-compose.yml** (10 pts):
```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://cardsmart:password@db:5432/cardsmart
      - SECRET_KEY=${SECRET_KEY}
      - FX_API_KEY=${FX_API_KEY}
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=cardsmart
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=cardsmart
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
volumes:
  pgdata:
```

Test: `docker-compose up --build` → app accessible at localhost:8000

### Task 4.6 — System Architecture Diagrams (20 pts)

Create `docs/architecture/` with C4 model diagrams (Mermaid or draw.io):

1. **System Context** (5 pts): CardSmart ↔ User ↔ FX API
2. **Container** (5 pts): Browser → Nginx → Flask App → PostgreSQL; Flask App → FX API
3. **Component** (5 pts): Flask Blueprints detail — auth, ingestion, analysis, plan, history, reporting, admin
4. **Code** (5 pts): Class diagram of models + services

### Task 4.7 — UI/UX Polish

1. **Consistent styling**: ensure all pages use the same Bootstrap theme
2. **Flash messages**: styled alerts (green for success, red for error, yellow for warning)
3. **Loading states**: show spinner when AJAX requests are in flight
4. **Empty states**: every page handles "no data" gracefully with helpful CTA
5. **Responsive**: test on different screen widths (Bootstrap grid should handle most)
6. **Error pages**: custom 404 and 500 error pages

### Task 4.8 — Comprehensive Testing

Ensure test coverage for all critical paths:

```bash
# Run all tests with coverage
pip install pytest-cov
pytest tests/ -v --cov=app --cov-report=html
```

Target: > 70% coverage on `app/services/` and `app/routes/`.

**Must-have tests**:
- Auth: register, login, logout, duplicate email, wrong password
- Ingestion: CSV valid/invalid, JSON valid/invalid, duplicate detection, FX conversion
- Recommendation: known-input calculations, edge cases, determinism
- Plan: commit, remove, atomic transaction
- History: display, filter, pagination
- Reporting: CSV export, JSON export
- Admin: role checks (403 for non-admin), user list, disable, reset password
- Smoke: every route returns expected status code

---

## Points Tally (After Sprint 4)

| Category | Points | Status |
|----------|--------|--------|
| UI: 9 screens (Sprint 0–3) | 300 | ✅ |
| Data Integration (Sprint 1) | 50 | ✅ |
| Charting (Sprint 2) | 75 | ✅ |
| Admin Functionality (Sprint 3) | 100 | ✅ |
| Infrastructure — VCM + auto-start (Sprint 4) | 50 | ✅ |
| Database — PostgreSQL (Sprint 4) | 50 | ✅ |
| **Required Subtotal** | **625** | |
| CI/CD Pipeline (Sprint 4) | 40 | ✅ |
| Security Analysis (Sprint 4) | 25 | ✅ |
| Containerization (Sprint 4) | 25 | ✅ |
| System Architecture (Sprint 4) | 20 | ✅ |
| **Grand Total** | **735** | well above 650 |

---

## Definition of Done (Sprint 4)

- [ ] App runs on Duke VCM with PostgreSQL
- [ ] App auto-starts on VCM reboot
- [ ] GitLab CI/CD pipeline: build + test + SAST + deploy
- [ ] Security: DFD + STRIDE threat model completed
- [ ] Security: Semgrep report generated, critical issues fixed
- [ ] Security: OWASP ZAP scan completed
- [ ] Dockerfile builds and runs the app
- [ ] docker-compose.yml starts app + PostgreSQL
- [ ] C4 architecture diagrams in docs/
- [ ] UI is polished, consistent, handles edge cases
- [ ] Test coverage > 70% on services + routes
- [ ] All code committed to GitLab
- [ ] README.md updated with setup instructions + team info
