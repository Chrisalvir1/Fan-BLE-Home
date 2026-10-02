"""Tests of structure and hints, not real fan compatibility."""
import pytest
from custom_components.fan_ble_home.advertisement import parse_advertisement, protocol_hints, AdField

def test_fields():
    fields = parse_advertisement(bytes.fromhex("02010603030a18"))
    assert [(x.ad_type, x.data.hex()) for x in fields] == [(1, "06"), (3, "0a18")]

def test_zero_padding():
    assert len(parse_advertisement(bytes.fromhex("0201060000"))) == 1

def test_invalid():
    for raw in (bytes.fromhex("02"), bytes.fromhex("030106"), bytes.fromhex("0001")):
        with pytest.raises(ValueError):
            parse_advertisement(raw)

def test_synthetic_family_signature():
    payload = bytes.fromhex("48464b4a") + bytes(22)
    raw = bytes([len(payload) + 1, 3]) + payload
    assert protocol_hints(raw) == ("zhimei_v1_family_candidate",)

def test_nonmatching_payload():
    assert protocol_hints(bytes.fromhex("02010603030a18")) == ()

def test_signature_does_not_verify_integrity():
    payload = bytes.fromhex("48464b4a") + bytes([255]) * 22
    assert protocol_hints(bytes([27, 3]) + payload) == ("zhimei_v1_family_candidate",)
