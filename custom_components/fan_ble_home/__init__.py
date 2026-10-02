"""Experimental BLE fan study integration; no control entities yet."""

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .study import BleStudy


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Share a bounded study session across configuration entries."""
    data = hass.data.setdefault(DOMAIN, {})
    if "study" not in data:
        data["study"] = BleStudy(hass)
        data["entries"] = set()

        async def start(call: ServiceCall) -> None:
            from homeassistant.components import bluetooth

            if not bluetooth.async_current_scanners(hass):
                raise HomeAssistantError("No Bluetooth scanners are available")
            data["study"].start(call.data["duration"])

        async def stop(call: ServiceCall) -> None:
            data["study"].stop()

        hass.services.async_register(
            DOMAIN, "start_study", start,
            schema=vol.Schema({vol.Optional("duration", default=60): vol.All(vol.Coerce(int), vol.Range(min=10, max=300))}),
        )
        hass.services.async_register(DOMAIN, "stop_study", stop, schema=vol.Schema({}))
    data["entries"].add(entry.entry_id)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Release shared resources after the final entry is unloaded."""
    data = hass.data.get(DOMAIN)
    if data is not None:
        data["entries"].discard(entry.entry_id)
        if not data["entries"]:
            data["study"].stop()
            hass.services.async_remove(DOMAIN, "start_study")
            hass.services.async_remove(DOMAIN, "stop_study")
            hass.data.pop(DOMAIN)
    return True
