"""Tests for Fan BLE Home config flow."""
from unittest.mock import patch
import pytest

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from custom_components.fan_ble_home.const import DOMAIN, CONF_SHARED_CODE, CONF_SERIAL_NUMBER

@pytest.fixture(autouse=True)
def auto_mock_bluetooth():
    """Mock bluetooth scanners to avoid error during setup if needed."""
    with patch("homeassistant.components.bluetooth.async_current_scanners", return_value=["mock_scanner"]):
        yield

async def test_form_valid_input(hass):
    """Test we get the form and create an entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "My Fan",
            CONF_SHARED_CODE: "76, 176, 219, 111, 5",
            CONF_SERIAL_NUMBER: "12345",
        },
    )
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "My Fan"
    assert result2["data"] == {
        "name": "My Fan",
        CONF_SHARED_CODE: "76,176,219,111,5",
        CONF_SERIAL_NUMBER: "12345",
        "protocol_verified": False,
    }

async def test_form_invalid_code(hass):
    """Test we handle invalid shared code."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "name": "My Fan",
            CONF_SHARED_CODE: "invalid",
        },
    )
    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {CONF_SHARED_CODE: "invalid_code"}

async def test_form_duplicate(hass):
    """Test that duplicate shared codes are rejected."""
    # First entry
    await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER},
        data={"name": "Fan 1", CONF_SHARED_CODE: "1,2,3,4,5"}
    )
    # Second entry
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER},
        data={"name": "Fan 2", CONF_SHARED_CODE: "[001, 2, 3, 4, 5]"}
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"
