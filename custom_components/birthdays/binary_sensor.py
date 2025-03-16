from homeassistant.helpers.entity import BinarySensorEntity
from datetime import datetime
from .const import *

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the binary sensor platform."""
    config = entry.data
    async_add_entities([BirthdayBinarySensor(config)])

class BirthdayBinarySensor(BinarySensorEntity):
    """Binary sensor indicating if today is the birthday."""

    def __init__(self, config):
        self._name = f"birthdays_{config[CONF_NAME]}_today"
        self._config = config
        self._state = False
        self.update()

    def update(self):
        """Update binary sensor state."""
        today = datetime.today()
        self._state = today.day == self._config[CONF_DAY] and today.month == self._config[CONF_MONTH]

    @property
    def is_on(self):
        return self._state
