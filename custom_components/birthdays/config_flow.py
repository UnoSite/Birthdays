"""Config flow for the Birthdays integration.

This allows users to set up birthday tracking through Home Assistant's UI.
Users can configure multiple instances, each representing a different person's birthday.
"""

import logging
import voluptuous as vol
import datetime
from homeassistant import config_entries
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
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

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
