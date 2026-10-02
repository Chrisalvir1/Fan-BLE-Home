"""Redacted study diagnostics; no shared codes, serials or BLE payloads."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict:
    """Return bounded metadata without exposing stored control data."""
    data = hass.data.get(DOMAIN, {})
    study = data.get("study")
    return {
        "protocol_verified": False,
        "control_supported": False,
        "study": study.diagnostics() if study else {"active": False},
    }
