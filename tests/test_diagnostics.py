"""Tests for Fan BLE Home diagnostics."""
from unittest.mock import MagicMock
import pytest

from homeassistant.core import HomeAssistant
from custom_components.fan_ble_home.diagnostics import async_get_config_entry_diagnostics
from custom_components.fan_ble_home.const import DOMAIN

async def test_diagnostics(hass: HomeAssistant):
    """Test diagnostics export."""
    mock_entry = MagicMock()
    
    hass.data[DOMAIN] = {}
    mock_study = MagicMock()
    mock_study.diagnostics.return_value = {"mock_study": "data"}
    hass.data[DOMAIN]["study"] = mock_study
    
    diag = await async_get_config_entry_diagnostics(hass, mock_entry)
    assert diag["protocol_verified"] is False
    assert diag["control_supported"] is False
    assert diag["study"] == {"mock_study": "data"}

async def test_diagnostics_no_study(hass: HomeAssistant):
    """Test diagnostics when study isn't initialized."""
    mock_entry = MagicMock()
    diag = await async_get_config_entry_diagnostics(hass, mock_entry)
    assert diag["study"] == {"active": False}
