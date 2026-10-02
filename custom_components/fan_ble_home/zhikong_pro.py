"""ZhiKong Pro (ZhiMei V1) Protocol Profile."""
import binascii
from typing import Any

from .protocol import ProtocolProfile, ActionType

# Constants and matrix adapted from ha-ble-adv (MIT License, Copyright 2024 NicoIIT)
# See THIRD_PARTY_NOTICES.md for details.
MATRIX = [29, 4, 17, 32, 152, 117, 40, 70, 11, 175, 67, 172, 214, 190, 137, 142]

class ZhiKongProProfile(ProtocolProfile):
    """Protocol profile for ZhiKong Pro (based on ZhiMei V1 structure)."""

    def _crc16(self, buffer: bytearray) -> int:
        return binascii.crc_hqx(buffer, 0)

    def _unapply_matrix(self, buffer: bytearray, key: int) -> bytearray:
        """Unapply xor pivot with Encoding Matrix."""
        if not buffer:
            return bytearray()
        pivot = ((buffer[0] - MATRIX[key & 0xF]) & 0xFF) ^ 0xFF
        return bytearray([((x - MATRIX[(key + i) & 0xF] + 256) % 256) ^ pivot for i, x in enumerate(buffer)])

    def _apply_matrix(self, buffer: bytearray, key: int) -> bytearray:
        """Apply xor pivot with Encoding Matrix."""
        if len(buffer) < 2:
            return bytearray()
        pivot = MATRIX[((buffer[1] >> 4) & 15) ^ (buffer[1] & 15)]
        return bytearray([(((x ^ pivot) + MATRIX[(key + i) & 0xF]) + 256) % 256 for i, x in enumerate(buffer)])

    def _decrypt(self, raw_bytes: bytes) -> bytearray | None:
        """Decrypt raw BLE packet. Minimal adaptation from ha-ble-adv."""
        # Typically a raw advertisement has AD structures. We assume raw_bytes contains the manufacturer data
        # Wait, the reference expects `buffer[self._header_start_pos:]`. The header is usually 0xFF + company ID.
        # Let's assume we search for the ZhiMei V1 signature directly in the unwhitened payload, or we just try to decrypt.
        # But `RawAdvertisementTransport` gives us the WHOLE packet or just the manufacturer data?
        # If it's just manufacturer data, the offset is 0. 
        # In ha-ble-adv, ZhiMei V1 header is 48 46 4b 4a.
        buffer = bytearray(raw_bytes)
        
        # Search for the header 48 46 4b 4a
        header = bytearray([0x48, 0x46, 0x4b, 0x4a])
        start_pos = buffer.find(header)
        if start_pos == -1:
            return None
            
        data = buffer[start_pos:]
        if len(data) < 16:
            return None
            
        decoded = self._unapply_matrix(data[4:], 6) # ha-ble-adv uses key=6 after header
        
        # Check CRC
        if len(decoded) >= 14:
            crc_calc = self._crc16(decoded[:-3])
            crc_rx = int.from_bytes(decoded[-2:], "little")
            if crc_calc == crc_rx:
                return decoded
        return None

    def can_decode(self, raw_bytes: bytes) -> str:
        if self._decrypt(raw_bytes) is not None:
            return "high"
        return "none"

    def decode(self, raw_bytes: bytes) -> ActionType:
        decoded = self._decrypt(raw_bytes)
        if not decoded:
            return ActionType.UNKNOWN
            
        # Extracted based on ha-ble-adv structure
        cmd_byte = decoded[7]
        arg0 = decoded[11]
        
        if cmd_byte == 0x01: # Toggle Light
            return ActionType.LIGHT_ON # Simple map for duplicate controller flow
        elif cmd_byte == 0x02: # Fan speed
            if arg0 == 1: return ActionType.SPEED_1
            if arg0 == 2: return ActionType.SPEED_2
            if arg0 == 3: return ActionType.SPEED_3
            if arg0 == 4: return ActionType.SPEED_4
            if arg0 == 5: return ActionType.SPEED_5
            if arg0 == 6: return ActionType.SPEED_6
            if arg0 == 0: return ActionType.FAN_OFF
        
        return ActionType.UNKNOWN

    def extract_config(self, raw_bytes: bytes) -> dict[str, Any]:
        decoded = self._decrypt(raw_bytes)
        if not decoded:
            return {}
        
        return {
            "id": int.from_bytes(decoded[3:7], "little"),
            "seed": decoded[1],
            "index": decoded[8]
        }

    def can_encode(self, config: dict[str, Any], action: ActionType) -> bool:
        return "id" in config

    def encode(self, config: dict[str, Any], action: ActionType) -> bytes | None:
        if not self.can_encode(config, action):
            return None
            
        # Simplified encode logic
        cmd_byte = 0x01
        arg0 = 0x00
        
        if action == ActionType.LIGHT_ON or action == ActionType.LIGHT_OFF:
            cmd_byte = 0x01
            arg0 = 0x01
        elif action == ActionType.FAN_OFF:
            cmd_byte = 0x02
            arg0 = 0x00
        elif action in [ActionType.SPEED_1, ActionType.SPEED_2, ActionType.SPEED_3]:
            cmd_byte = 0x02
            arg0 = int(action.value[-1])
            
        uid = config["id"].to_bytes(4, "little")
        seed = config.get("seed", 0x11)
        index = config.get("index", 0x22)
        
        # Build 14 byte readable buffer
        # In ha-ble-adv: [0] = 0xFF, [1] = seed, [2] = tx_count, [3:7] = uid, [7] = cmd, [8] = index, [9] = 0xFF, [10] = tx_count, [11:14] = args
        tx_count = 1
        decoded = bytearray([0xFF, seed, tx_count, uid[0], uid[1], uid[2], uid[3], cmd_byte, index, 0xFF, tx_count, arg0, 0x00, 0x00])
        
        # Encrypt
        buffer = decoded + self._crc16(decoded[:-1]).to_bytes(2, "little")
        buf_matrix = self._apply_matrix(buffer, 6)
        
        header = bytearray([0x48, 0x46, 0x4b, 0x4a])
        return header + buf_matrix

