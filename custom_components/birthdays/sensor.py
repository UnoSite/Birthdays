"""Sensor platform for the Birthdays integration.

This module creates multiple sensors for tracking birthdays:
- `sensor.birthdays_{name}_next`: Days until the next birthday.
- `sensor.birthdays_{name}_date`: Birth date of the person.
- `sensor.birthdays_{name}_years`: Age of the person.
- `sensor.birthdays_{name}_days`: Number of days the person has lived.
"""

import logging
from datetime import datetime
from homeassistant.helpers.entity import Entity, DeviceInfo
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
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
    name = config[CONF_NAME].lower().replace(" ", "_")
    entry_id = entry.entry_id

    _LOGGER.debug("Setting up Birthday sensors for: %s", name)

    async_add_entities([
        BirthdaySensor(config, entry_id, f"{name}_next", "Next birthday in"),
        BirthdaySensor(config, entry_id, f"{name}_date", "Date of birth"),
        BirthdaySensor(config, entry_id, f"{name}_years", "Number of years"),
        BirthdaySensor(config, entry_id, f"{name}_days", "Number of days"),
    ])

    _LOGGER.info("Birthday sensors created for: %s", name)

class BirthdaySensor(Entity):
    """Representation of a Birthday Sensor."""

    def __init__(self, config, entry_id, entity_suffix, sensor_type):
        """Initialize the sensor.

        Args:
            config (dict): Configuration data containing name, birth date details.
            entry_id (str): Unique ID of the integration instance.
            entity_suffix (str): Suffix for the entity ID.
            sensor_type (str): The type of sensor (Next birthday, Date of birth, etc.).
        """
        self._name = f"birthdays_{config[CONF_NAME].lower().replace(' ', '_')}_{entity_suffix}"
        self._entity_id = f"sensor.birthdays_{config[CONF_NAME].lower().replace(' ', '_')}_{entity_suffix}"
        self._sensor_type = sensor_type
        self._state = None
        self._config = config
        self._attr_unique_id = f"{entry_id}_{entity_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=f"Birthday: {config[CONF_NAME]}",
            manufacturer="Birthdays Integration",
            model="Birthday Sensor",
            entry_type=DeviceEntryType.SERVICE,
        )

        _LOGGER.debug("Initialized BirthdaySensor: %s (%s)", self._name, sensor_type)

        self.update()

    def update(self):
        """Update sensor state.

        This function calculates values based on the birth date.
        """
        name = self._config[CONF_NAME]
        birth_date = datetime(self._config[CONF_YEAR], self._config[CONF_MONTH], self._config[CONF_DAY])
        today = datetime.today()

        if self._sensor_type == "Next birthday in":
            next_birthday = datetime(today.year, birth_date.month, birth_date.day)
            if next_birthday < today:
                next_birthday = datetime(today.year + 1, birth_date.month, birth_date.day)
            days_until = (next_birthday - today).days
            self._state = days_until
            _LOGGER.debug("Next birthday for %s in %d days", name, days_until)
        elif self._sensor_type == "Date of birth":
            self._state = birth_date.strftime("%Y-%m-%d")
        elif self._sensor_type == "Number of years":
            age = today.year - birth_date.year
            if (today.month, today.day) < (birth_date.month, birth_date.day):
                age -= 1  # Adjust if birthday hasn't occurred yet this year
            self._state = age
            _LOGGER.debug("%s is %d years old", name, age)
        elif self._sensor_type == "Number of days":
            days_lived = (today - birth_date).days
            self._state = days_lived
            _LOGGER.debug("%s has lived for %d days", name, days_lived)

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Birthday: {self._config[CONF_NAME]} - {self._sensor_type}"

    @property
    def state(self):
        """Return the current state of the sensor."""
        return self._state

    @property
    def entity_id(self):
        """Ensure entity_id is correctly formatted."""
        return self._entity_id
