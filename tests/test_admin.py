from app.extensions import db
from app.models import Card, SystemEvent


def test_normal_user_cannot_access_card_admin(logged_in_client):
    response = logged_in_client.get("/admin/cards")
    assert response.status_code == 403


def test_admin_can_list_cards(admin_client, sample_card):
    response = admin_client.get("/admin/cards")
    assert response.status_code == 200
    assert b"Sample Card" in response.data


def test_admin_can_create_card(admin_client):
    response = admin_client.post(
        "/admin/cards/new",
        data={
            "card_id": "new-card",
            "name": "New Card",
            "issuer": "New Bank",
            "annual_fee": "0",
            "base_reward_rate": "1.5",
            "credit_utilization_rate": "1.0",
            "category_multipliers_json": '{"dining": 3}',
            "credits_json": "{}",
            "transfer_partners_json": "{}",
            "category_caps_json": "{}",
            "is_active": "y",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert Card.query.filter_by(card_id="new-card").first() is not None
    assert SystemEvent.query.filter_by(event_type="admin_update_card").count() == 1


def test_admin_can_edit_card(admin_client, sample_card):
    response = admin_client.post(
        f"/admin/cards/{sample_card.id}/edit",
        data={
            "card_id": sample_card.card_id,
            "name": "Updated Card",
            "issuer": sample_card.issuer,
            "annual_fee": "199",
            "base_reward_rate": "2.0",
            "credit_utilization_rate": "0.9",
            "category_multipliers_json": '{"travel": 4}',
            "credits_json": '{"travel": 100}',
            "transfer_partners_json": "{}",
            "category_caps_json": "{}",
            "is_active": "y",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    updated = db.session.get(Card, sample_card.id)
    assert updated.name == "Updated Card"
    assert updated.annual_fee == 199.0
    assert updated.category_multipliers == {"travel": 4}


def test_invalid_negative_multiplier_is_rejected(admin_client):
    response = admin_client.post(
        "/admin/cards/new",
        data={
            "card_id": "bad-card",
            "name": "Bad Card",
            "issuer": "Bad Bank",
            "annual_fee": "0",
            "base_reward_rate": "1.0",
            "credit_utilization_rate": "1.0",
            "category_multipliers_json": '{"dining": -3}',
            "credits_json": "{}",
            "transfer_partners_json": "{}",
            "category_caps_json": "{}",
            "is_active": "y",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Multiplier for &#39;dining&#39; must be a non-negative number." in response.data
    assert Card.query.filter_by(card_id="bad-card").first() is None
