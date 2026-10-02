"""Isolated parser tests; no Home Assistant or Bluetooth required."""

import importlib.util
from pathlib import Path
import sys
import unittest

PATH = Path(__file__).resolve().parents[1] / "custom_components" / "fan_ble_home" / "shared_code.py"
SPEC = importlib.util.spec_from_file_location("fan_ble_home_shared_code_test", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
parse_shared_code = MODULE.parse_shared_code


class SharedCodeTests(unittest.TestCase):
    def test_canonical(self):
        self.assertEqual(parse_shared_code("1,2,3,4,5").normalized, "1,2,3,4,5")

    def test_whitespace_and_brackets(self):
        self.assertEqual(parse_shared_code(" [001, 2, 3, 4, 005] ").values, (1, 2, 3, 4, 5))

    def test_byte_boundaries(self):
        self.assertEqual(parse_shared_code("0,255,0,255,0").values, (0, 255, 0, 255, 0))

    def test_reject_invalid_text(self):
        for text in ("", "1,2,3,4", "1,2,3,4,5,6", "1,2,3,4,256", "-1,2,3,4,5", "1.0,2,3,4,5", "1,2,3,4,x", "[1,2,3,4,5", "https://example.com", "1 2 3 4 5"):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    parse_shared_code(text)


if __name__ == "__main__":
    unittest.main()
