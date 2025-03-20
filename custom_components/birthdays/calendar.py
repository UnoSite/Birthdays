"""Calendar entity for the Birthdays integration."""

import logging
from datetime import datetime, timedelta
import homeassistant.util.dt as dt_util
from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from .const import *

_LOGGER = logging.getLogger(__name__)

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

    try:
        year = int(entry.data[CONF_YEAR])
        month = int(entry.data[CONF_MONTH])
        day = int(entry.data[CONF_DAY])
        name = entry.data[CONF_NAME]

        calendar.add_event(
            entry_id=entry.entry_id,
            name=name,
            year=year,
            month=month,
            day=day,
        )
    except (KeyError, ValueError, TypeError) as e:
        _LOGGER.error("Skipping event addition. Entry data missing or invalid: %s (%s)", entry.entry_id, e)


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
            event
            for event_list in self._events.values()
            for event in event_list
            if isinstance(event, CalendarEvent) and event.start_datetime_local >= now
        ]
        return min(upcoming_events, key=lambda x: x.start_datetime_local) if upcoming_events else None

    @property
    def extra_state_attributes(self):
        """Return state attributes for the calendar entity."""
        return {
            "events": [
                {
                    "summary": event.summary,
                    "start_time": event.start_datetime_local.isoformat(),
                    "end_time": event.end_datetime_local.isoformat(),
                    "all_day": event.all_day,
                }
                for event_list in self._events.values()
                for event in event_list
                if isinstance(event, CalendarEvent)
            ]
        }

    async def async_get_events(self, hass, start_date, end_date):
        """Return events within a specific time range."""
        _LOGGER.debug("Fetching events between %s and %s", start_date, end_date)

        start_date = dt_util.as_utc(start_date)
        end_date = dt_util.as_utc(end_date)

        return [
            {
                "summary": event.summary,
                "start_time": event.start_datetime_local.isoformat(),
                "end_time": event.end_datetime_local.isoformat(),
                "all_day": event.all_day,
            }
            for event_list in self._events.values()
            for event in event_list
            if isinstance(event, CalendarEvent) and start_date <= event.start_datetime_local <= end_date
        ]

    def add_event(self, entry_id, name, year, month, day):
        """Add or update a birthday event in the calendar."""
        now = dt_util.now().astimezone()
        event_date = datetime(now.year, month, day, 0, 0, tzinfo=now.tzinfo)

        if event_date < now:
            event_date = datetime(now.year + 1, month, day, 0, 0, tzinfo=now.tzinfo)

        age = event_date.year - year

        try:
            event = CalendarEvent(
                summary=f"🎂 {name} turns {age}",
                start_datetime_local=event_date,
                end_datetime_local=event_date + timedelta(days=1) - timedelta(seconds=1),
                all_day=True
            )

            if isinstance(event, CalendarEvent):
                self._events[entry_id] = [event]
                _LOGGER.info("Added/updated birthday event: %s (turning %d) on %s", name, age, event.start_datetime_local.strftime("%Y-%m-%d"))
            else:
                raise ValueError("Event creation failed")
        except Exception as e:
            _LOGGER.error("Failed to create CalendarEvent for %s: %s", name, e)

    async def remove_event(self, hass, entry_id):
        """Remove events related to a deleted birthday instance."""
        if entry_id in self._events:
            del self._events[entry_id]
            _LOGGER.info("Removed birthday events for entry: %s", entry_id)
        else:
            _LOGGER.warning("Tried to remove non-existing event for entry: %s", entry_id)

        if not self._events:
            _LOGGER.info("All birthdays removed, removing Birthdays calendar.")
            await self._remove_calendar(hass)

    async def _remove_calendar(self, hass):
        """Remove the Birthdays calendar entity when the last birthday is deleted."""
        entity_registry = async_get_entity_registry(hass)
        calendar_entity = entity_registry.async_get(CALENDAR_ENTITY_ID)

        if calendar_entity:
            entity_registry.async_remove(calendar_entity.entity_id)
            _LOGGER.info("Birthdays calendar entity removed.")
        else:
            _LOGGER.warning("Tried to remove non-existing Birthdays calendar entity.")
