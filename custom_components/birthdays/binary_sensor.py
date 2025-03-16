"""Binary sensor for the Birthdays integration.

This sensor checks if today is the birthday of the configured person.
It returns `on` if the birth date matches the current day and month.
"""

import logging
from datetime import datetime
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.device_registry import DeviceEntryType
from .const import *

# Set up logging
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the binary sensor platform.

    This function is called when a new instance of the integration is added.

    Args:
        hass: The Home Assistant instance.
        entry: The configuration entry containing the user data.
        async_add_entities: Function to register new entities.
    """
    _LOGGER.debug("Setting up binary sensor for entry: %s", entry.entry_id)
    
    config = entry.data
    async_add_entities([BirthdayBinarySensor(config, entry.entry_id)])

    _LOGGER.info("Binary sensor added for: %s", config[CONF_NAME])

class BirthdayBinarySensor(BinarySensorEntity):
    """Binary sensor indicating if today is the birthday."""

    def __init__(self, config, entry_id):
        """Initialize the binary sensor.

        Args:
            config (dict): Configuration data containing name, day, and month.
            entry_id (str): Unique ID of the integration instance.
        """
        self._name = f"birthdays_{config[CONF_NAME]}_today"
        self._config = config
        self._state = False
        self._attr_unique_id = f"{entry_id}_today"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=f"Birthday: {config[CONF_NAME]}",
            manufacturer="Birthdays Integration",
            model="Birthday Sensor",
            entry_type=DeviceEntryType.SERVICE,
        )

        _LOGGER.debug("Initialized BirthdayBinarySensor for: %s", config[CONF_NAME])
        self.update()

    def update(self):
        """Update binary sensor state.

        Checks if today matches the configured birthday and updates the state.
        """
        today = datetime.today()
        is_birthday = today.day == self._config[CONF_DAY] and today.month == self._config[CONF_MONTH]

        if is_birthday != self._state:
            _LOGGER.debug("State change for %s: %s -> %s", self._name, self._state, is_birthday)

        self._state = is_birthday

    @property
    def is_on(self):
        """Return True if today is the birthday."""
        return self._state

    @property
    def name(self):
        """Return the name of the entity."""
        return self._name
