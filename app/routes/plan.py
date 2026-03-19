from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required


plan_bp = Blueprint("plan", __name__, url_prefix="/plan")


@plan_bp.route("/commit", methods=["GET", "POST"])
@login_required
def commit():
    if request.method == "POST":
        flash("Plan commit is coming in a later sprint.", "info")
        return redirect(url_for("plan.commit"))
    return render_template("plan/commit.html")


@plan_bp.route("/remove", methods=["GET", "POST"])
@login_required
def remove():
    if request.method == "POST":
        flash("Plan removal is coming in a later sprint.", "info")
        return redirect(url_for("plan.commit"))
    return render_template("plan/remove.html")

