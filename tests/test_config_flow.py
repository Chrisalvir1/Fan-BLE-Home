"""Tests for Fan BLE Home config flow."""
from unittest.mock import patch
import pytest

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.fan_ble_home.const import DOMAIN, CONF_SHARED_CODE, CONF_SERIAL_NUMBER

@pytest.fixture(autouse=True)
def auto_mock_bluetooth():
    """Mock bluetooth scanners to avoid error during setup if needed."""
    with patch("homeassistant.components.bluetooth.async_scanner_count", return_value=1):
        yield

async def test_form_valid_input_and_normalization(hass: HomeAssistant):
    """Test valid format, normalization, and optional serial."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"action": "manual"})
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Mock Fan",
            CONF_SHARED_CODE: " [010, 020, 030, 040, 050] ",
            CONF_SERIAL_NUMBER: " 99999 ",
        },
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Mock Fan"
    assert result2["data"] == {
        "name": "Mock Fan",
        CONF_SHARED_CODE: "10,20,30,40,50",
        CONF_SERIAL_NUMBER: "99999",
        "protocol_verified": False,
    }

async def test_form_invalid_code(hass: HomeAssistant):
    """Test we handle invalid shared code."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"action": "manual"})
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "Mock Fan",
            CONF_SHARED_CODE: "not,a,valid,code",
        },
    )
    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {CONF_SHARED_CODE: "invalid_code"}

async def test_form_empty_name(hass: HomeAssistant):
    """Test we handle empty name."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"action": "manual"})
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "   ",
            CONF_SHARED_CODE: "10,20,30,40,50",
        },
    )
    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"name": "invalid_name"}

async def test_form_duplicate(hass: HomeAssistant):
    """Test that duplicate shared codes are rejected."""
    # First entry directly via MockConfigEntry
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Mock Fan 1",
        data={
            "name": "Mock Fan 1",
            CONF_SHARED_CODE: "10,20,30,40,50",
            CONF_SERIAL_NUMBER: "",
            "protocol_verified": False,
        },
        unique_id="shared_code:10,20,30,40,50"
    )
    entry.add_to_hass(hass)

    # Second entry
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"action": "manual"})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"name": "Mock Fan 2", CONF_SHARED_CODE: "[010, 20, 30, 40, 50]"})
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"
