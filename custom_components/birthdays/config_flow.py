"""Config flow for the Birthdays integration.

This allows users to set up birthday tracking through Home Assistant's UI.
Users can configure multiple instances, each representing a different person's birthday.
"""

import logging
import voluptuous as vol
import datetime
from homeassistant import config_entries
from homeassistant.core import callback
from .const import *

# Set up logging
_LOGGER = logging.getLogger(__name__)

# Get the current year
CURRENT_YEAR = datetime.datetime.now().year

# Define selectable ranges for birth date input
YEARS = list(range(CURRENT_YEAR, CURRENT_YEAR - 120, -1))  # Last 120 years
MONTHS = list(range(1, 13))  # January - December
DAYS = list(range(1, 32))  # Days in a month

class BirthdaysConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Birthdays integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the user setup step.

        This step allows users to input:
        - Name of the birthday person
        - Year of birth
        - Month of birth
        - Day of birth

        If valid data is provided, an entry is created in Home Assistant.

        Args:
            user_input (dict, optional): User-provided input. Defaults to None.

        Returns:
            FlowResult: A form for user input or an entry creation.
        """
        errors = {}

        if user_input is not None:
            _LOGGER.debug("User submitted data: %s", user_input)

            name_cleaned = user_input[CONF_NAME].strip().lower()

            # Valider om fødselsdagen allerede eksisterer
            existing_entries = {entry.data[CONF_NAME].strip().lower() for entry in self._async_current_entries()}
            if name_cleaned in existing_entries:
                errors["base"] = "duplicate_entry"
                _LOGGER.warning("Duplicate entry detected for name: %s", user_input[CONF_NAME])

            # Valider, om datoen er gyldig
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
                vol.Required(CONF_YEAR): vol.In(YEARS),
                vol.Required(CONF_MONTH): vol.In(MONTHS),
                vol.Required(CONF_DAY): vol.In(DAYS),
            }),
            errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow handler."""
        return BirthdaysOptionsFlowHandler(config_entry)

class BirthdaysOptionsFlowHandler(config_entries.OptionsFlow):
    """Handles options for the Birthdays integration."""

    def __init__(self, config_entry):
        """Initialize the options flow handler."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return self.async_show_form(step_id="init")
