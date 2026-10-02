"""Redacted study diagnostics; no shared codes, serials or BLE payloads."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict:
    """Return bounded metadata without exposing stored control data."""
    data = hass.data.get(DOMAIN, {})
    study = data.get("study")
    
    # Safely redact config data
    redacted_data = {}
    for k, v in entry.data.items():
        if k in ["id", "seed", "index", "shared_code", "serial", "serial_number", "mac", "name"]:
            redacted_data[k] = "***REDACTED***"
        else:
            redacted_data[k] = v

    return {
        "protocol_verified": entry.data.get("verified", False),
        "control_supported": entry.data.get("verified", False),
        "config_data": redacted_data,
        "study": study.diagnostics() if study else {"active": False},
    }
