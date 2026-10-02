"""Isolated parser tests; no Home Assistant or Bluetooth required."""
import pytest
from custom_components.fan_ble_home.shared_code import parse_shared_code

def test_canonical():
    assert parse_shared_code("1,2,3,4,5").normalized == "1,2,3,4,5"

def test_whitespace_and_brackets():
    assert parse_shared_code(" [001, 2, 3, 4, 005] ").values == (1, 2, 3, 4, 5)

def test_byte_boundaries():
    assert parse_shared_code("0,255,0,255,0").values == (0, 255, 0, 255, 0)

def test_reject_invalid_text():
    for text in ("", "1,2,3,4", "1,2,3,4,5,6", "1,2,3,4,256", "-1,2,3,4,5", "1.0,2,3,4,5", "1,2,3,4,x", "[1,2,3,4,5", "https://example.com", "1 2 3 4 5"):
        with pytest.raises(ValueError):
            parse_shared_code(text)
