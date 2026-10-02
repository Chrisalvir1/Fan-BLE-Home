"""Tests of structure and hints, not real fan compatibility."""

import importlib.util
from pathlib import Path
import sys
import unittest

PATH = Path(__file__).resolve().parents[1] / "custom_components" / "fan_ble_home" / "advertisement.py"
SPEC = importlib.util.spec_from_file_location("fan_ble_home_ad_test", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class AdvertisementTests(unittest.TestCase):
    def test_fields(self):
        fields = MODULE.parse_advertisement(bytes.fromhex("02010603030a18"))
        self.assertEqual([(x.ad_type, x.data.hex()) for x in fields], [(1, "06"), (3, "0a18")])

    def test_zero_padding(self):
        self.assertEqual(len(MODULE.parse_advertisement(bytes.fromhex("0201060000"))), 1)

    def test_invalid(self):
        for raw in (bytes.fromhex("02"), bytes.fromhex("030106"), bytes.fromhex("0001")):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    MODULE.parse_advertisement(raw)

    def test_synthetic_family_signature(self):
        payload = bytes.fromhex("48464b4a") + bytes(22)
        raw = bytes([len(payload) + 1, 3]) + payload
        self.assertEqual(MODULE.protocol_hints(raw), ("zhimei_v1_family_candidate",))

    def test_nonmatching_payload(self):
        self.assertEqual(MODULE.protocol_hints(bytes.fromhex("02010603030a18")), ())

    def test_signature_does_not_verify_integrity(self):
        payload = bytes.fromhex("48464b4a") + bytes([255]) * 22
        self.assertEqual(MODULE.protocol_hints(bytes([27, 3]) + payload), ("zhimei_v1_family_candidate",))


if __name__ == "__main__":
    unittest.main()
