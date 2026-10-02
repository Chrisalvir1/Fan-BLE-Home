"""Tests for ensuring strict privacy in diagnostics."""
import pytest
from unittest.mock import patch, MagicMock
from homeassistant.core import HomeAssistant
from custom_components.fan_ble_home.diagnostics import async_get_config_entry_diagnostics
from custom_components.fan_ble_home.const import DOMAIN

async def test_diagnostics_redacts_secrets(hass: HomeAssistant):
    """Ensure ids, seeds, macs, etc. are redacted."""
    from homeassistant.config_entries import ConfigEntry
    entry = MagicMock(spec=ConfigEntry)
    entry.data = {
        "verified": True,
        "id": 123456,
        "seed": 0x11,
        "index": 0x22,
        "shared_code": "secret_code",
        "serial": "secret_serial",
        "mac": "AA:BB:CC:DD:EE:FF",
        "safe_value": "hello"
    }
    
    diag = await async_get_config_entry_diagnostics(hass, entry)
    
    assert diag["config_data"]["safe_value"] == "hello"
    for secret_key in ["id", "seed", "index", "shared_code", "serial", "mac"]:
        assert diag["config_data"][secret_key] == "***REDACTED***"
