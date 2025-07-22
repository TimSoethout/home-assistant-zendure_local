"""Config flow for Zendure Local integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME, CONF_RESOURCE

from .const import DEFAULT_NAME, DEFAULT_RESOURCE, DOMAIN


class ZendureLocalConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zendure Local."""

    VERSION = 1
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Check for existing entries with the same resource to prevent duplicates
            self._async_abort_entries_match({CONF_RESOURCE: user_input[CONF_RESOURCE]})

            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                    vol.Required(CONF_RESOURCE, default=DEFAULT_RESOURCE): str,
                }
            ),
            errors=errors,
        )
