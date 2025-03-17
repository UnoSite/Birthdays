"""Birthdays integration for Home Assistant.

This integration allows users to track birthdays using sensors and a calendar.
Each configured birthday instance creates:
- A sensor showing the person's name.
- A binary sensor indicating if today is their birthday.
- A sensor counting days until the next birthday.
- A sensor showing the birth date.
- A sensor showing the person's age.
- A calendar with all birthdays.

Configuration is handled via the UI (Config Flow).
"""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from .const import *

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

    # Forward setup to platforms
    for platform in ["sensor", "binary_sensor", "calendar"]:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    _LOGGER.info("Birthdays integration setup complete for entry: %s", entry.entry_id)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of a config entry.

    This function is called when an instance of the integration is removed.
    It cleans up stored data, removes devices, and unloads the associated platforms.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The configuration entry being removed.

    Returns:
        bool: True if unload is successful.
    """
    _LOGGER.debug("Unloading Birthdays integration for entry: %s", entry.entry_id)

    # Remove device from device registry
    device_registry = async_get_device_registry(hass)  # Ingen await!
    if device_registry:
        device = device_registry.async_get_device({(DOMAIN, entry.entry_id)})
        if device:
            device_registry.async_remove_device(device.id)
            _LOGGER.info("Removed device for entry: %s", entry.entry_id)
        else:
            _LOGGER.warning("Device not found for entry: %s", entry.entry_id)

    # Unload associated platforms én ad gangen
    unload_results = []
    for platform in ["sensor", "binary_sensor", "calendar"]:
        success = await hass.config_entries.async_forward_entry_unload(entry, platform)
        unload_results.append(success)

    success = all(unload_results)

    # Remove entry data
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.info("Removed entry data for: %s", entry.entry_id)

    _LOGGER.info("Successfully unloaded Birthdays integration for entry: %s", entry.entry_id)
    return success

async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle cleanup when an entry is removed.

    This function ensures the integration is completely cleaned up without requiring a restart.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The configuration entry being removed.
    """
    _LOGGER.debug("Removing Birthdays integration entry: %s", entry.entry_id)

    # Remove calendar entity if it was the last instance
    if DOMAIN in hass.data and CALENDAR_ENTITY_ID in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(CALENDAR_ENTITY_ID)
        _LOGGER.info("Removed Birthdays calendar entity")

    # Remove domain data if no entries remain
    if DOMAIN in hass.data and not hass.data[DOMAIN]:
        hass.data.pop(DOMAIN)
        _LOGGER.info("All Birthdays data removed from Home Assistant")

    _LOGGER.info("Cleanup complete for Birthdays integration entry: %s", entry.entry_id)
