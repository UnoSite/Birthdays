"""Calendar entity for the Birthdays integration.

This calendar entity aggregates all birthdays into a single calendar.
The calendar is always 'on' and will include events for each birthday.
"""

import logging
import dataclasses
from datetime import datetime, timedelta
import homeassistant.util.dt as dt_util
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
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
    _LOGGER.debug("Setting up Birthdays Calendar entity.")

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

@dataclasses.dataclass
class BirthdayCalendarEvent:
    """Dataclass til Birthday Events (sikrer korrekt håndtering)."""
    summary: str
    start: datetime
    end: datetime

    def as_dict(self):
        """Konverterer til en dictionary."""
        return {
            "summary": self.summary,
            "start": self.start.isoformat(),
            "end": self.end.isoformat()
        }

class BirthdaysCalendar(CalendarEntity):
    """Calendar for Birthdays."""

    def __init__(self):
        """Initialize the calendar entity."""
        self._attr_name = CALENDAR_NAME
        self._attr_unique_id = CALENDAR_ENTITY_ID
        self._events = []

        _LOGGER.debug("Initialized BirthdaysCalendar.")

    @property
    def state(self):
        """Return the state of the calendar (always 'on')."""
        return "on"

    @property
    def event(self):
        """Return the next upcoming birthday event."""
        now = dt_util.now()
        upcoming_events = [event for event in self._events if event.start >= now]
        return min(upcoming_events, key=lambda x: x.start) if upcoming_events else None

    @property
    def extra_state_attributes(self):
        """Return state attributes for the calendar entity."""
        return {
            "events": [event.as_dict() for event in self._events]
        }

    async def async_get_events(self, hass, start_date, end_date):
        """Return events within a specific time range."""
        _LOGGER.debug("Fetching events between %s and %s", start_date, end_date)

        start_date = dt_util.as_utc(start_date)
        end_date = dt_util.as_utc(end_date)

        return [event.as_dict() for event in self._events if start_date <= event.start <= end_date]

    def add_event(self, name, year, month, day):
        """Add a birthday event to the calendar."""
        now = dt_util.now().astimezone()
        event_date = datetime(now.year, month, day, 0, 0, tzinfo=now.tzinfo)

        if event_date < now:
            event_date = datetime(now.year + 1, month, day, 0, 0, tzinfo=now.tzinfo)

        event = BirthdayCalendarEvent(
            summary=f"🎂 {name}'s Birthday",
            start=event_date,
            end=event_date + timedelta(days=1)
        )

        self._events.append(event)
        _LOGGER.info("Added birthday event: %s on %s", name, event.start.strftime("%Y-%m-%d"))
