import voluptuous as vol
import datetime

from homeassistant import config_entries
from .const import *

CURRENT_YEAR = datetime.datetime.now().year

YEARS = list(range(CURRENT_YEAR, CURRENT_YEAR - 120, -1))
MONTHS = list(range(1, 13))
DAYS = list(range(1, 32))

class BirthdaysConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Birthdays."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle user step."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_YEAR): vol.In(YEARS),
                vol.Required(CONF_MONTH): vol.In(MONTHS),
                vol.Required(CONF_DAY): vol.In(DAYS),
            }),
            errors=errors
        )
