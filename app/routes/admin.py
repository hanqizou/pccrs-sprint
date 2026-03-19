import json
from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms import CardForm
from app.models.card import Card
from app.services.event_logger import log_system_event


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped(*args, **kwargs):
        if not getattr(current_user, "is_admin", False):
            abort(403)
        return view_func(*args, **kwargs)

    return wrapped


@admin_bp.route("/users")
@admin_required
def users():
    return render_template("admin/users.html")


@admin_bp.route("/events")
@admin_required
def events():
    return render_template("admin/events.html")


@admin_bp.route("/analytics")
@admin_required
def analytics():
    return render_template("admin/analytics.html")


def form_to_card_payload(form):
    return {
        "card_id": form.card_id.data.strip(),
        "name": form.name.data.strip(),
        "issuer": form.issuer.data.strip(),
        "annual_fee": form.annual_fee.data,
        "base_reward_rate": form.base_reward_rate.data,
        "credit_utilization_rate": form.credit_utilization_rate.data,
        "category_multipliers": json.loads((form.category_multipliers_json.data or "{}").strip() or "{}"),
        "credits": json.loads((form.credits_json.data or "{}").strip() or "{}"),
        "transfer_partners": json.loads((form.transfer_partners_json.data or "{}").strip() or "{}"),
        "category_caps": json.loads((form.category_caps_json.data or "{}").strip() or "{}"),
        "is_active": form.is_active.data,
    }


def populate_card_form(form, card):
    form.card_id.data = card.card_id
    form.name.data = card.name
    form.issuer.data = card.issuer
    form.annual_fee.data = card.annual_fee
    form.base_reward_rate.data = card.base_reward_rate
    form.credit_utilization_rate.data = card.credit_utilization_rate
    form.category_multipliers_json.data = json.dumps(card.category_multipliers, indent=2, sort_keys=True)
    form.credits_json.data = json.dumps(card.credits, indent=2, sort_keys=True)
    form.transfer_partners_json.data = json.dumps(card.transfer_partners, indent=2, sort_keys=True)
    form.category_caps_json.data = json.dumps(card.category_caps, indent=2, sort_keys=True)
    form.is_active.data = card.is_active


def validate_card_uniqueness(form, existing_card=None):
    query = Card.query.filter_by(card_id=form.card_id.data.strip())
    if existing_card is not None:
        query = query.filter(Card.id != existing_card.id)
    if query.first():
        form.card_id.errors.append("Card ID must be unique.")
        return False
    return True


@admin_bp.route("/cards")
@admin_required
def cards():
    return render_template("admin/cards.html", cards=Card.query.order_by(Card.name.asc()).all())


@admin_bp.route("/cards/new", methods=["GET", "POST"])
@admin_required
def new_card():
    form = CardForm()
    if form.validate_on_submit() and validate_card_uniqueness(form):
        card = Card(**form_to_card_payload(form))
        db.session.add(card)
        db.session.flush()
        db.session.add(
            log_system_event(
                current_user.id,
                "admin_update_card",
                f"Created card {card.card_id}",
                {"action": "create", "card_id": card.card_id},
            )
        )
        db.session.commit()
        flash("Card created successfully.", "success")
        return redirect(url_for("admin.cards"))

    return render_template("admin/card_form.html", form=form, mode="Create")


@admin_bp.route("/cards/<int:card_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_card(card_id):
    card = db.get_or_404(Card, card_id)
    form = CardForm()
    if form.validate_on_submit() and validate_card_uniqueness(form, existing_card=card):
        for key, value in form_to_card_payload(form).items():
            setattr(card, key, value)
        db.session.add(
            log_system_event(
                current_user.id,
                "admin_update_card",
                f"Updated card {card.card_id}",
                {"action": "update", "card_id": card.card_id},
            )
        )
        db.session.commit()
        flash("Card updated successfully.", "success")
        return redirect(url_for("admin.cards"))

    if not form.is_submitted():
        populate_card_form(form, card)

    return render_template("admin/card_form.html", form=form, mode="Edit", card=card)

