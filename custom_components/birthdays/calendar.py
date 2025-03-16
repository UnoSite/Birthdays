from homeassistant.helpers.entity import Entity
from .const import *

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the calendar platform."""
    async_add_entities([BirthdaysCalendar()])

class BirthdaysCalendar(Entity):
    """Calendar for Birthdays."""

    def __init__(self):
        self._name = CALENDAR_NAME
        self._entity_id = CALENDAR_ENTITY_ID

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return "on"
