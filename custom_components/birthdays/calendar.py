"""Calendar entity for the Birthdays integration.

This calendar entity aggregates all birthdays into a single calendar.
The calendar is always 'on' and will include events for each birthday.
"""

import logging
from homeassistant.helpers.entity import Entity
from .const import *

# Set up logging
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the calendar platform.

    This function is called when a new instance of the integration is added.

    Args:
        hass: The Home Assistant instance.
        entry: The configuration entry containing the user data.
        async_add_entities: Function to register new entities.
    """
    _LOGGER.debug("Setting up calendar entity for Birthdays integration.")
    
    async_add_entities([BirthdaysCalendar()])

    _LOGGER.info("Birthdays calendar entity added: %s", CALENDAR_ENTITY_ID)

class BirthdaysCalendar(Entity):
    """Calendar for Birthdays."""

    def __init__(self):
        """Initialize the calendar entity."""
        self._name = CALENDAR_NAME
        self._entity_id = CALENDAR_ENTITY_ID

        _LOGGER.debug("Initialized BirthdaysCalendar with entity_id: %s", self._entity_id)

    @property
    def name(self):
        """Return the name of the calendar entity."""
        return self._name

    @property
    def state(self):
        """Return the state of the calendar.

        Since this is a static calendar containing all birthdays, it is always 'on'.
        """
        return "on"

    @property
    def unique_id(self):
        """Return a unique ID for the calendar entity."""
        return self._entity_id
