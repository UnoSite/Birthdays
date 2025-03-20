"""Config flow for the Birthdays integration."""

import logging
import voluptuous as vol
import datetime
import homeassistant.util.dt as dt_util
from homeassistant import config_entries
from homeassistant.core import callback
from .const import *

_LOGGER = logging.getLogger(__name__)

# Get the current year dynamically
CURRENT_YEAR = dt_util.now().year

class BirthdaysConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Birthdays integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the user setup step."""
        errors = {}

        if user_input is not None:
            _LOGGER.debug("User submitted data: %s", user_input)

            name = user_input.get(CONF_NAME, "").strip()
            if not name:
                errors["base"] = "missing_name"
                _LOGGER.warning("User attempted to submit an empty name.")

            # Validate year input (should be a 4-digit number up to CURRENT_YEAR)
            year_input = user_input.get(CONF_YEAR, "").strip()
            if not year_input.isdigit() or not (1000 <= int(year_input) <= CURRENT_YEAR):
                errors["base"] = "invalid_year"
                _LOGGER.error("Invalid year provided: %s", year_input)

            # Check for duplicate entries
            existing_entries = {
                entry.data.get(CONF_NAME, "").strip().lower()
                for entry in self._async_current_entries()
                if CONF_NAME in entry.data
            }
            if name.lower() in existing_entries:
                errors["base"] = "duplicate_entry"
                _LOGGER.warning("Duplicate entry detected for name: %s", name)

            # Validate the date
            try:
                datetime.date(
                    int(user_input[CONF_YEAR]), 
                    user_input[CONF_MONTH], 
                    user_input[CONF_DAY]
                )
            except (ValueError, TypeError) as e:
                errors["base"] = "invalid_date"
                _LOGGER.error("Invalid date provided (%s): %s", user_input, e)

            if not errors:
                user_input[CONF_YEAR] = int(user_input[CONF_YEAR])  # Ensure it is stored as an integer
                return self.async_create_entry(title=name, data=user_input)

        # Vis UI-formular til at indtaste fødselar
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_YEAR): str,  # Tekstfelt til årstal
                vol.Required(CONF_MONTH, default=1): vol.In(range(1, 13)),  # Dropdown
                vol.Required(CONF_DAY, default=1): vol.In(range(1, 32)),  # Dropdown
            }),
            errors=errors
        )

    async def async_step_reconfigure(self, user_input=None):
        """Allow reconfiguration of an existing entry."""
        return await self.async_step_user(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        return BirthdaysOptionsFlowHandler(config_entry)


class BirthdaysOptionsFlowHandler(config_entries.OptionsFlow):
    """Handles options for the Birthdays integration."""

    def __init__(self, config_entry):
        """Initialize the options flow handler."""
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            _LOGGER.debug("User updated data: %s", user_input)

            # Validate year input (should be a 4-digit number up to CURRENT_YEAR)
            year_input = user_input.get(CONF_YEAR, "").strip()
            if not year_input.isdigit() or not (1000 <= int(year_input) <= CURRENT_YEAR):
                errors["base"] = "invalid_year"
                _LOGGER.error("Invalid year provided: %s", year_input)

            # Validate the new date input
            try:
                datetime.date(
                    int(user_input[CONF_YEAR]), 
                    user_input[CONF_MONTH], 
                    user_input[CONF_DAY]
                )
            except (ValueError, TypeError) as e:
                errors["base"] = "invalid_date"
                _LOGGER.error("Invalid date provided (%s): %s", user_input, e)

            if not errors:
                user_input[CONF_YEAR] = int(user_input[CONF_YEAR])  # Ensure it is stored as an integer
                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        # Hent de nuværende værdier fra config_entry
        current_config = self._config_entry.data

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME, default=current_config.get(CONF_NAME, "")): str,
                vol.Required(CONF_YEAR, default=str(current_config.get(CONF_YEAR, ""))): str,  # Tekstfelt til årstal
                vol.Required(CONF_MONTH, default=current_config.get(CONF_MONTH, 1)): vol.In(range(1, 13)),
                vol.Required(CONF_DAY, default=current_config.get(CONF_DAY, 1)): vol.In(range(1, 32)),
            }),
            errors=errors
                )
