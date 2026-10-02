"""Experimental BLE fan study integration; no control entities yet."""

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .study import BleStudy
from .classifier import Sensitivity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Share a bounded study session across configuration entries."""
    data = hass.data.setdefault(DOMAIN, {})
    if "study" not in data:
        data["study"] = BleStudy(hass)
        data["entries"] = set()

        async def start(call: ServiceCall) -> None:
            from homeassistant.components import bluetooth

            if bluetooth.async_scanner_count(hass, connectable=False) == 0:
                raise HomeAssistantError("No Bluetooth scanners are available")
            
            duration = call.data.get("duration", 60)
            sensitivity = call.data.get("sensitivity", Sensitivity.STRICT.value)
            
            data["study"].start(duration, sensitivity)

        async def stop(call: ServiceCall) -> None:
            data["study"].stop("manual")

        hass.services.async_register(
            DOMAIN, "start_study", start,
            schema=vol.Schema({
                vol.Optional("duration", default=60): vol.All(vol.Coerce(int), vol.Range(min=10, max=300)),
                vol.Optional("sensitivity", default=Sensitivity.STRICT.value): vol.In([Sensitivity.STRICT.value, Sensitivity.RESEARCH.value])
            }),
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
            data["study"].stop("reload")
            hass.services.async_remove(DOMAIN, "start_study")
            hass.services.async_remove(DOMAIN, "stop_study")
            hass.data.pop(DOMAIN)
    return True
