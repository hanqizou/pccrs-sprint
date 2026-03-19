import os
from datetime import timedelta

import requests

from app.time_utils import utcnow


class FXServiceError(Exception):
    pass


class FXService:
    API_URL = "https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
    CACHE_TTL = timedelta(hours=24)
    _cache = {"rates": None, "updated_at": None}

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("FX_API_KEY")

    @classmethod
    def set_cache(cls, rates, updated_at=None):
        cls._cache = {
            "rates": rates,
            "updated_at": updated_at or utcnow(),
        }

    @classmethod
    def clear_cache(cls):
        cls._cache = {"rates": None, "updated_at": None}

    def last_updated(self):
        return self._cache["updated_at"]

    def has_fresh_cache(self):
        updated_at = self._cache["updated_at"]
        return bool(updated_at and utcnow() - updated_at < self.CACHE_TTL and self._cache["rates"])

    def _normalize_rates(self, raw_rates):
        normalized = {"USD": 1.0}
        for currency, value in raw_rates.items():
            if currency == "USD":
                normalized[currency] = 1.0
                continue
            if value:
                normalized[currency] = round(1 / value, 8)
        return normalized

    def sync_rates(self):
        if not self.api_key:
            raise FXServiceError("FX API key is not configured.")

        response = requests.get(
            self.API_URL.format(api_key=self.api_key),
            timeout=10,
        )
        response.raise_for_status()
        payload = response.json()

        raw_rates = payload.get("conversion_rates")
        if payload.get("result") != "success" or not isinstance(raw_rates, dict):
            raise FXServiceError("FX API response did not include conversion rates.")

        normalized_rates = self._normalize_rates(raw_rates)
        self.set_cache(normalized_rates)
        return normalized_rates

    def get_rates(self):
        if self.has_fresh_cache():
            return self._cache["rates"]

        try:
            return self.sync_rates()
        except (requests.RequestException, FXServiceError):
            if self._cache["rates"]:
                return self._cache["rates"]
            raise FXServiceError("Unable to refresh FX rates and no cached rates are available.")

    def get_rate(self, currency):
        currency = (currency or "USD").upper()
        if currency == "USD":
            return 1.0

        rates = self.get_rates()
        rate = rates.get(currency)
        if rate is None:
            raise FXServiceError(f"No FX rate available for {currency}.")
        return rate

    def convert_to_usd(self, amount, currency):
        return round(float(amount) * self.get_rate(currency), 2)


