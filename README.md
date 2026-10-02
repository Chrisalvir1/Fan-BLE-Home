# Fan BLE Home

Home Assistant custom integration for local Bluetooth Low Energy ceiling fans and lights.

## Status

**Current phase:** `configuration_only` / `passive_observation`

Version 0.1.0-alpha.2 is a structural scaffold and study tool. It does **not** transmit BLE commands, decode barcode images, or create control entities (like fans, lights, or switches).

The current integration features:
- A config flow that stores a manually entered shared code and an optional physical serial number.
- A local bounded BLE study service to passively observe changed advertisements without claiming device control or logging sensitive payloads.

The project is currently researching ZhiKong Pro and Daminy-compatible protocols.

## Installation for development

Add this repository to HACS as an Integration custom repository, download it, restart Home Assistant and add Fan BLE Home under Settings > Devices & services. Manual installation: copy `custom_components/fan_ble_home` into your Home Assistant `custom_components` directory and restart.

## Architecture & Protocol Status

Please read the accompanying documentation for deep technical details:
- [docs/architecture.md](docs/architecture.md)
- [docs/protocol-status.md](docs/protocol-status.md)

## Privacy and Identity

Shared codes may grant control access. **Do not publish your real codes in issues or logs.** Physical serial numbers are optional and must never be hardcoded for every device.

## License

MIT for original code in this repository. Any future third-party code must retain its own license and required notices. This project is not affiliated with device or app manufacturers.
