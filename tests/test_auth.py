def test_home_page_for_anonymous_users(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Get Started" in response.data


def test_home_redirects_authenticated_users(logged_in_client):
    response = logged_in_client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")


def test_registration_creates_user_and_logs_event(client, db_session):
    response = client.post(
        "/auth/register",
        data={
            "display_name": "New User",
            "email": "new@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "preference_mode": "travel",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")

    from app.models import SystemEvent, User

    user = User.query.filter_by(email="new@example.com").first()
    assert user is not None
    assert user.password_hash != "password123"
    assert user.check_password("password123")

    event = SystemEvent.query.filter_by(event_type="user_register", user_id=user.id).first()
    assert event is not None


def test_registration_rejects_duplicate_email(client, db_session):
    from app.models import User

    user = User(email="dup@example.com", display_name="Dup")
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/auth/register",
        data={
            "display_name": "Another Dup",
            "email": "dup@example.com",
            "password": "password123",
            "confirm_password": "password123",
            "preference_mode": "travel",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Email already in use." in response.data


def test_registration_rejects_invalid_email(client):
    response = client.post(
        "/auth/register",
        data={
            "display_name": "Bad Email",
            "email": "not-an-email",
            "password": "password123",
            "confirm_password": "password123",
            "preference_mode": "travel",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid email address." in response.data


def test_registration_rejects_mismatched_passwords(client):
    response = client.post(
        "/auth/register",
        data={
            "display_name": "Mismatch",
            "email": "mismatch@example.com",
            "password": "password123",
            "confirm_password": "password124",
            "preference_mode": "travel",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Field must be equal to password." in response.data


def test_registration_rejects_short_password(client):
    response = client.post(
        "/auth/register",
        data={
            "display_name": "Short",
            "email": "short@example.com",
            "password": "short",
            "confirm_password": "short",
            "preference_mode": "travel",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Password must be at least 8 characters long." in response.data


def test_login_updates_last_login(client, db_session):
    from app.models import User

    user = User(email="login@example.com", display_name="Login User")
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/auth/login",
        data={"email": "login@example.com", "password": "password123"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    db_session.refresh(user)
    assert user.last_login is not None


def test_login_rejects_wrong_password_with_generic_message(client, db_session):
    from app.models import User

    user = User(email="wrongpass@example.com", display_name="Wrong Password")
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/auth/login",
        data={"email": "wrongpass@example.com", "password": "nope1234"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


def test_login_rejects_missing_user_with_generic_message(client):
    response = client.post(
        "/auth/login",
        data={"email": "missing@example.com", "password": "password123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


def test_disabled_user_cannot_log_in(client, db_session):
    from app.models import User

    user = User(email="disabled@example.com", display_name="Disabled", is_active=False)
    user.set_password("password123")
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/auth/login",
        data={"email": "disabled@example.com", "password": "password123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


def test_logout_clears_session(logged_in_client):
    response = logged_in_client.get("/auth/logout", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")

    dashboard_response = logged_in_client.get("/dashboard")
    assert dashboard_response.status_code == 302
    assert "/auth/login" in dashboard_response.headers["Location"]
