import io

from app.models import SystemEvent, Transaction
from app.services.category_mapper import map_mcc_to_category
from app.services.fx_service import FXService


def test_category_mapper_covers_major_categories():
    assert map_mcc_to_category("5812") == "dining"
    assert map_mcc_to_category("5411") == "groceries"
    assert map_mcc_to_category("4511") == "travel"
    assert map_mcc_to_category("5541") == "gas"
    assert map_mcc_to_category("7832") == "entertainment"
    assert map_mcc_to_category("9999") == "other"


def test_valid_csv_upload_creates_transactions_and_event(logged_in_client):
    csv_payload = b"date,merchant,amount,category\n2025-09-01,Chipotle,14.50,dining\n2025-09-02,Whole Foods,87.30,groceries\n"
    response = logged_in_client.post(
        "/ingestion/upload",
        data={"data_file": (io.BytesIO(csv_payload), "transactions.csv")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Successfully imported 2 transactions." in response.data
    assert Transaction.query.count() == 2
    assert SystemEvent.query.filter_by(event_type="import").count() == 1


def test_csv_missing_columns_is_rejected(logged_in_client):
    csv_payload = b"date,merchant,amount\n2025-09-01,Chipotle,14.50\n"
    response = logged_in_client.post(
        "/ingestion/upload",
        data={"data_file": (io.BytesIO(csv_payload), "bad.csv")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Missing columns: category" in response.data


def test_duplicate_upload_is_rejected(logged_in_client):
    csv_payload = b"date,merchant,amount,category\n2025-09-01,Chipotle,14.50,dining\n"
    upload_args = {
        "data": {"data_file": (io.BytesIO(csv_payload), "dup.csv")},
        "content_type": "multipart/form-data",
        "follow_redirects": True,
    }
    first_response = logged_in_client.post("/ingestion/upload", **upload_args)
    second_response = logged_in_client.post(
        "/ingestion/upload",
        data={"data_file": (io.BytesIO(csv_payload), "dup.csv")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert first_response.status_code == 200
    assert b"This file has already been imported." in second_response.data


def test_empty_file_is_rejected(logged_in_client):
    response = logged_in_client.post(
        "/ingestion/upload",
        data={"data_file": (io.BytesIO(b""), "empty.csv")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"No transactions found." in response.data


def test_invalid_amount_is_rejected(logged_in_client):
    csv_payload = b"date,merchant,amount,category\n2025-09-01,Chipotle,-14.50,dining\n"
    response = logged_in_client.post(
        "/ingestion/upload",
        data={"data_file": (io.BytesIO(csv_payload), "invalid.csv")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Amount must be greater than 0." in response.data


def test_valid_json_upload_maps_mcc_and_converts_cents(logged_in_client):
    json_payload = b'{"transactions":[{"date":"2025-09-01","description":"Chipotle","amount_cents":1450,"mcc_code":"5812"}]}'
    response = logged_in_client.post(
        "/ingestion/upload",
        data={"data_file": (io.BytesIO(json_payload), "transactions.json")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    txn = Transaction.query.first()
    assert txn.category == "dining"
    assert txn.amount == 14.5


def test_invalid_json_structure_returns_helpful_error(logged_in_client):
    json_payload = b'{"wrong_key":[]}'
    response = logged_in_client.post(
        "/ingestion/upload",
        data={"data_file": (io.BytesIO(json_payload), "bad.json")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid structure: expected a &#39;transactions&#39; list." in response.data


def test_fx_sync_stores_rates_with_mocked_api(logged_in_client, monkeypatch):
    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"result": "success", "conversion_rates": {"USD": 1.0, "EUR": 0.9}}

    monkeypatch.setattr("app.services.fx_service.requests.get", lambda *args, **kwargs: DummyResponse())
    FXService.clear_cache()

    response = logged_in_client.post("/ingestion/fx-sync", follow_redirects=True)
    assert response.status_code == 200
    assert FXService().get_rate("EUR") == round(1 / 0.9, 8)


def test_fx_cache_is_used_when_api_is_unavailable(monkeypatch):
    from app.time_utils import utcnow
    import requests

    FXService.set_cache({"USD": 1.0, "EUR": 1.11}, updated_at=utcnow())
    monkeypatch.setattr(
        "app.services.fx_service.requests.get",
        lambda *args, **kwargs: (_ for _ in ()).throw(requests.RequestException("down")),
    )
    assert FXService().get_rate("EUR") == 1.11


def test_foreign_currency_csv_is_converted_using_cached_fx(logged_in_client):
    from app.time_utils import utcnow

    FXService.set_cache({"USD": 1.0, "EUR": 1.1}, updated_at=utcnow())
    csv_payload = (
        b"date,merchant,amount,category,original_currency\n"
        b"2025-09-01,Paris Cafe,10.00,dining,EUR\n"
    )
    response = logged_in_client.post(
        "/ingestion/upload",
        data={"data_file": (io.BytesIO(csv_payload), "foreign.csv")},
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert response.status_code == 200
    txn = Transaction.query.first()
    assert txn.original_currency == "EUR"
    assert txn.original_amount == 10.0
    assert txn.amount == 11.0
