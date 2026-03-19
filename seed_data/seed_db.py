import csv
import json
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from app.extensions import db
from app.models import Card, Transaction, User


CARDS_PATH = BASE_DIR / "cards.json"
CSV_PATH = BASE_DIR / "demo_transactions.csv"


def load_cards():
    with CARDS_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_transactions():
    with CSV_PATH.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def upsert_cards(cards):
    for item in cards:
        card = Card.query.filter_by(card_id=item["card_id"]).first()
        if card is None:
            card = Card(card_id=item["card_id"])
            db.session.add(card)

        card.name = item["name"]
        card.issuer = item["issuer"]
        card.annual_fee = item["annual_fee"]
        card.base_reward_rate = item["base_reward_rate"]
        card.category_multipliers = item["category_multipliers"]
        card.credits = item["credits"]
        card.credit_utilization_rate = item["credit_utilization_rate"]
        card.transfer_partners = item["transfer_partners"]
        card.category_caps = item["category_caps"]
        card.is_active = True


def ensure_user(email, password, display_name, role="normal"):
    user = User.query.filter_by(email=email).first()
    if user is None:
        user = User(email=email, display_name=display_name, role=role)
        user.set_password(password)
        db.session.add(user)
    else:
        user.display_name = display_name
        user.role = role
    return user


def import_demo_transactions(user, rows):
    import_id = "demo-seed-2026-03-17"
    existing = Transaction.query.filter_by(user_id=user.id, import_id=import_id).first()
    if existing:
        return

    for row in rows:
        transaction = Transaction(
            user_id=user.id,
            import_id=import_id,
            date=datetime.strptime(row["date"], "%Y-%m-%d").date(),
            merchant=row["merchant"],
            amount=float(row["amount"]),
            original_amount=float(row["amount"]),
            original_currency="USD",
            category=row["category"],
            mcc_code=row.get("mcc_code") or None,
        )
        db.session.add(transaction)


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        upsert_cards(load_cards())

        demo_user = ensure_user("demo@cardsmart.com", "demo123", "Demo User")
        admin_user = ensure_user("admin@cardsmart.com", "admin123", "Admin User", role="admin")

        db.session.commit()
        import_demo_transactions(demo_user, load_transactions())
        db.session.commit()

        print(f"Seeded {Card.query.count()} cards.")
        print(f"Demo user: {demo_user.email}")
        print(f"Admin user: {admin_user.email}")


if __name__ == "__main__":
    main()
