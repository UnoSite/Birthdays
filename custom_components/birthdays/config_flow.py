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

# Define selectable ranges for birth date input
YEARS = list(range(CURRENT_YEAR, CURRENT_YEAR - 120, -1))  # Last 120 years
MONTHS = list(range(1, 13))  # January - December
DAYS = list(range(1, 32))  # Days in a month

class BirthdaysConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Birthdays integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the user setup step."""
        errors = {}

        # Hvis ingen kalender findes, opret en standard Birthdays instans
        existing_calendars = [
            entry for entry in self._async_current_entries() if entry.title == "Birthdays"
        ]
        if not existing_calendars:
            return self.async_create_entry(
                title="Birthdays",
                data={},
            )

        if user_input is not None:
            _LOGGER.debug("User submitted data: %s", user_input)

            name_cleaned = user_input[CONF_NAME].strip().lower()

            # Check for duplicate entries
            existing_entries = {entry.data[CONF_NAME].strip().lower() for entry in self._async_current_entries()}
            if name_cleaned in existing_entries:
                errors["base"] = "duplicate_entry"
                _LOGGER.warning("Duplicate entry detected for name: %s", user_input[CONF_NAME])

            # Validate the date
            try:
                datetime.date(user_input[CONF_YEAR], user_input[CONF_MONTH], user_input[CONF_DAY])
            except ValueError:
                errors["base"] = "invalid_date"
                _LOGGER.error("Invalid date provided: %s-%s-%s", user_input[CONF_YEAR], user_input[CONF_MONTH], user_input[CONF_DAY])

            if not errors:
                return self.async_create_entry(title=user_input[CONF_NAME].strip(), data=user_input)

        # Show the form for user input
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_YEAR, default=CURRENT_YEAR): vol.In(YEARS),
                vol.Required(CONF_MONTH, default=1): vol.In(MONTHS),
                vol.Required(CONF_DAY, default=1): vol.In(DAYS),
            }),
            errors=errors
        )

    async def async_step_reconfigure(self, user_input=None):
        """Allow reconfiguration of an existing entry."""
        return await self.async_step_init(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        return BirthdaysOptionsFlowHandler(config_entry)

class BirthdaysOptionsFlowHandler(config_entries.OptionsFlow):
    """Handles options for the Birthdays integration."""

    def __init__(self, config_entry):
        """Initialize the options flow handler."""
        super().__init__()
        self._config_entry = config_entry  # Korrekt reference til config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            _LOGGER.debug("User updated data: %s", user_input)

            # Validate the new date input
            try:
                datetime.date(user_input[CONF_YEAR], user_input[CONF_MONTH], user_input[CONF_DAY])
            except ValueError:
                errors["base"] = "invalid_date"
                _LOGGER.error("Invalid date provided: %s-%s-%s", user_input[CONF_YEAR], user_input[CONF_MONTH], user_input[CONF_DAY])

            if not errors:
                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        # Hent de nuværende værdier fra config_entry
        current_config = self._config_entry.data

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_NAME, default=current_config.get(CONF_NAME, "")): str,
                vol.Required(CONF_YEAR, default=current_config.get(CONF_YEAR, CURRENT_YEAR)): vol.In(YEARS),
                vol.Required(CONF_MONTH, default=current_config.get(CONF_MONTH, 1)): vol.In(MONTHS),
                vol.Required(CONF_DAY, default=current_config.get(CONF_DAY, 1)): vol.In(DAYS),
            }),
            errors=errors
                )
