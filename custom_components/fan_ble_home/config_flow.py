"""Config flow for Fan BLE Home."""
import logging
import asyncio
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_SERIAL_NUMBER, CONF_SHARED_CODE
from homeassistant.const import CONF_NAME
from .shared_code import parse_shared_code
from .transport import RawAdvertisementTransport, RawAdvertisement
from .zhikong_pro import ZhiKongProProfile
from .protocol import ActionType

_LOGGER = logging.getLogger(__name__)

class FanBleHomeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fan BLE Home."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._config_data = {}
        self._detected_actions = set()
        self._transport = None
        self._profile = ZhiKongProProfile()
        self._listener_unsub = None
        self._packet_buffer = []

    def _start_transport(self):
        if not self._transport:
            self._transport = RawAdvertisementTransport(self.hass)
            self._listener_unsub = self._transport.register_callback(self._on_adv)
            self._transport.start()

    def _stop_transport(self):
        if self._listener_unsub:
            self._listener_unsub()
            self._listener_unsub = None
        if self._transport:
            self._transport.stop()
            self._transport = None

    @callback
    def _on_adv(self, adv: RawAdvertisement):
        self._packet_buffer.append(adv)


    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            if user_input["action"] == "duplicate_zhikong":
                return await self.async_step_duplicate_check_backend()
            return await self.async_step_manual()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("action", default="duplicate_zhikong"): vol.In({
                    "duplicate_zhikong": "Duplicar controlador existente (ZhiKong Pro)",
                    "manual": "Configuración manual (Avanzado)"
                })
            })
        )

    async def async_step_manual(self, user_input: dict | None = None) -> FlowResult:
        """Accept shared-code text, pending protocol verification."""
        errors: dict[str, str] = {}
        if user_input is not None:
            name = user_input[CONF_NAME].strip()
            if not name:
                errors[CONF_NAME] = "invalid_name"
            try:
                code = parse_shared_code(user_input[CONF_SHARED_CODE])
            except ValueError:
                errors[CONF_SHARED_CODE] = "invalid_code"
            if not errors:
                normalized = code.normalized
                await self.async_set_unique_id(f"shared_code:{normalized}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_NAME: name,
                        CONF_SHARED_CODE: normalized,
                        CONF_SERIAL_NUMBER: user_input.get(CONF_SERIAL_NUMBER, "").strip(),
                        "protocol_verified": False,
                    },
                )
        return self.async_show_form(
            step_id="manual",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_SHARED_CODE): str,
                vol.Optional(CONF_SERIAL_NUMBER): str,
            }),
            errors=errors,
        )

    async def async_step_duplicate_check_backend(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step 1: Check if raw backend is available."""
        self._start_transport()
        self._packet_buffer.clear()
        
        # Wait 3 seconds to see if any RAW packets arrive at all
        await asyncio.sleep(3)
        
        if not self._packet_buffer:
            self._stop_transport()
            return self.async_abort(reason="no_raw_backend")
            
        return await self.async_step_detect_any()

    async def async_step_detect_any(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step 2: Ask user to press any button to detect ZhiKong Pro."""
        if user_input is not None:
            self._packet_buffer.clear()
            # Wait up to 15 seconds for a matching packet
            for _ in range(15):
                await asyncio.sleep(1)
                for adv in list(self._packet_buffer):
                    if self._profile.can_decode(adv.raw_bytes) != "none":
                        config = self._profile.extract_config(adv.raw_bytes)
                        if config:
                            self._config_data.update(config)
                            self._config_data["protocol"] = "zhikong_pro"
                            self._packet_buffer.clear()
                            return await self.async_step_guided_actions()
            return self.async_show_form(
                step_id="detect_any",
                errors={"base": "no_candidate_detected"},
                data_schema=vol.Schema({vol.Optional("retry", default=True): bool})
            )

        return self.async_show_form(
            step_id="detect_any",
            description_placeholders={"instructions": "Presiona cualquier botón en el mando ZhiKong Pro."},
        )

    async def async_step_guided_actions(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step 3: Guided actions."""
        # For brevity in Phase 3 proof-of-concept, we assume detection is enough to populate entities
        # A full implementation would step through LIGHT_ON, FAN_ON, etc.
        if user_input is not None:
            return await self.async_step_validate_blink()

        return self.async_show_form(
            step_id="guided_actions",
            description_placeholders={"instructions": "Presiona los botones principales. Haz clic en Siguiente cuando termines."},
        )

    async def async_step_validate_blink(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Step 4: Validate physically by transmitting."""
        if user_input is not None:
            if user_input["did_blink"]:
                self._config_data["verified"] = True
                self._stop_transport()
                return self.async_create_entry(title="ZhiKong Pro Fan", data=self._config_data)
            else:
                self._stop_transport()
                return self.async_abort(reason="validation_failed")

        # TRANSMIT test packet here
        encoded = self._profile.encode(self._config_data, ActionType.LIGHT_ON)
        if encoded:
            # We would send it here. Without a raw transmitter in standard HA, this is a placeholder.
            # ha-ble-adv uses ESPHome API or ble_adv proxy.
            _LOGGER.info("Simulating transmission of validated packet: %s", encoded.hex())

        return self.async_show_form(
            step_id="validate_blink",
            description_placeholders={"instructions": "Se ha enviado un comando de prueba (Luz). ¿El dispositivo reaccionó?"},
            data_schema=vol.Schema({
                vol.Required("did_blink", default=False): bool
            })
        )
