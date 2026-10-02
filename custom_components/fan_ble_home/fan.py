"""Fan platform for Fan BLE Home."""
import logging
from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .transport import RawAdvertisementTransport, RawAdvertisement
from .zhikong_pro import ZhiKongProProfile
from .protocol import ActionType

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the fan platform."""
    if entry.data.get("verified"):
        async_add_entities([ZhiKongProFan(hass, entry)])

class ZhiKongProFan(FanEntity):
    """Fan entity for ZhiKong Pro."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the fan."""
        self.hass = hass
        self._entry = entry
        self._attr_name = entry.title
        self._attr_unique_id = f"{entry.entry_id}_fan"
        self._attr_supported_features = FanEntityFeature.SET_SPEED
        self._is_on = False
        self._percentage = 0
        self._profile = ZhiKongProProfile()
        self._transport = RawAdvertisementTransport(hass)
        self._listener_unsub = None
        self._last_transmitted_hex = None

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        self._listener_unsub = self._transport.register_callback(self._on_adv)
        self._transport.start()

    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed."""
        if self._listener_unsub:
            self._listener_unsub()
        self._transport.stop()

    @callback
    def _on_adv(self, adv: RawAdvertisement) -> None:
        """Handle incoming raw advertisements to update state."""
        # Echo prevention
        if self._last_transmitted_hex and adv.raw_bytes.hex() == self._last_transmitted_hex:
            return

        action = self._profile.decode(adv.raw_bytes)
        config = self._profile.extract_config(adv.raw_bytes)
        
        # Match ID
        if config.get("id") != self._entry.data.get("id"):
            return

        if action == ActionType.FAN_ON:
            self._is_on = True
        elif action == ActionType.FAN_OFF:
            self._is_on = False
            self._percentage = 0
        elif action == ActionType.SPEED_1:
            self._is_on = True
            self._percentage = 16
        elif action == ActionType.SPEED_2:
            self._is_on = True
            self._percentage = 33
        elif action == ActionType.SPEED_3:
            self._is_on = True
            self._percentage = 50
        elif action == ActionType.SPEED_4:
            self._is_on = True
            self._percentage = 66
        elif action == ActionType.SPEED_5:
            self._is_on = True
            self._percentage = 83
        elif action == ActionType.SPEED_6:
            self._is_on = True
            self._percentage = 100

        if action != ActionType.UNKNOWN:
            self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        return self._is_on

    @property
    def percentage(self) -> int | None:
        return self._percentage

    async def async_turn_on(self, percentage: int | None = None, preset_mode: str | None = None, **kwargs) -> None:
        """Turn on the fan."""
        self._is_on = True
        if percentage is not None:
            self._percentage = percentage
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the fan."""
        self._is_on = False
        self._percentage = 0
        self.async_write_ha_state()
