from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.forms import UploadTransactionsForm
from app.services.fx_service import FXService, FXServiceError
from app.services.ingestion_service import IngestionError, import_transactions_for_user

ingestion_bp = Blueprint("ingestion", __name__, url_prefix="/ingestion")


@ingestion_bp.route("", methods=["GET"])
@ingestion_bp.route("/", methods=["GET"])
@login_required
def index():
    form = UploadTransactionsForm()
    return render_template(
        "ingestion/upload.html",
        form=form,
        fx_last_updated=FXService().last_updated(),
    )


@ingestion_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    form = UploadTransactionsForm()
    if not form.is_submitted():
        return redirect(url_for("ingestion.index"))

    if not form.validate():
        return render_template(
            "ingestion/upload.html",
            form=form,
            fx_last_updated=FXService().last_updated(),
        ), 400

    uploaded_file = form.data_file.data
    file_bytes = uploaded_file.read()
    if not file_bytes:
        flash("No transactions found.", "danger")
        return redirect(url_for("ingestion.index"))

    try:
        imported = import_transactions_for_user(current_user, uploaded_file.filename, file_bytes)
    except IngestionError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("ingestion.index"))

    flash(f"Successfully imported {len(imported)} transactions.", "success")
    return redirect(url_for("dashboard.dashboard"))


@ingestion_bp.route("/fx-sync", methods=["POST"])
@login_required
def fx_sync():
    service = FXService()
    try:
        service.sync_rates()
        flash(f"FX rates refreshed at {service.last_updated()}.", "success")
    except FXServiceError as exc:
        flash(str(exc), "warning")
    except Exception:
        if service.last_updated():
            flash(f"FX API unavailable. Using cached rates from {service.last_updated()}.", "warning")
        else:
            flash("FX sync failed and no cached rates are available.", "danger")
    return redirect(url_for("ingestion.index"))

