def test_home_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"CardSmart" in response.data


def test_public_routes(client):
    for route in ["/", "/auth/login", "/auth/register"]:
        response = client.get(route)
        assert response.status_code == 200


def test_anonymous_nav_shows_public_links_only(client):
    response = client.get("/")
    assert b"Login" in response.data
    assert b"Register" in response.data
    assert b"Dashboard" not in response.data
    assert b"Admin Users" not in response.data


def test_protected_routes_redirect_anonymous_users(client):
    protected_routes = [
        "/dashboard",
        "/ingestion",
        "/analysis/decision",
        "/analysis/current",
        "/plan/commit",
        "/history",
        "/reporting",
    ]

    for route in protected_routes:
        response = client.get(route)
        assert response.status_code == 302
        assert "/auth/login" in response.headers["Location"]


def test_logged_in_user_can_reach_core_pages(logged_in_client):
    for route in [
        "/dashboard",
        "/ingestion",
        "/analysis/decision",
        "/analysis/current",
        "/plan/commit",
        "/history",
        "/reporting",
    ]:
        response = logged_in_client.get(route)
        assert response.status_code == 200


def test_logged_in_nav_hides_admin_links(logged_in_client):
    response = logged_in_client.get("/dashboard")
    assert b"Dashboard" in response.data
    assert b"Logout" in response.data
    assert b"Admin Users" not in response.data


def test_admin_routes_forbid_normal_users(logged_in_client):
    for route in ["/admin/users", "/admin/events", "/admin/analytics"]:
        assert logged_in_client.get(route).status_code == 403


def test_admin_routes_allow_admin_users(admin_client):
    for route in ["/admin/users", "/admin/events", "/admin/analytics"]:
        assert admin_client.get(route).status_code == 200


def test_admin_nav_shows_admin_links(admin_client):
    response = admin_client.get("/dashboard")
    assert b"Admin Users" in response.data
    assert b"Admin Events" in response.data
    assert b"Admin Analytics" in response.data
