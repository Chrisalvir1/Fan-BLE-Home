"""Test init and services."""
from unittest.mock import patch, MagicMock
import pytest
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntryState
from custom_components.fan_ble_home.const import DOMAIN
from pytest_homeassistant_custom_component.common import MockConfigEntry

async def test_setup_unload_entry(hass: HomeAssistant):
    """Test setup and unload."""
    entry = MockConfigEntry(domain=DOMAIN, data={"name": "test"})
    entry.add_to_hass(hass)
    
    assert await hass.config_entries.async_setup(entry.entry_id)
    assert hass.data[DOMAIN]["entries"]
    assert hass.services.has_service(DOMAIN, "start_study")
    assert hass.services.has_service(DOMAIN, "stop_study")
    
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert entry.state == ConfigEntryState.NOT_LOADED
    assert not hass.services.has_service(DOMAIN, "start_study")
    assert DOMAIN not in hass.data
