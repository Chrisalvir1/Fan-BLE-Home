"""Transport layer for Raw BLE Advertising."""
import logging
from dataclasses import dataclass
import time
from collections.abc import Callable

from homeassistant.core import HomeAssistant, callback
from homeassistant.components.bluetooth import async_register_callback, BluetoothScanningMode, BluetoothServiceInfoBleak

_LOGGER = logging.getLogger(__name__)

@dataclass
class RawAdvertisement:
    """Ephemeral structure for raw BLE bytes. No secrets, MACs, or identifiable data."""
    source_alias: str
    timestamp: float
    rssi: int
    proxy_id: str
    raw_bytes: bytes


class RawAdvertisementTransport:
    """Independent transport for accessing Raw BLE data."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the transport."""
        self.hass = hass
        self._callbacks: list[Callable[[RawAdvertisement], None]] = []
        self._cancel_ha_callback = None
        self._source_map: dict[str, str] = {}
        self._source_counter = 0

    def get_source_alias(self, address: str) -> str:
        """Pseudonymize source."""
        if address not in self._source_map:
            self._source_counter += 1
            self._source_map[address] = f"source_{self._source_counter}"
        return self._source_map[address]

    def register_callback(self, callback_fn: Callable[[RawAdvertisement], None]) -> Callable[[], None]:
        """Register a callback for raw advertisements."""
        self._callbacks.append(callback_fn)
        def remove():
            if callback_fn in self._callbacks:
                self._callbacks.remove(callback_fn)
        return remove

    def start(self) -> None:
        """Start listening to raw BLE advertisements."""
        if self._cancel_ha_callback:
            return

        @callback
        def _ha_callback(service_info: BluetoothServiceInfoBleak, change: any) -> None:
            raw_payload = None
            if hasattr(service_info, "raw_advertisement"):
                raw_payload = getattr(service_info, "raw_advertisement")
            elif hasattr(service_info, "device") and hasattr(service_info.device, "details"):
                details = service_info.device.details
                if isinstance(details, dict) and "props" in details:
                    props = details["props"]
                    if isinstance(props, dict) and "ManufacturerData" in props:
                        raw_payload = props["ManufacturerData"]
            
            if not raw_payload:
                return

            # Normalize raw_payload
            if isinstance(raw_payload, dict):
                # Concatenate the dict values or extract the specific AD types if needed
                # For simplicity, if it's BlueZ, it might give a dict of {company_id: bytes}
                # But true raw advertising is a flat bytes object.
                # Actually BlueZ manufacturer data is not the full raw packet. 
                # If we only have manufacturer data, it's NOT the raw packet. 
                # Let's strictly require a bytes object.
                pass
            
            if isinstance(raw_payload, bytes):
                adv = RawAdvertisement(
                    source_alias=self.get_source_alias(service_info.address),
                    timestamp=time.monotonic(),
                    rssi=service_info.rssi,
                    proxy_id=service_info.source,
                    raw_bytes=raw_payload,
                )
                for cb in self._callbacks:
                    try:
                        cb(adv)
                    except Exception as err:
                        _LOGGER.debug("Error in raw callback: %s", err)

        try:
            self._cancel_ha_callback = async_register_callback(
                self.hass,
                _ha_callback,
                {"connectable": False},
                BluetoothScanningMode.PASSIVE
            )
        except Exception as e:
            _LOGGER.error("Failed to register raw BLE callback: %s", e)

    def stop(self) -> None:
        """Stop listening and clear buffers."""
        if self._cancel_ha_callback:
            self._cancel_ha_callback()
            self._cancel_ha_callback = None
        self._source_map.clear()
        self._source_counter = 0
        self._callbacks.clear()
