"""Tests for Fan BLE Home study logic."""
import asyncio
from unittest.mock import MagicMock, patch
import pytest

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from custom_components.fan_ble_home.study import BleStudy
from custom_components.fan_ble_home.const import DOMAIN

async def test_study_lifecycle_and_pseudonymization(hass: HomeAssistant):
    """Test start, receive (with pseudonymization and buffer limits), stop."""
    study = BleStudy(hass)
    assert not study.active
    
    with patch("homeassistant.components.bluetooth.async_register_callback") as mock_register:
        mock_unregister = MagicMock()
        mock_register.return_value = mock_unregister
        
        study.start(10)
        assert study.active
        assert study._timer is not None
        mock_register.assert_called_once()
        
        # Simulate receive over max buffer
        for i in range(250):
            mock_info = MagicMock()
            mock_info.address = f"AA:BB:CC:DD:EE:{i:02X}"
            mock_info.rssi = -60
            mock_info.manufacturer_data = {1: b'\x01\x02'}
            mock_info.service_data = {}
            study._receive(mock_info, None)
        
        # It should cap unique sources to 200
        assert len(study._addresses) == 200
        # It should cap samples to 200
        assert len(study.samples) == 200
        assert study.samples[0]["source_alias"] == "source_1"
        assert study.samples[-1]["source_alias"] == "source_200"
        
        # Stop
        timer = study._timer
        with patch.object(timer, "cancel") as mock_cancel:
            study.stop()
            assert not study.active
            mock_unregister.assert_called_once()
            mock_cancel.assert_called_once()
            assert study._timer is None

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
    
    diag_str = str(diag)
    assert "AA:BB:CC:DD:EE:FF" not in diag_str
    assert "abcd" not in diag_str
    
    sample = diag["samples"][0]
    assert sample["source_alias"] == "source_1"
    assert sample["manufacturer_lengths"] == {"1": 2}

async def test_study_start_exception(hass: HomeAssistant):
    """Ensure an exception during start doesn't leave study active incorrectly."""
    study = BleStudy(hass)
    with patch("homeassistant.components.bluetooth.async_register_callback", side_effect=Exception("Test Error")):
        with pytest.raises(Exception):
            study.start(10)
        assert not study.active
        assert study._timer is None
