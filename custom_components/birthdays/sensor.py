from datetime import datetime, timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import *

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the sensor platform."""
    config = entry.data
    async_add_entities([
        BirthdaySensor(config, "Name"),
        BirthdaySensor(config, "Next birthday in"),
        BirthdaySensor(config, "Date of birth"),
        BirthdaySensor(config, "Number of years"),
        BirthdaySensor(config, "Number of days"),
    ])

class BirthdaySensor(Entity):
    """Representation of a Birthday Sensor."""

    def __init__(self, config, sensor_type):
        self._name = f"birthdays_{config[CONF_NAME]}_{sensor_type.replace(' ', '_').lower()}"
        self._sensor_type = sensor_type
        self._state = None
        self._config = config
        self.update()

    def update(self):
        """Update sensor state."""
        name = self._config[CONF_NAME]
        birth_date = datetime(self._config[CONF_YEAR], self._config[CONF_MONTH], self._config[CONF_DAY])
        today = datetime.today()

        if self._sensor_type == "Name":
            self._state = name
        elif self._sensor_type == "Next birthday in":
            next_birthday = datetime(today.year, birth_date.month, birth_date.day)
            if next_birthday < today:
                next_birthday = datetime(today.year + 1, birth_date.month, birth_date.day)
            self._state = (next_birthday - today).days
        elif self._sensor_type == "Date of birth":
            self._state = birth_date.strftime("%Y-%m-%d")
        elif self._sensor_type == "Number of years":
            self._state = today.year - birth_date.year
        elif self._sensor_type == "Number of days":
            self._state = (today - birth_date).days

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return self._name
