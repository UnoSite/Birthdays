"""Sensor platform for the Birthdays integration.

This module creates multiple sensors for tracking birthdays:
- `sensor.birthdays_{name}_next`: Days until the next birthday.
- `sensor.birthdays_{name}_date`: Birth date of the person.
- `sensor.birthdays_{name}_years`: Age of the person.
"""

import logging
from datetime import datetime
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import *

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the sensor platform.

    This function is called when a new instance of the integration is added.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The configuration entry with user data.
        async_add_entities (function): Function to register new entities.
    """
    config = entry.data
    name_slug = config[CONF_NAME].lower().replace(" ", "_")
    entry_id = entry.entry_id

    _LOGGER.debug("Setting up Birthday sensors for: %s", name_slug)

    async_add_entities([
        BirthdaySensor(config, entry_id, SENSOR_NAME_TEMPLATE.format(name=name_slug, sensor_type="next"), "Next birthday in", ICON_NEXT_BIRTHDAY),
        BirthdaySensor(config, entry_id, SENSOR_NAME_TEMPLATE.format(name=name_slug, sensor_type="date"), "Date of birth", ICON_DATE_OF_BIRTH),
        BirthdaySensor(config, entry_id, SENSOR_NAME_TEMPLATE.format(name=name_slug, sensor_type="years"), "Number of years", ICON_YEARS_OLD),
    ])

    _LOGGER.info("Birthday sensors created for: %s", name_slug)

class BirthdaySensor(Entity):
    """Representation of a Birthday Sensor."""

    def __init__(self, config, entry_id, entity_id, sensor_type, icon):
        """Initialize the sensor.

        Args:
            config (dict): Configuration data containing name, birth date details.
            entry_id (str): Unique ID of the integration instance.
            entity_id (str): Entity ID for the sensor.
            sensor_type (str): The type of sensor (Next birthday, Date of birth, etc.).
            icon (str): The icon for the sensor.
        """
        name = config[CONF_NAME]
        self._attr_name = f"Birthday: {name} - {sensor_type}"
        self._attr_unique_id = f"{entry_id}_{sensor_type.lower().replace(' ', '_')}"
        self.entity_id = entity_id
        self._attr_icon = icon
        self._sensor_type = sensor_type
        self._state = None
        self._config = config
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=f"Birthday: {name}",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

        _LOGGER.debug("Initialized BirthdaySensor: %s (entity_id: %s)", self._attr_name, self.entity_id)
        self.update()

    def update(self):
        """Update sensor state.

        This function calculates values based on the birth date.
        """
        birth_date = datetime(self._config[CONF_YEAR], self._config[CONF_MONTH], self._config[CONF_DAY])
        today = datetime.today()

        if self._sensor_type == "Next birthday in":
            next_birthday = datetime(today.year, birth_date.month, birth_date.day)
            if next_birthday < today:
                next_birthday = datetime(today.year + 1, birth_date.month, birth_date.day)
            self._state = (next_birthday - today).days
            _LOGGER.debug("Next birthday for %s in %d days", self._config[CONF_NAME], self._state)
        elif self._sensor_type == "Date of birth":
            self._state = birth_date.strftime("%Y-%m-%d")
        elif self._sensor_type == "Number of years":
            age = today.year - birth_date.year
            if (today.month, today.day) < (birth_date.month, birth_date.day):
                age -= 1
            self._state = age
            _LOGGER.debug("%s is %d years old", self._config[CONF_NAME], self._state)

    @property
    def state(self):
        """Return the current state of the sensor."""
        return self._state
