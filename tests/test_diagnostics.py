"""Tests for Fan BLE Home diagnostics."""
from unittest.mock import MagicMock
import pytest

from homeassistant.core import HomeAssistant
from custom_components.fan_ble_home.diagnostics import async_get_config_entry_diagnostics
from custom_components.fan_ble_home.const import DOMAIN
from pytest_homeassistant_custom_component.common import MockConfigEntry

async def test_diagnostics_redaction(hass: HomeAssistant):
    """Test diagnostics export doesn't leak secrets."""
    mock_entry = MockConfigEntry(
        domain=DOMAIN,
        title="My Secret Fan",
        data={
            "name": "My Secret Fan",
            "shared_code": "1,2,3,4,5",
            "serial_number": "SECRET_SERIAL",
            "protocol_verified": False,
        }
    )
    mock_entry.add_to_hass(hass)
    
    hass.data[DOMAIN] = {}
    mock_study = MagicMock()
    mock_study.diagnostics.return_value = {"active": True, "samples": []}
    hass.data[DOMAIN]["study"] = mock_study
    
    diag = await async_get_config_entry_diagnostics(hass, mock_entry)
    
    diag_str = str(diag)
    assert "1,2,3,4,5" not in diag_str
    assert "SECRET_SERIAL" not in diag_str
    assert "My Secret Fan" not in diag_str
    assert diag["protocol_verified"] is False
    assert diag["control_supported"] is False
    assert diag["study"] == {"active": True, "samples": []}

async def test_diagnostics_no_study(hass: HomeAssistant):
    """Test diagnostics when study isn't initialized."""
    mock_entry = MockConfigEntry(domain=DOMAIN, data={})
    diag = await async_get_config_entry_diagnostics(hass, mock_entry)
    assert diag["study"] == {"active": False}
