"""Parse shared-code text without assuming protocol field meanings."""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class SharedCode:
    """Five numeric fields; their BLE protocol mapping is unverified."""

    values: tuple[int, ...]

    @property
    def normalized(self) -> str:
        """Return canonical comma-separated text."""
        return ",".join(str(value) for value in self.values)


def parse_shared_code(raw: str) -> SharedCode:
    """Accept comma-separated decimal fields with optional brackets.

    This parser handles text only, not barcode/QR images. Values are
    provisionally limited to byte range; parsing does not verify pairing,
    physical identity, capabilities, or the BLE protocol.
    """
    text = raw.strip()
    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1].strip()
    if not re.fullmatch(r"[0-9]{1,3}(?:\s*,\s*[0-9]{1,3}){4}", text):
        raise ValueError("Expected five comma-separated decimal values")
    values = tuple(int(part.strip()) for part in text.split(","))
    if any(value > 255 for value in values):
        raise ValueError("Values must be in the provisional byte range 0-255")
    return SharedCode(values)
