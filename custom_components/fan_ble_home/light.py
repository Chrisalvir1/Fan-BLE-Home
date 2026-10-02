"""Light platform for Fan BLE Home."""
import logging
from homeassistant.components.light import LightEntity, ColorMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .transport import RawAdvertisementTransport, RawAdvertisement
from .zhikong_pro import ZhiKongProProfile
from .protocol import ActionType

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up the light platform."""
    if entry.data.get("verified"):
        async_add_entities([ZhiKongProLight(hass, entry)])

class ZhiKongProLight(LightEntity):
    """Light entity for ZhiKong Pro."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the light."""
        self.hass = hass
        self._entry = entry
        self._attr_name = f"{entry.title} Light"
        self._attr_unique_id = f"{entry.entry_id}_light"
        self._attr_supported_color_modes = {ColorMode.ONOFF}
        self._attr_color_mode = ColorMode.ONOFF
        self._is_on = False
        self._profile = ZhiKongProProfile()
        self._transport = RawAdvertisementTransport(hass)
        self._listener_unsub = None
        self._last_transmitted_hex = None

    async def async_added_to_hass(self) -> None:
        self._listener_unsub = self._transport.register_callback(self._on_adv)
        self._transport.start()

    async def async_will_remove_from_hass(self) -> None:
        if self._listener_unsub:
            self._listener_unsub()
        self._transport.stop()

    @callback
    def _on_adv(self, adv: RawAdvertisement) -> None:
        if self._last_transmitted_hex and adv.raw_bytes.hex() == self._last_transmitted_hex:
            return

        action = self._profile.decode(adv.raw_bytes)
        config = self._profile.extract_config(adv.raw_bytes)
        
        if config.get("id") != self._entry.data.get("id"):
            return

        if action == ActionType.LIGHT_ON:
            self._is_on = True
            self.async_write_ha_state()
        elif action == ActionType.LIGHT_OFF:
            self._is_on = False
            self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        return self._is_on

    async def async_turn_on(self, **kwargs) -> None:
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._is_on = False
        self.async_write_ha_state()
