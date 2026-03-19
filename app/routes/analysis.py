from flask import Blueprint, render_template
from flask_login import login_required


analysis_bp = Blueprint("analysis", __name__, url_prefix="/analysis")


@analysis_bp.route("/decision")
@login_required
def decision():
    return render_template("analysis/decision.html")


@analysis_bp.route("/current")
@login_required
def current():
    return render_template("analysis/current.html")

