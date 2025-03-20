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
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from .const import *

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Birthdays integration from a config entry.

    This function is called when a new instance of the integration is added.
    It ensures that a central "Birthdays" calendar exists and forwards setup to sensors.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The configuration entry with user data.

    Returns:
        bool: True if setup is successful.
    """
    _LOGGER.debug("Setting up Birthdays integration for entry: %s", entry.entry_id)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data

    try:
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor", "calendar"])
        _LOGGER.info("Birthdays integration setup complete for entry: %s", entry.entry_id)
    except Exception as e:
        _LOGGER.error("Failed to set up Birthdays entry %s: %s", entry.entry_id, str(e))
        return False

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

    # Unload only the sensors and binary sensors for the removed birthdate
    success = await hass.config_entries.async_unload_platforms(entry, ["sensor", "binary_sensor"])

    # Remove only the specific birthday data
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.info("Removed entry data for: %s", entry.entry_id)

    # Check if any birthdays remain
    remaining_entries = [
        e for e in hass.config_entries.async_entries(DOMAIN) if e.entry_id != entry.entry_id
    ]

    if not remaining_entries:
        _LOGGER.info("Last birthday instance removed. Removing calendar...")
        await hass.config_entries.async_unload_platforms(entry, ["calendar"])
        await _remove_calendar_entity(hass)

    _LOGGER.info("Successfully unloaded Birthdays integration for entry: %s", entry.entry_id)
    return success


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle cleanup when an entry is removed.

    This function ensures that the central "Birthdays" calendar **is removed**
    when the last birthday is deleted.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The configuration entry being removed.
    """
    _LOGGER.debug("Removing Birthdays integration entry: %s", entry.entry_id)

    # Check if there are remaining birthdays
    remaining_entries = [
        ent for ent in hass.config_entries.async_entries(DOMAIN) if ent.entry_id != entry.entry_id
    ]

    if not remaining_entries:
        _LOGGER.info("Last birthday removed. Removing Birthdays calendar entity.")
        await _remove_calendar_entity(hass)

    # Remove domain data completely if no birthdays remain
    if DOMAIN in hass.data and not hass.data[DOMAIN]:
        hass.data.pop(DOMAIN)
        _LOGGER.info("All Birthdays data removed from Home Assistant.")

    _LOGGER.info("Cleanup complete for Birthdays integration entry: %s", entry.entry_id)


async def _remove_calendar_entity(hass: HomeAssistant):
    """Remove the Birthdays calendar entity when the last birthday is deleted."""
    entity_registry = async_get_entity_registry(hass)
    calendar_entity = entity_registry.async_get(CALENDAR_ENTITY_ID)

    if calendar_entity:
        try:
            entity_registry.async_remove(calendar_entity.entity_id)
            _LOGGER.info("Birthdays calendar entity removed.")
        except Exception as e:
            _LOGGER.error("Failed to remove Birthdays calendar entity: %s", str(e))
    else:
        _LOGGER.info("No Birthdays calendar entity found to remove.")
