# Protocol Status

## Evidence States
- `unknown`: No signature matched.
- `candidate`: Metadata hints at a match, but no raw confirmation.
- `candidate_with_known_signature`: Structural header confirmed in raw payload. (Max state in Phase 2)
- `decoded_unverified`: Not implemented yet.
- `code_matched`: Not implemented yet.
- `control_tested`: Not implemented yet.
- `control_verified`: Not implemented yet.

## Supported Families
- **ZhiMei v1 / fan v1**: `structural candidate detection only` (Phase 2 capability).
- **ZhiKong Pro**: `research only` (No formal candidate signature applied natively yet beyond shared base).
- **FanLamp Pro**: `not started`.
