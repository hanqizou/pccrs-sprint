from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.forms import LoginForm, RegisterForm
from app.models.user import User
from app.services.event_logger import log_system_event
from app.time_utils import utcnow


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data.lower()).first()
        if existing_user:
            form.email.errors.append("Email already in use.")
        else:
            user = User(
                email=form.email.data.lower(),
                display_name=form.display_name.data.strip(),
                preference_mode=form.preference_mode.data,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.flush()
            db.session.add(
                log_system_event(
                    user.id,
                    "user_register",
                    f"New user registered: {user.email}",
                    {"email": user.email},
                )
            )
            db.session.commit()
            login_user(user)
            flash("Registration complete.", "success")
            return redirect(url_for("dashboard.dashboard"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.is_active and user.check_password(form.password.data):
            user.last_login = utcnow()
            db.session.commit()
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard.dashboard"))
        flash("Invalid email or password.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("dashboard.home"))
