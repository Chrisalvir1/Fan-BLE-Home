"""Test init and services."""
from unittest.mock import patch, MagicMock
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import HomeAssistantError
from custom_components.fan_ble_home.const import DOMAIN
from pytest_homeassistant_custom_component.common import MockConfigEntry

async def test_setup_multiple_entries_and_unload(hass: HomeAssistant):
    """Test setup of multiple entries and selective unload."""
    entry1 = MockConfigEntry(domain=DOMAIN, data={"name": "test1"})
    entry1.add_to_hass(hass)
    entry2 = MockConfigEntry(domain=DOMAIN, data={"name": "test2"})
    entry2.add_to_hass(hass)
    
    # Setup first
    assert await hass.config_entries.async_setup(entry1.entry_id)
    assert hass.services.has_service(DOMAIN, "start_study")
    
    # Setup second
    assert await hass.config_entries.async_setup(entry2.entry_id)
    assert len(hass.data[DOMAIN]["entries"]) == 2
    
    # Unload first
    assert await hass.config_entries.async_unload(entry1.entry_id)
    assert entry1.state == ConfigEntryState.NOT_LOADED
    # Services should still exist
    assert hass.services.has_service(DOMAIN, "start_study")
    assert len(hass.data[DOMAIN]["entries"]) == 1
    
    # Unload second
    assert await hass.config_entries.async_unload(entry2.entry_id)
    assert entry2.state == ConfigEntryState.NOT_LOADED
    # Services should be removed
    assert not hass.services.has_service(DOMAIN, "start_study")
    assert DOMAIN not in hass.data

async def test_start_study_no_scanners(hass: HomeAssistant):
    """Test start_study service fails safely when no scanners are available."""
    entry = MockConfigEntry(domain=DOMAIN, data={"name": "test"})
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    
    with patch("homeassistant.components.bluetooth.async_current_scanners", return_value=[]):
        with pytest.raises(HomeAssistantError, match="No Bluetooth scanners are available"):
            await hass.services.async_call(DOMAIN, "start_study", {"duration": 10}, blocking=True)
