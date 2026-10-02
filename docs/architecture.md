# Architecture

Fan BLE Home is designed to use the native Home Assistant Bluetooth stack.

## Phase 2: Passive Observation and Classification
In Phase 2, the integration implements a strictly passive study mode.

### 1. Metadata vs Raw
Home Assistant provides metadata natively (`manufacturer_data`, `service_data`). Sin embargo, full RAW advertisement bytes are not guaranteed on all adapters or HA OS setups.
- **MetadataCandidateFilter**: Triggers loosely on any data to keep research summaries active without needing raw bytes. Metadata may contain valid bytes, but these bytes do not equal the original native raw sequence.
- **RawAdvertisementAnalyzer**: Only triggers when raw bytes are natively available. If `raw` is not provided by the API, it is NOT invoked and Phase 2 can legitimately conclude that raw data is unavailable for that adapter. We NEVER synthesize or rebuild a raw packet by artificially merging metadata arrays.

### 2. Privacy, Limits and Filters
- **Pseudonymization**: Devices are aliased as `source_1`, `source_2`. Real MAC addresses are dropped immediately.
- **Memory Limits**: The internal buffer enforces a hard limit of 200 sources and 200 samples. Once exceeded, further entries are counted under `dropped_due_to_limits`.
- **Sensitivities**:
  - `strict`: Rejects anything not structurally matching a known candidate. If no raw native source is available and no metadata signature is validated, strict returns zero candidates.
  - `research`: Aggregates metadata for debugging but strips payloads. Unknown samples do not increase candidate counts.

### 3. Signatures Do Not Equal Identity
A detected structural signature (e.g., `ZhiMei v1`) DOES NOT mean a specific brand or model is found. It simply indicates the packet structure matches a family. This prevents false positive pairings and ensures the decoder will have the right schema.
