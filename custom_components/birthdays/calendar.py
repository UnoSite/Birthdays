"""Calendar entity for the Birthdays integration.

This calendar entity aggregates all birthdays into a single calendar.
The calendar is always 'on' and will include events for each birthday.
"""

import logging
from datetime import datetime
from homeassistant.components.calendar import CalendarEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.core import HomeAssistant
from .const import *

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up the calendar platform.

    This function is called when a new instance of the integration is added.

    Args:
        hass: The Home Assistant instance.
        entry: The configuration entry containing the user data.
        async_add_entities: Function to register new entities.
    """
    _LOGGER.debug("Setting up calendar entity for Birthdays integration.")

    # Sørg for kun at tilføje kalenderen én gang
    if CALENDAR_ENTITY_ID not in hass.data.setdefault(DOMAIN, {}):
        calendar = BirthdaysCalendar()
        hass.data[DOMAIN][CALENDAR_ENTITY_ID] = calendar
        async_add_entities([calendar])
        _LOGGER.info("Birthdays calendar entity added: %s", CALENDAR_ENTITY_ID)
    else:
        calendar = hass.data[DOMAIN][CALENDAR_ENTITY_ID]

    # Tilføj fødselsdagen til kalenderen
    calendar.add_event(
        name=entry.data[CONF_NAME],
        year=entry.data[CONF_YEAR],
        month=entry.data[CONF_MONTH],
        day=entry.data[CONF_DAY],
    )

class BirthdaysCalendar(CalendarEntity):
    """Calendar for Birthdays."""

    def __init__(self):
        """Initialize the calendar entity."""
        self._name = CALENDAR_NAME
        self._entity_id = CALENDAR_ENTITY_ID
        self._events = []
        self._attr_unique_id = CALENDAR_ENTITY_ID
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "birthdays_calendar")},
            name="Birthdays Calendar",
            manufacturer="Birthdays Integration",
            model="Calendar",
            entry_type=DeviceEntryType.SERVICE,
        )

        _LOGGER.debug("Initialized BirthdaysCalendar with entity_id: %s", self._entity_id)

    @property
    def name(self):
        """Return the name of the calendar entity."""
        return self._name

    @property
    def state(self):
        """Return the state of the calendar (always 'on')."""
        return "on"

    @property
    def unique_id(self):
        """Return a unique ID for the calendar entity."""
        return self._entity_id

    @property
    def event(self):
        """Return the next event in the calendar."""
        if not self._events:
            return None
        return min(self._events, key=lambda x: x["date"])

    def add_event(self, name, year, month, day):
        """Add a birthday event to the calendar.

        Args:
            name (str): Name of the person.
            year (int): Year of birth.
            month (int): Month of birth.
            day (int): Day of birth.
        """
        event_date = datetime(year=datetime.today().year, month=month, day=day)
        if event_date < datetime.today():
            event_date = datetime(year=datetime.today().year + 1, month=month, day=day)

        event = {
            "name": name,
            "date": event_date,
        }

        self._events.append(event)
        _LOGGER.info("Added birthday to calendar: %s on %s", name, event_date.strftime("%Y-%m-%d"))
