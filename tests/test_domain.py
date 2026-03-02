import pytest
from src.domain.postprocess import DataNormalizer

@pytest.mark.parametrize(
    "input_date, expected",
    [
        ("25 сентября 2025 г.", "2025-09-25"),
        ("21.01.2026", "2026-01-21"),
        ("1 февраля 2024", "2024-02-01"),
        ("", ""), 
        (None, ""),
    ],
)
def test_normalize_date(input_date, expected):
    assert DataNormalizer.normalize_date(input_date) == expected

@pytest.mark.parametrize(
    "input_val, expected",
    [
        ("22зо6о", "223060"),
        ("УНП 19O8199З7", "УНП 190819937"),
        ("Серия ЮП О1", "Серия ЮП 01"),
        (None, None),
    ],
)
def test_fix_ocr_numbers(input_val, expected):
    assert DataNormalizer.fix_ocr_numbers(input_val) == expected