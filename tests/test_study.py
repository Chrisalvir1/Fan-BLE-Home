"""Tests for Fan BLE Home study logic."""
import asyncio
from unittest.mock import MagicMock, patch
import pytest

from homeassistant.core import HomeAssistant
from custom_components.fan_ble_home.study import BleStudy
from custom_components.fan_ble_home.classifier import CandidateStatus, CandidateEvidence, Sensitivity

class MockInfo:
    def __init__(self, address, rssi, manufacturer_data, service_data):
        self.address = address
        self.rssi = rssi
        self.manufacturer_data = manufacturer_data
        self.service_data = service_data

@patch("homeassistant.components.bluetooth.async_register_callback")
@patch("homeassistant.components.bluetooth.async_scanner_count", return_value=1)
async def test_study_lifecycle_and_pseudonymization(mock_count, mock_register, hass: HomeAssistant):
    """Test start, receive (with pseudonymization and buffer limits), stop."""
    study = BleStudy(hass)
    assert not study.active
    
    mock_unregister = MagicMock()
    mock_register.return_value = mock_unregister
    
    study.start(10, sensitivity="research")
    assert study.active
    assert study._timer is not None
    mock_register.assert_called_once()
    
    # Simulate receive over max buffer
    for i in range(250):
        mock_info = MockInfo(
            address=f"AA:BB:CC:DD:EE:{i:02X}",
            rssi=-60,
            manufacturer_data={1: b'\x01\x02'},
            service_data={}
        )
        study._receive(mock_info, None)
    
    # In research mode, it accepts unknown.
    assert len(study._addresses) == 200
    assert len(study.samples) == 200
    assert study.samples[0]["source_alias"] == "source_1"
    assert study.samples[-1]["source_alias"] == "source_200"
    
    assert study.dropped_due_to_limits == 50
    assert study.candidates_count == 0  # Unknowns do not increase candidate count
    assert study.metadata_only_count == 250
    assert study.raw_available_count == 0
    
    # Stop
    study.stop()
    assert not study.active
    mock_unregister.assert_called_once()


@patch("homeassistant.components.bluetooth.async_register_callback")
@patch("homeassistant.components.bluetooth.async_scanner_count", return_value=1)
async def test_study_diagnostics_redaction(mock_count, mock_register, hass: HomeAssistant):
    """Ensure raw payload and MAC are not in diagnostics."""
    study = BleStudy(hass)
    study.start(10, sensitivity="research")
    
    mock_info = MockInfo(
        address="AA:BB:CC:DD:EE:FF",
        rssi=-52, # Will be rounded to -50
        manufacturer_data={1: b'\xab\xcd'},
        service_data={}
    )
    
    study._receive(mock_info, None)
    diag = study.diagnostics()
    study.stop()
    
    diag_str = str(diag)
    assert "AA:BB:CC:DD:EE:FF" not in diag_str
    assert "abcd" not in diag_str
    
    sample = diag["samples"][0]
    assert sample["source_alias"] == "source_1"
    assert sample["rssi_bucket"] == -50
    assert sample["manufacturer_lengths"] == {"1": 2}
    assert sample["raw_available"] is False


@patch("homeassistant.components.bluetooth.async_register_callback", side_effect=Exception("Test Error"))
@patch("homeassistant.components.bluetooth.async_scanner_count", return_value=1)
async def test_study_start_exception(mock_count, mock_register, hass: HomeAssistant):
    """Ensure an exception during start doesn't leave study active incorrectly."""
    study = BleStudy(hass)
    with pytest.raises(Exception):
        study.start(10)
    assert not study.active
    assert study._timer is None


@patch("homeassistant.components.bluetooth.async_register_callback")
@patch("homeassistant.components.bluetooth.async_scanner_count", return_value=1)
async def test_strict_mode_filters(mock_count, mock_register, hass: HomeAssistant):
    """Test strict mode ignores unknowns (even if metadata contains header but no raw)."""
    study = BleStudy(hass)
    study.start(10, sensitivity="strict")
    
    # Metadata only, no raw
    mock_info_unknown = MockInfo(
        address="AA:BB:CC:DD:EE:11",
        rssi=-60,
        manufacturer_data={1: b'\x48\x46\x4B\x4A\x01'},
        service_data={}
    )
    
    study._receive(mock_info_unknown, None)
    study.stop()

    # Because strict mode drops non-candidates and we no longer mock raw, it should be empty
    assert len(study.samples) == 0
    assert study.candidates_count == 0
    assert study.unique_sources_seen == 0
    assert study.metadata_only_count == 1
    assert study.raw_available_count == 0


@patch("homeassistant.components.bluetooth.async_register_callback")
@patch("homeassistant.components.bluetooth.async_scanner_count", return_value=1)
async def test_raw_available_count_does_not_increase_without_native_raw(mock_count, mock_register, hass: HomeAssistant):
    """Ensure raw counts don't artificially inflate."""
    study = BleStudy(hass)
    study.start(10, sensitivity="research")
    
    mock_info = MockInfo(
        address="AA:BB:CC:DD:EE:FF",
        rssi=-50,
        manufacturer_data={1: b'\x48\x46\x4B\x4A'},
        service_data={}
    )
    
    study._receive(mock_info, None)
    study.stop()
    
    assert study.raw_available_count == 0
    assert study.metadata_only_count == 1
    assert study.candidates_count == 0
