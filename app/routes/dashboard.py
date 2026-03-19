from sqlalchemy import func

from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models.transaction import Transaction


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("home.html")


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():
    stats = None
    total_transactions = Transaction.query.filter_by(user_id=current_user.id).count()
    if total_transactions:
        start_date, end_date = (
            Transaction.query.with_entities(
                func.min(Transaction.date),
                func.max(Transaction.date),
            )
            .filter_by(user_id=current_user.id)
            .first()
        )
        top_categories = (
            db.session.query(
                Transaction.category,
                func.sum(Transaction.amount).label("total"),
            )
            .filter(Transaction.user_id == current_user.id)
            .group_by(Transaction.category)
            .order_by(func.sum(Transaction.amount).desc())
            .limit(3)
            .all()
        )
        stats = {
            "total_transactions": total_transactions,
            "start_date": start_date,
            "end_date": end_date,
            "top_categories": top_categories,
        }

    return render_template("dashboard.html", stats=stats)

