# Fan BLE Home

This integration provides local, push-based control over Bluetooth Low Energy (BLE) ceiling fans and lights.
**Current Status: EXPERIMENTAL PASSIVE STUDY PHASE (Phase 2).**

## Features (Phase 2)
- **Passive BLE Study**: Safely scan and classify BLE advertisements from Home Assistant.
- **Candidate Detection**: Identifies known structural signatures (e.g., ZhiMei v1).
- **Privacy First**: No raw MACs, names, or payloads are exposed.
- **No Transmission**: Completely passive; it does not alter or pair with any devices.

## Installation
1. Install via HACS as a custom repository.
2. Restart Home Assistant.
3. Add the integration from the Settings -> Devices & Services menu.

## Disclaimer
**No control entities (fan, light) are created in this phase.** This is explicitly a foundational passive scanning tool to verify structural candidates before decoders are implemented.
