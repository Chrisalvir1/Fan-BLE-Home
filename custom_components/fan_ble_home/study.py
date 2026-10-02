"""Bounded in-memory BLE observation; no protocol or identity claims."""

import asyncio
from collections import deque
from datetime import datetime, timezone

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant, callback


class BleStudy:
    """Collect changed advertisements, not a lossless raw radio capture."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.samples = deque(maxlen=200)
        self._unsubscribe = None
        self._timer = None
        self.active = False
        self.received = 0
        self._addresses = {}

    @callback
    def stop(self) -> None:
        """Release subscription and timeout."""
        if self._unsubscribe is not None:
            self._unsubscribe()
            self._unsubscribe = None
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        self.active = False

    @callback
    def start(self, duration: int) -> None:
        """Listen for at most five minutes using HA's shared stack."""
        self.stop()
        self.samples.clear()
        self._addresses.clear()
        self.received = 0
        self.active = True
        self._unsubscribe = bluetooth.async_register_callback(
            self.hass,
            self._receive,
            {"connectable": False},
            bluetooth.BluetoothScanningMode.PASSIVE,
        )
        self._timer = asyncio.get_running_loop().call_later(duration, self.stop)

    @callback
    def _receive(self, info, change) -> None:
        """Keep structured data locally; never log payloads or addresses."""
        if not self.active:
            return
        manufacturer = {str(key): bytes(value).hex() for key, value in info.manufacturer_data.items()}
        service = {str(key): bytes(value).hex() for key, value in info.service_data.items()}
        if not manufacturer and not service:
            return
        if info.address not in self._addresses:
            if len(self._addresses) >= 200:
                return
            self._addresses[info.address] = f"source_{len(self._addresses) + 1}"
        self.received += 1
        self.samples.append({
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "source_alias": self._addresses[info.address],
            "rssi": info.rssi,
            "manufacturer_data": manufacturer,
            "service_data": service,
            "classification": "unverified",
        })

    def diagnostics(self) -> dict:
        """Export metadata only; omit payloads and physical addresses."""
        return {
            "active": self.active,
            "received_callbacks": self.received,
            "retained_samples": len(self.samples),
            "decoder_status": "not_implemented",
            "capture_scope": "HA changed-advertisement callbacks; may include cached replay and merged data",
            "samples": [{
                "observed_at": sample["observed_at"],
                "source_alias": sample["source_alias"],
                "rssi": sample["rssi"],
                "manufacturer_lengths": {key: len(value) // 2 for key, value in sample["manufacturer_data"].items()},
                "service_lengths": {key: len(value) // 2 for key, value in sample["service_data"].items()},
                "classification": sample["classification"],
            } for sample in self.samples],
        }
