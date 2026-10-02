# Protocol research status

## Verified project status

Shared-code parsing and temporary HA advertisement observation are implemented. No fan control, command decoding or shared-code-to-controller mapping is implemented. No physical fan compatibility has been verified for this project.

## Reference layouts

Source inspected: NicoIIT/ha-ble-adv at commit 10fb6edac13930cc78a56811147aa8d262d49eb9, custom_components/ble_adv/codecs/zhimei.py and tests/codecs/test_zhimei.py.

The reference declares zhimei_fan_v1 with header 48 46 4B 4A and AD type 0x03. Related light and fan codecs share the header. It declares remote v1 with type 0xFF and related header, and v1b with a leading 00 00 00 header prefix. A header alone cannot distinguish a fan from a light, verify a packet, identify a physical device or prove ZhiKong compatibility.

## Current capture limitation

study.py retains manufacturer_data and service_data from HA discovery callbacks, not complete raw AD fields. Type 0x03 represents a UUID-list field, so the current stored fields do not cover every reference format. advertisement.py is an independent raw-data parser and is NOT connected to study.py yet. A verified raw-data acquisition path is required before using it for classification. Do not reconstruct arbitrary raw packets from merged HA metadata and claim they were captured on air.

## Required next stages

1. Verify the raw-data acquisition API on the supported HA version.
2. Implement decoding and integrity checks against reference vectors.
3. Distinguish app and remote protocol variants.
4. Establish the meaning of the shared code without guessing byte order or roles.
5. Add transmission and capabilities only after those stages.

No MAC address, RSSI, label serial or matching header is sufficient physical identity evidence. FanLamp Pro requires a separate codec family. Diagnostic exports currently exclude payloads and cannot serve as full protocol capture files.
