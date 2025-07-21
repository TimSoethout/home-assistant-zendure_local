"""Config flow for Zendure Local integration."""

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_RESOURCE

from .const import DEFAULT_NAME, DEFAULT_RESOURCE, DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zendure Local."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

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
