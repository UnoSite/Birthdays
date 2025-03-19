"""Sensor platform for the Birthdays integration."""

import logging
import homeassistant.util.dt as dt_util
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import *

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the sensor platform."""
    config = entry.data
    name_slug = config[CONF_NAME].lower().replace(" ", "_")
    entry_id = entry.entry_id

    _LOGGER.debug("Setting up Birthday sensors for: %s", name_slug)

    async_add_entities([
        BirthdaySensor(config, entry_id, "next", "Next birthday in", ICON_NEXT_BIRTHDAY),
        BirthdaySensor(config, entry_id, "date", "Date of birth", ICON_DATE_OF_BIRTH),
        BirthdaySensor(config, entry_id, "years", "Number of years", ICON_YEARS_OLD),
    ], True)

    _LOGGER.info("Birthday sensors created for: %s", name_slug)

class BirthdaySensor(Entity):
    """Representation of a Birthday Sensor."""

    def __init__(self, config, entry_id, sensor_type, friendly_name, icon):
        """Initialize the sensor."""
        name = config[CONF_NAME]
        name_slug = name.lower().replace(" ", "_")

        self._attr_name = f"Birthday: {name} - {friendly_name}"
        self._attr_unique_id = f"{entry_id}_{sensor_type}"
        self.entity_id = f"sensor.birthdays_{name_slug}_{sensor_type}"
        self._attr_icon = icon
        self._sensor_type = sensor_type
        self._config = config
        self._attr_native_value = None
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=f"Birthday: {name}",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

        _LOGGER.debug("Initialized BirthdaySensor: %s (entity_id: %s)", self._attr_name, self.entity_id)

    async def async_update(self):
        """Update sensor state."""
        today = dt_util.now().date()
        birth_date = dt_util.parse_datetime(
            f"{self._config[CONF_YEAR]}-{self._config[CONF_MONTH]:02d}-{self._config[CONF_DAY]:02d}T00:00:00Z"
        ).date()

        if self._sensor_type == "next":
            next_birthday = birth_date.replace(year=today.year)
            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 1)
            self._attr_native_value = (next_birthday - today).days
            _LOGGER.debug("Next birthday for %s in %d days", self._config[CONF_NAME], self._attr_native_value)

        elif self._sensor_type == "date":
            self._attr_native_value = birth_date.strftime("%Y-%m-%d")

        elif self._sensor_type == "years":
            age = today.year - birth_date.year
            if (today.month, today.day) < (birth_date.month, birth_date.day):
                age -= 1
            self._attr_native_value = age
            _LOGGER.debug("%s is %d years old", self._config[CONF_NAME], self._attr_native_value)

        self.async_write_ha_state()
