"""Birthdays integration for Home Assistant.

This integration allows users to track birthdays using sensors and a calendar.
Each configured birthday instance creates:
- A sensor showing the person's name.
- A binary sensor indicating if today is their birthday.
- A sensor counting days until the next birthday.
- A sensor showing the birth date.
- A sensor showing the person's age.
- A sensor counting total days since birth.
- A calendar with all birthdays.

Configuration is handled via the UI (Config Flow).
"""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import *

# Set up logging
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Birthdays integration from a config entry.

    This function is called when a new instance of the integration is added.
    It stores the configuration data and forwards the setup to relevant platforms.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The configuration entry with user data.

    Returns:
        bool: True if setup is successful.
    """
    _LOGGER.debug("Setting up Birthdays integration for entry: %s", entry.entry_id)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data

    # Forward setup to sensor, binary sensor, and calendar platforms
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor", "calendar"])
    )

    _LOGGER.info("Birthdays integration setup complete for entry: %s", entry.entry_id)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of a config entry.

    This function is called when an instance of the integration is removed.
    It cleans up stored data and unloads the associated platforms.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The configuration entry being removed.

    Returns:
        bool: True if unload is successful.
    """
    _LOGGER.debug("Unloading Birthdays integration for entry: %s", entry.entry_id)

    # Remove entry data
    hass.data[DOMAIN].pop(entry.entry_id, None)

    # Unload the associated platforms
    success = await hass.config_entries.async_forward_entry_unload(entry, ["sensor", "binary_sensor", "calendar"])

    if success:
        _LOGGER.info("Successfully unloaded Birthdays integration for entry: %s", entry.entry_id)
    else:
        _LOGGER.warning("Failed to unload some platforms for entry: %s", entry.entry_id)

    return success
