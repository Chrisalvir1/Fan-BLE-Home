"""Tests for Fan BLE Home study logic."""
import asyncio
from unittest.mock import MagicMock, patch
import pytest

from homeassistant.core import HomeAssistant
from custom_components.fan_ble_home.study import BleStudy
from custom_components.fan_ble_home.const import DOMAIN
from custom_components.fan_ble_home import async_setup_entry, async_unload_entry
from homeassistant.config_entries import ConfigEntry

async def test_study_lifecycle(hass: HomeAssistant):
    """Test start, receive, stop lifecycle."""
    study = BleStudy(hass)
    assert not study.active
    
    with patch("homeassistant.components.bluetooth.async_register_callback") as mock_register:
        mock_unregister = MagicMock()
        mock_register.return_value = mock_unregister
        
        study.start(10)
        assert study.active
        mock_register.assert_called_once()
        
        # Simulate receive
        mock_info = MagicMock()
        mock_info.address = "AA:BB:CC:DD:EE:FF"
        mock_info.rssi = -60
        mock_info.manufacturer_data = {1: b'\x01\x02'}
        mock_info.service_data = {}
        
        study._receive(mock_info, None)
        assert study.received == 1
        assert len(study.samples) == 1
        assert study.samples[0]["source_alias"] == "source_1"
        assert study.samples[0]["manufacturer_data"] == {"1": "0102"}
        
        study.stop()
        assert not study.active
        mock_unregister.assert_called_once()

async def test_study_diagnostics_redaction(hass: HomeAssistant):
    """Ensure raw payload and MAC are not in diagnostics."""
    study = BleStudy(hass)
    study.active = True
    
    mock_info = MagicMock()
    mock_info.address = "AA:BB:CC:DD:EE:FF"
    mock_info.rssi = -50
    mock_info.manufacturer_data = {1: b'\xab\xcd'}
    mock_info.service_data = {}
    
    study._receive(mock_info, None)
    
    diag = study.diagnostics()
    assert "AA:BB:CC:DD:EE:FF" not in str(diag)
    assert "abcd" not in str(diag)
    
    sample = diag["samples"][0]
    assert sample["source_alias"] == "source_1"
    assert sample["manufacturer_lengths"] == {"1": 2}
