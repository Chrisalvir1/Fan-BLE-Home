"""Protocol definitions for Fan BLE Home."""
from abc import ABC, abstractmethod
from typing import Any
import enum

class ActionType(enum.Enum):
    """Supported logical actions."""
    LIGHT_ON = "light_on"
    LIGHT_OFF = "light_off"
    FAN_ON = "fan_on"
    FAN_OFF = "fan_off"
    SPEED_1 = "speed_1"
    SPEED_2 = "speed_2"
    SPEED_3 = "speed_3"
    SPEED_4 = "speed_4"
    SPEED_5 = "speed_5"
    SPEED_6 = "speed_6"
    BRIGHTNESS_UP = "brightness_up"
    BRIGHTNESS_DOWN = "brightness_down"
    COLOR_TEMP_UP = "color_temp_up"
    COLOR_TEMP_DOWN = "color_temp_down"
    UNKNOWN = "unknown"


class ProtocolProfile(ABC):
    """Base profile for decoding and encoding raw BLE advertisements."""

    @abstractmethod
    def can_decode(self, raw_bytes: bytes) -> str:
        """Return confidence level ('high', 'medium', 'low', 'none')."""

    @abstractmethod
    def decode(self, raw_bytes: bytes) -> ActionType:
        """Decode raw bytes into an observed action."""

    @abstractmethod
    def can_encode(self, config: dict[str, Any], action: ActionType) -> bool:
        """Return True if this profile can encode the given action with the config."""

    @abstractmethod
    def encode(self, config: dict[str, Any], action: ActionType) -> bytes | None:
        """Encode an action into raw BLE bytes. Return None if unable."""

    @abstractmethod
    def extract_config(self, raw_bytes: bytes) -> dict[str, Any]:
        """Extract reproducible config secrets from a raw packet."""
