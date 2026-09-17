from datetime import date
from app.routers.imports import normalize_phone, parse_date


def test_import_normalizes_phone():
    assert normalize_phone("+91 98765-43210") == "919876543210"


def test_import_accepts_mixed_date_formats():
    assert parse_date("01-09-2026") == date(2026, 9, 1)
    assert parse_date("2026/09/01") == date(2026, 9, 1)
