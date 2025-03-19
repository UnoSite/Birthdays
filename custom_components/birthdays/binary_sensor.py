"""Binary sensor for the Birthdays integration.

This sensor checks if today is the birthday of the configured person.
It returns `on` if the birth date matches the current day and month.
"""

import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.entity import DeviceInfo
import homeassistant.util.dt as dt_util
from .const import *

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

    # Tjek om nødvendige data er til stede
    required_keys = [CONF_NAME, CONF_YEAR, CONF_MONTH, CONF_DAY]
    if not all(key in config for key in required_keys):
        _LOGGER.error("Missing required data in entry %s: %s", entry.entry_id, config)
        return

    sensor = BirthdayBinarySensor(config, entry.entry_id)
    async_add_entities([sensor], True)  # True for at kalde update med det samme

    _LOGGER.info("Binary sensor added for: %s", config.get(CONF_NAME, "Unknown"))


class BirthdayBinarySensor(BinarySensorEntity):
    """Binary sensor indicating if today is the birthday."""

    should_poll = False  # Home Assistant skal ikke poll'e denne sensor

    def __init__(self, config, entry_id):
        """Initialize the binary sensor.

        Args:
            config (dict): Configuration data containing name, day, and month.
            entry_id (str): Unique ID of the integration instance.
        """
        self._config = config

        # Tjek om nødvendige data er til stede
        required_keys = [CONF_NAME, CONF_YEAR, CONF_MONTH, CONF_DAY]
        if not all(key in config for key in required_keys):
            _LOGGER.error("Missing required data in binary sensor configuration: %s", config)
            self._attr_name = "Unknown Birthday Sensor"
            self._state = False
            return

        name = config[CONF_NAME]
        name_slug = name.lower().replace(" ", "_")

        self._attr_name = f"Birthday: {name}"
        self._attr_unique_id = f"{entry_id}_today"
        self.entity_id = BINARY_SENSOR_NAME_TEMPLATE.format(name=name_slug)
        self._attr_icon = ICON_BINARY_SENSOR
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=f"Birthday: {name}",
            manufacturer=MANUFACTURER,
            model=MODEL,
        )
        self._state = False

        _LOGGER.debug("Initialized BirthdayBinarySensor: %s (entity_id: %s)", self._attr_name, self.entity_id)

    async def async_update(self):
        """Update binary sensor state.

        Checks if today matches the configured birthday and updates the state.
        """
        today = dt_util.now().date()

        # Tjek om nødvendige datooplysninger er til stede
        required_keys = [CONF_YEAR, CONF_MONTH, CONF_DAY]
        if not all(key in self._config for key in required_keys):
            _LOGGER.error("Missing date information in binary sensor configuration: %s", self._config)
            return

        is_birthday = today.day == self._config[CONF_DAY] and today.month == self._config[CONF_MONTH]

        if is_birthday != self._state:
            _LOGGER.debug("State change for %s: %s -> %s", self._attr_name, self._state, is_birthday)
            self._state = is_birthday
            self.async_write_ha_state()

    @property
    def is_on(self):
        """Return True if today is the birthday."""
        return self._state
