import csv
import hashlib
import io
import json
from datetime import datetime

from app.extensions import db
from app.models.transaction import Transaction
from app.services.category_mapper import map_mcc_to_category, normalize_category
from app.services.event_logger import log_system_event
from app.services.fx_service import FXService, FXServiceError


REQUIRED_CSV_COLUMNS = {"date", "merchant", "amount", "category"}


class IngestionError(Exception):
    pass


def compute_import_id(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()


def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError) as exc:
        raise IngestionError(f"Invalid date '{value}'. Expected YYYY-MM-DD.") from exc


def parse_amount(value):
    try:
        amount = float(value)
    except (TypeError, ValueError) as exc:
        raise IngestionError(f"Invalid amount '{value}'.") from exc

    if amount <= 0:
        raise IngestionError("Amount must be greater than 0.")
    return round(amount, 2)


def parse_csv_transactions(file_bytes, fx_service=None):
    text = file_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    fieldnames = set(reader.fieldnames or [])
    missing_columns = REQUIRED_CSV_COLUMNS - fieldnames
    if missing_columns:
        raise IngestionError(f"Missing columns: {', '.join(sorted(missing_columns))}")

    fx_service = fx_service or FXService()
    transactions = []
    for row in reader:
        amount = parse_amount(row.get("amount"))
        currency = (row.get("original_currency") or row.get("currency") or "USD").upper()
        usd_amount = amount
        if currency != "USD":
            try:
                usd_amount = fx_service.convert_to_usd(amount, currency)
            except FXServiceError as exc:
                raise IngestionError(str(exc)) from exc

        transactions.append(
            {
                "date": parse_date(row.get("date")),
                "merchant": (row.get("merchant") or "").strip(),
                "amount": usd_amount,
                "original_amount": amount,
                "original_currency": currency,
                "category": normalize_category(row.get("category")),
                "mcc_code": (row.get("mcc_code") or "").strip() or None,
            }
        )

    if not transactions:
        raise IngestionError("No transactions found.")

    return transactions


def parse_json_transactions(file_bytes, fx_service=None):
    try:
        payload = json.loads(file_bytes.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise IngestionError(f"Invalid JSON: {exc.msg}") from exc

    transactions_payload = payload.get("transactions")
    if not isinstance(transactions_payload, list):
        raise IngestionError("Invalid structure: expected a 'transactions' list.")

    fx_service = fx_service or FXService()
    parsed_transactions = []
    for item in transactions_payload:
        if not isinstance(item, dict):
            raise IngestionError("Invalid structure: each transaction must be an object.")

        required = {"date", "description", "amount_cents", "mcc_code"}
        if missing := sorted(required - set(item)):
            raise IngestionError(f"Invalid structure: missing {', '.join(missing)}.")

        try:
            amount_cents = int(item["amount_cents"])
        except (TypeError, ValueError) as exc:
            raise IngestionError(f"Invalid amount_cents '{item.get('amount_cents')}'.") from exc

        if amount_cents <= 0:
            raise IngestionError("amount_cents must be greater than 0.")

        original_amount = round(amount_cents / 100, 2)
        currency = (item.get("original_currency") or item.get("currency") or "USD").upper()
        usd_amount = original_amount
        if currency != "USD":
            try:
                usd_amount = fx_service.convert_to_usd(original_amount, currency)
            except FXServiceError as exc:
                raise IngestionError(str(exc)) from exc

        parsed_transactions.append(
            {
                "date": parse_date(item.get("date")),
                "merchant": (item.get("description") or "").strip(),
                "amount": usd_amount,
                "original_amount": original_amount,
                "original_currency": currency,
                "category": map_mcc_to_category(item.get("mcc_code")),
                "mcc_code": str(item.get("mcc_code")),
            }
        )

    if not parsed_transactions:
        raise IngestionError("No transactions found.")

    return parsed_transactions


def import_transactions_for_user(user, filename, file_bytes, fx_service=None):
    import_id = compute_import_id(file_bytes)
    duplicate = Transaction.query.filter_by(user_id=user.id, import_id=import_id).first()
    if duplicate:
        raise IngestionError("This file has already been imported.")

    lower_name = filename.lower()
    if lower_name.endswith(".csv"):
        parsed_transactions = parse_csv_transactions(file_bytes, fx_service=fx_service)
    elif lower_name.endswith(".json"):
        parsed_transactions = parse_json_transactions(file_bytes, fx_service=fx_service)
    else:
        raise IngestionError("Unsupported file type.")

    created_transactions = []
    for item in parsed_transactions:
        created_transactions.append(
            Transaction(
                user_id=user.id,
                import_id=import_id,
                date=item["date"],
                merchant=item["merchant"],
                amount=item["amount"],
                original_amount=item["original_amount"],
                original_currency=item["original_currency"],
                category=item["category"],
                mcc_code=item["mcc_code"],
            )
        )

    db.session.add_all(created_transactions)
    db.session.add(
        log_system_event(
            user.id,
            "import",
            f"Imported {len(created_transactions)} transactions from {filename}",
            {
                "filename": filename,
                "count": len(created_transactions),
                "import_id": import_id,
            },
        )
    )
    db.session.commit()
    return created_transactions
