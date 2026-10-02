# Architecture

Fan BLE Home is structured as a standard Home Assistant custom component, prioritizing local-only, protocol-safe Bluetooth Low Energy communication without cloud dependencies.

## Design Philosophy

- **Local Only:** All interactions occur directly over BLE using Home Assistant's built-in Bluetooth API. No ESP32 is mandatory if the HA host has BLE.
- **Evidence-Based Integration:** Entities are not created unless their underlying BLE protocol behavior is known, mapped, and tested.
- **Privacy-First Diagnostics:** Internal diagnostics and study modes deliberately redact actual MAC addresses, shared codes, serials, and exact BLE payloads to prevent accidental leaks.
- **State Optimism:** Because many BLE fans do not report their state reliably, the integration depends on optimistic state updates.

## Component Structure

- `__init__.py`: Handles integration setup, lifecycle, and shared resources like the study mode.
- `config_flow.py`: Accepts manual shared-code imports, ensuring no duplicate codes exist.
- `shared_code.py`: A strict structural parser for user-entered shared codes.
- `study.py`: An active observer that buffers BLE advertisements without assuming device identity.
- `advertisement.py`: Parser and protocol-hint generator for BLE manufacturer and service data.
- `diagnostics.py`: Safely exports metadata for debugging without exposing secrets.

## Extensibility

In the future, a `protocol/` module will handle the parsing, decoding, and encoding of different BLE fan families (e.g., ZhiKong Pro, FanLamp Pro).
