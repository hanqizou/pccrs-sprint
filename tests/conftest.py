import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.extensions import db as _db
from app.models import Card, User


@pytest.fixture
def app():
    import os

    os.environ["FLASK_ENV"] = "testing"
    os.environ["FX_API_KEY"] = "test-fx-key"
    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)

    with app.app_context():
        _db.drop_all()
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    yield _db.session
    _db.session.rollback()


@pytest.fixture
def sample_card(db_session):
    card = Card(
        card_id="sample-card",
        name="Sample Card",
        issuer="Sample Bank",
        annual_fee=95,
        base_reward_rate=1.0,
        category_multipliers={"dining": 3, "travel": 2},
        credits={"travel": 50},
        transfer_partners={"hyatt": {"ratio": 1.0, "cpp": 2.0}},
        category_caps={},
    )
    db_session.add(card)
    db_session.commit()
    return card


@pytest.fixture
def logged_in_client(app, db_session):
    client = app.test_client()
    user = User(email="user@example.com", display_name="Test User")
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/auth/login",
        data={"email": "user@example.com", "password": "password123"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    return client


@pytest.fixture
def admin_client(app, db_session):
    client = app.test_client()
    admin = User(email="admin@example.com", display_name="Admin User", role="admin")
    admin.set_password("password123")
    db_session.add(admin)
    db_session.commit()

    response = client.post(
        "/auth/login",
        data={"email": "admin@example.com", "password": "password123"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    return client
