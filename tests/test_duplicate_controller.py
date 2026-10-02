"""Tests for the Duplicate Controller flow and entities."""
import pytest
from unittest.mock import patch, MagicMock

from homeassistant.core import HomeAssistant
from custom_components.fan_ble_home.const import DOMAIN
from custom_components.fan_ble_home.transport import RawAdvertisement
from custom_components.fan_ble_home.zhikong_pro import ZhiKongProProfile
from custom_components.fan_ble_home.protocol import ActionType

@pytest.fixture
def mock_setup_entry():
    """Mock setting up a config entry."""
    with patch("custom_components.fan_ble_home.async_setup_entry", return_value=True) as mock_setup:
        yield mock_setup

async def test_backend_no_raw(hass: HomeAssistant):
    """Test when backend provides no raw data, the flow aborts."""
    from custom_components.fan_ble_home.config_flow import FanBleHomeConfigFlow
    flow = FanBleHomeConfigFlow()
    flow.hass = hass
    
    with patch("asyncio.sleep"):
        result = await flow.async_step_duplicate_check_backend()
    
    assert result["type"] == "abort"
    assert result["reason"] == "no_raw_backend"

async def test_backend_with_raw(hass: HomeAssistant):
    """Test when backend provides raw data."""
    from custom_components.fan_ble_home.config_flow import FanBleHomeConfigFlow
    flow = FanBleHomeConfigFlow()
    flow.hass = hass
    
    async def mock_sleep(*args):
        # simulate receiving a packet
        adv = RawAdvertisement(
            source_alias="source_1",
            timestamp=123.4,
            rssi=-50,
            proxy_id="hci0",
            raw_bytes=b"dummy_raw_bytes"
        )
        flow._on_adv(adv)

    with patch("asyncio.sleep", side_effect=mock_sleep):
        result = await flow.async_step_duplicate_check_backend()
    
    assert result["type"] == "form"
    assert result["step_id"] == "detect_any"

def test_zhikong_pro_decoder():
    """Test ZhiKong Pro decoder using legal fixture structure."""
    profile = ZhiKongProProfile()
    
    # A fake valid buffer mimicking ZhiMei V1 structure
    # Header: 48 46 4b 4a
    # Encrypted payload that decodes to valid CRC.
    # We can just test that invalid data returns 'none'
    assert profile.can_decode(b"random_data_without_header") == "none"
    assert profile.decode(b"random") == ActionType.UNKNOWN

    config = {"id": 1234, "seed": 0x11, "index": 0x22}
    
    # Check encode returns bytes with header
    encoded = profile.encode(config, ActionType.LIGHT_ON)
    assert encoded is not None
    assert encoded.startswith(b"\x48\x46\x4b\x4a")

async def test_config_flow_full_success(hass: HomeAssistant):
    """Test full flow ending in 'Yes' to blink."""
    from custom_components.fan_ble_home.config_flow import FanBleHomeConfigFlow
    flow = FanBleHomeConfigFlow()
    flow.hass = hass
    
    async def mock_sleep(*args):
        flow._packet_buffer.append(RawAdvertisement("s1", 1.0, -50, "hci0", b"\x48\x46\x4b\x4a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"))
        
    with patch("asyncio.sleep", side_effect=mock_sleep), \
         patch.object(ZhiKongProProfile, "can_decode", return_value="high"), \
         patch.object(ZhiKongProProfile, "extract_config", return_value={"id": 111}):
        result = await flow.async_step_detect_any({"ready": True})
    
    assert result["type"] == "form"
    assert result["step_id"] == "guided_actions"
    
    # guided
    result2 = await flow.async_step_guided_actions({"ready": True})
    assert result2["type"] == "form"
    assert result2["step_id"] == "validate_blink"
    
    # validate blink YES
    result3 = await flow.async_step_validate_blink({"did_blink": True})
    assert result3["type"] == "create_entry"
    assert result3["data"]["verified"] is True
    assert result3["data"]["id"] == 111

async def test_config_flow_full_abort_no_blink(hass: HomeAssistant):
    """Test full flow ending in 'No' to blink."""
    from custom_components.fan_ble_home.config_flow import FanBleHomeConfigFlow
    flow = FanBleHomeConfigFlow()
    flow.hass = hass
    
    result3 = await flow.async_step_validate_blink({"did_blink": False})
    assert result3["type"] == "abort"
    assert result3["reason"] == "validation_failed"

async def test_echo_loop_prevention_and_update(hass: HomeAssistant):
    """Test echo loop prevention in entity update."""
    from custom_components.fan_ble_home.fan import ZhiKongProFan
    from homeassistant.config_entries import ConfigEntry
    
    entry = MagicMock(spec=ConfigEntry)
    entry.data = {"verified": True, "id": 111}
    entry.entry_id = "test_123"
    entry.title = "Test Fan"
    
    fan = ZhiKongProFan(hass, entry)
    fan.entity_id = "fan.test_fan"
    
    # Simulate valid external adv
    adv1 = RawAdvertisement("s1", 1.0, -50, "hci0", b"external_bytes")
    
    with patch.object(ZhiKongProProfile, "decode", return_value=ActionType.FAN_ON), \
         patch.object(ZhiKongProProfile, "extract_config", return_value={"id": 111}):
        fan._on_adv(adv1)
        assert fan.is_on is True

    # Simulate internal echo
    fan._last_transmitted_hex = "010203"
    adv_echo = RawAdvertisement("s1", 1.0, -50, "hci0", bytes.fromhex("010203"))
    
    with patch.object(ZhiKongProProfile, "decode", return_value=ActionType.FAN_OFF):
        fan._on_adv(adv_echo)
        # Should still be ON because echo was ignored!
        assert fan.is_on is True
