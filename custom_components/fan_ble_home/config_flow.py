"""Configuration flow for experimental shared-code storage."""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_SERIAL_NUMBER, CONF_SHARED_CODE, DOMAIN
from .shared_code import parse_shared_code


class FanBleHomeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Store configuration without claiming verified device control."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
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
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_SHARED_CODE): str,
                vol.Optional(CONF_SERIAL_NUMBER): str,
            }),
            errors=errors,
        )
