"""Structural BLE AD parsing; signatures are hints, not device identity."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AdField:
    """One advertising data structure."""

    ad_type: int
    data: bytes


def parse_advertisement(raw: bytes) -> tuple[AdField, ...]:
    """Parse length/type/data fields, rejecting truncation or bad padding."""
    fields = []
    offset = 0
    while offset < len(raw):
        length = raw[offset]
        if length == 0:
            if any(raw[offset:]):
                raise ValueError("Nonzero data after advertising terminator")
            break
        end = offset + 1 + length
        if end > len(raw):
            raise ValueError("Truncated advertising field")
        fields.append(AdField(raw[offset + 1], raw[offset + 2:end]))
        offset = end
    return tuple(fields)


def protocol_hints(raw: bytes) -> tuple[str, ...]:
    """Recognize reference signatures only; do not decode or verify CRC.

    Layout references: NicoIIT/ha-ble-adv, zhimei.py and test_zhimei.py,
    commit 10fb6edac13930cc78a56811147aa8d262d49eb9.
    A match does NOT establish a fan, manufacturer, command or identity.
    """
    hints = []
    for field in parse_advertisement(raw):
        if field.ad_type == 0x03 and len(field.data) == 26 and field.data.startswith(bytes.fromhex("48464b4a")):
            hints.append("zhimei_v1_family_candidate")
        elif field.ad_type == 0xFF and field.data.startswith(bytes.fromhex("00000048464b4a")):
            hints.append("zhimei_v1b_family_candidate")
        elif field.ad_type == 0xFF and field.data.startswith(bytes.fromhex("48464b4a")):
            hints.append("zhimei_remote_v1_family_candidate")
    return tuple(dict.fromkeys(hints))
