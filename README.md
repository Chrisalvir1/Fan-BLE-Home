# Fan BLE Home

Experimental Home Assistant custom integration for local BLE fans and lights.

## Status

Version 0.1.0-alpha.1 is a configuration scaffold, not a working fan controller. It does not transmit BLE commands, discover fans, decode barcode images or create control entities.

The initial config flow stores a manually entered shared code and an optional physical serial number. The meaning of the shared-code fields is not yet verified. Importing a code does not prove successful pairing or control.

## Installation for development

Add this repository to HACS as an Integration custom repository, download it, restart Home Assistant and add Fan BLE Home under Settings > Devices & services. Manual installation: copy custom_components/fan_ble_home into your Home Assistant custom_components directory and restart.

## Roadmap

- Validate ZhiKong-compatible shared-code mapping against captured BLE commands.
- Implement local BLE transmission using supported host adapters, including Raspberry Pi 5 where available.
- Add listening-based discovery; do not assume a receiving-only fan broadcasts its identity.
- Implement verified fan/light capabilities and explicit optimistic-state handling.
- Add QR/barcode image import after determining supported payload formats.
- Study FanLamp Pro separately.

## Privacy and identity

Shared codes may grant control access. Do not publish your real codes in issues or logs. Physical serial numbers are optional and must never be hardcoded for every device. A shared code may identify a controller or group rather than a unique physical fan; this remains under investigation.

## License

MIT for original code in this repository. Any future third-party code must retain its own license and required notices. This project is not affiliated with device or app manufacturers.
