"""Bounded in-memory BLE observation; no protocol or identity claims."""

import asyncio
from collections import deque
from datetime import datetime, timezone
import logging

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant, callback

from .classifier import CandidateClassifier, Sensitivity, CandidateStatus

_LOGGER = logging.getLogger(__name__)


class BleStudy:
    """Collect changed advertisements, strictly limited and pseudonymized."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.samples = deque(maxlen=200)
        self._unsubscribe = None
        self._timer = None
        self.active = False
        self.received = 0
        self.dropped_due_to_limits = 0
        self.sensitivity = Sensitivity.STRICT
        self.stopped_reason = "manual"
        self.started_at = None
        self.ended_at = None
        
        self._addresses = {}
        self._candidate_counts_by_type = {}
        self.unique_sources_seen = 0
        self.candidates_count = 0
        self.raw_available_count = 0
        self.metadata_only_count = 0

    @callback
    def stop(self, reason: str = "manual") -> None:
        """Release subscription and timeout."""
        if self._unsubscribe is not None:
            self._unsubscribe()
            self._unsubscribe = None
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None
        if self.active:
            self.ended_at = datetime.now(timezone.utc).isoformat()
            self.stopped_reason = reason
        self.active = False

    @callback
    def start(self, duration: int, sensitivity: str = Sensitivity.STRICT.value) -> None:
        """Listen for a bounded time using HA's shared stack."""
        self.stop("restarted")
        self.samples.clear()
        self._addresses.clear()
        self._candidate_counts_by_type.clear()
        self.received = 0
        self.dropped_due_to_limits = 0
        self.unique_sources_seen = 0
        self.candidates_count = 0
        self.raw_available_count = 0
        self.metadata_only_count = 0
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.ended_at = None
        
        try:
            self.sensitivity = Sensitivity(sensitivity)
        except ValueError:
            self.sensitivity = Sensitivity.STRICT

        self._unsubscribe = bluetooth.async_register_callback(
            self.hass,
            self._receive,
            {"connectable": False},
            bluetooth.BluetoothScanningMode.PASSIVE,
        )
        self.active = True
        self._timer = self.hass.loop.call_later(duration, lambda: self.stop("timeout"))

    @callback
    def _receive(self, info, change) -> None:
        """Keep structured data locally; never log payloads or physical addresses."""
        if not self.active:
            return
        
        self.received += 1
        
        # Round RSSI to multiple of 5
        rssi_bucket = round(info.rssi / 5) * 5
        
        manufacturer = {str(key): bytes(value).hex() for key, value in info.manufacturer_data.items()}
        service = {str(key): bytes(value).hex() for key, value in info.service_data.items()}
        
        # Attempt to find true raw bytes if explicitly exposed natively by HA
        # We strictly do not reconstruct or synthesize them from metadata
        raw_payload = None
        
        # Depending on the adapter or HA version, raw may be passed. Usually it is not.
        if hasattr(info, "raw_advertisement"):
            raw_payload = getattr(info, "raw_advertisement")
        elif hasattr(info, "device") and hasattr(info.device, "details"):
            details = info.device.details
            if isinstance(details, dict) and "props" in details:
                # Some backends might expose it
                pass
                
        classification = CandidateClassifier.process(
            info.manufacturer_data, 
            info.service_data, 
            raw_payload
        )
        
        is_candidate = classification["status"] != CandidateStatus.UNKNOWN.value
        
        if classification["raw_available"]:
            self.raw_available_count += 1
        else:
            self.metadata_only_count += 1
            
        if self.sensitivity == Sensitivity.STRICT and not is_candidate:
            return
            
        if info.address not in self._addresses:
            if len(self._addresses) >= 200:
                self.dropped_due_to_limits += 1
                return
            self._addresses[info.address] = f"source_{len(self._addresses) + 1}"
            self.unique_sources_seen += 1
            
        source_alias = self._addresses[info.address]
        
        if is_candidate:
            self.candidates_count += 1
            c_type = classification["candidate_type"]
            self._candidate_counts_by_type[c_type] = self._candidate_counts_by_type.get(c_type, 0) + 1

        if len(self.samples) >= 200:
            self.dropped_due_to_limits += 1
            
        self.samples.append({
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "source_alias": source_alias,
            "rssi_bucket": rssi_bucket,
            "evidence": classification["evidence"],
            "candidate_type": classification["candidate_type"],
            "status": classification["status"],
            "confidence": classification["confidence"],
            "raw_available": classification["raw_available"],
            "explanation": classification["explanation"],
            "manufacturer_lengths": {key: len(value) // 2 for key, value in manufacturer.items()},
            "service_lengths": {key: len(value) // 2 for key, value in service.items()},
        })

    def diagnostics(self) -> dict:
        """Export redacted metadata summary only."""
        return {
            "session_active": self.active,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "sensitivity": self.sensitivity.value,
            "scanner_count": bluetooth.async_scanner_count(self.hass, connectable=False),
            "total_callbacks": self.received,
            "unique_sources_seen": self.unique_sources_seen,
            "candidates_count": self.candidates_count,
            "candidate_counts_by_type": self._candidate_counts_by_type,
            "raw_available_count": self.raw_available_count,
            "metadata_only_count": self.metadata_only_count,
            "dropped_due_to_limits": self.dropped_due_to_limits,
            "stopped_reason": self.stopped_reason,
            "samples": list(self.samples),
        }
