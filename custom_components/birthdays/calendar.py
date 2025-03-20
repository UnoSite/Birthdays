"""Calendar entity for the Birthdays integration."""

import logging
from datetime import datetime, timedelta
import homeassistant.util.dt as dt_util
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from dataclasses import asdict, dataclass
from .const import *

_LOGGER = logging.getLogger(__name__)

@dataclass
class BirthdayCalendarEvent:
    """Dataclass to ensure correct structure for CalendarEvent."""
    summary: str
    start: datetime
    end: datetime

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    """Set up the calendar platform."""
    _LOGGER.debug("Setting up Birthdays Calendar entity.")

    if CALENDAR_ENTITY_ID not in hass.data.setdefault(DOMAIN, {}):
        calendar = BirthdaysCalendar(hass)
        hass.data[DOMAIN][CALENDAR_ENTITY_ID] = calendar
        async_add_entities([calendar])
        _LOGGER.info("Birthdays calendar entity added: %s", CALENDAR_ENTITY_ID)
    else:
        calendar = hass.data[DOMAIN][CALENDAR_ENTITY_ID]

    # Tjek om nødvendige data er til stede før tilføjelse af fødselsdag
    required_keys = [CONF_NAME, CONF_YEAR, CONF_MONTH, CONF_DAY]
    if all(key in entry.data for key in required_keys):
        calendar.add_event(
            entry_id=entry.entry_id,
            name=entry.data[CONF_NAME],
            year=entry.data[CONF_YEAR],
            month=entry.data[CONF_MONTH],
            day=entry.data[CONF_DAY],
        )
    else:
        _LOGGER.error("Skipping event addition. Entry data missing required fields: %s", entry.entry_id)

class BirthdaysCalendar(CalendarEntity):
    """Calendar for Birthdays."""

    def __init__(self, hass):
        """Initialize the calendar entity."""
        self.hass = hass
        self._attr_name = CALENDAR_NAME
        self._attr_unique_id = CALENDAR_ENTITY_ID
        self._events = {}

        _LOGGER.debug("Initialized BirthdaysCalendar.")

    @property
    def state(self):
        """Return the state of the calendar (always 'on')."""
        return "on"

    @property
    def event(self):
        """Return the next upcoming birthday event."""
        now = dt_util.now()
        upcoming_events = [
            event for event_list in self._events.values() for event in event_list if event.start >= now
        ]
        return min(upcoming_events, key=lambda x: x.start) if upcoming_events else None

    @property
    def extra_state_attributes(self):
        """Return state attributes for the calendar entity."""
        return {
            "events": [asdict(event) for event_list in self._events.values() for event in event_list]
        }

    async def async_get_events(self, hass, start_date, end_date):
        """Return events within a specific time range."""
        _LOGGER.debug("Fetching events between %s and %s", start_date, end_date)

        start_date = dt_util.as_utc(start_date)
        end_date = dt_util.as_utc(end_date)

        return [
            asdict(event)
            for event_list in self._events.values() for event in event_list
            if start_date <= event.start <= end_date
        ]

    def add_event(self, entry_id, name, year, month, day):
        """Add or update a birthday event in the calendar."""
        now = dt_util.now().astimezone()
        event_date = datetime(now.year, month, day, 0, 0, tzinfo=now.tzinfo)

        # Hvis fødselsdagen allerede er passeret i år, skub den til næste år
        if event_date < now:
            event_date = datetime(now.year + 1, month, day, 0, 0, tzinfo=now.tzinfo)

        # Beregn alderen, som personen fylder på deres næste fødselsdag
        age = event_date.year - year

        event = BirthdayCalendarEvent(
            summary=f"🎂 {name} turns {age}",
            start=event_date,
            end=event_date + timedelta(days=1) - timedelta(seconds=1),
        )

        # Opdater eller tilføj event for denne entry_id
        self._events[entry_id] = [event]

        _LOGGER.info("Added/updated birthday event: %s (turning %d) on %s", name, age, event.start.strftime("%Y-%m-%d"))

    async def remove_event(self, hass, entry_id):
        """Remove events related to a deleted birthday instance."""
        if entry_id in self._events:
            del self._events[entry_id]
            _LOGGER.info("Removed birthday events for entry: %s", entry_id)

        # Hvis der stadig er fødselsdage, behold kalenderen
        if self._events:
            return

        # Hvis ingen fødselsdage tilbage, fjern kalenderen
        _LOGGER.info("All birthdays removed, removing Birthdays calendar.")
        await self._remove_calendar(hass)

    async def _remove_calendar(self, hass):
        """Remove the Birthdays calendar entity when the last birthday is deleted."""
        entity_registry = async_get_entity_registry(hass)
        calendar_entity = entity_registry.async_get(CALENDAR_ENTITY_ID)

        if calendar_entity:
            entity_registry.async_remove(calendar_entity.entity_id)
            _LOGGER.info("Birthdays calendar entity removed.")
