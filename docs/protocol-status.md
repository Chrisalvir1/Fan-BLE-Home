# Protocol Status

The integration categorizes support into formal states:

1. **configuration_only:** Parses user configuration but makes no BLE connections.
2. **passive_observation:** Listens to BLE advertisements but doesn't decode controls.
3. **candidate_detection:** Detects possible matching fans based on known BLE structural hints.
4. **protocol_decoded:** Accurately decodes incoming and outgoing control commands without physical verification.
5. **control_tested:** Tested successfully on a limited subset of devices.
6. **control_verified:** Confirmed working securely with optimistic state and checksums fully validated.

**Current integration state:** `configuration_only` / `passive_observation`.

## Target Protocols

### ZhiKong Pro (Daminy & Compatible)
- **Status:** Under research.
- **Goal:** Primary initial target. The shared code format is a tuple of 5 bytes.

### ZhiMei / Smart Light
- **Status:** Planned protocol profile.
- **Notes:** Contains multiple variants (v1, v1b, vr0, vr1) which must be uniquely identified.

### FanLamp Pro
- **Status:** Planned protocol profile.
- **Notes:** Kept entirely separate from ZhiKong Pro to avoid protocol collision.
