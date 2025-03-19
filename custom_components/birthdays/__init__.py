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

    entity_registry = async_get_entity_registry(hass)

    # Tjek om Birthdays-kalenderen allerede findes i entity_registry
    calendar_exists = any(
        entity.entity_id == CALENDAR_ENTITY_ID for entity in entity_registry.entities.values()
    )

    if not calendar_exists:
        _LOGGER.info("No existing Birthdays calendar found. Creating main instance.")
        await hass.config_entries.async_forward_entry_setups(entry, ["calendar", "binary_sensor"])
    else:
        _LOGGER.info("Existing Birthdays calendar found. Proceeding with config flow.")
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor", "calendar"])

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

    # Fjern kun de sensorer og entiteter, der er knyttet til denne specifikke fødselar
    success = await hass.config_entries.async_unload_platforms(entry, ["sensor", "binary_sensor"])

    # Fjern kun fødselarens data, men bevar kalenderen og den globale binary sensor
    if DOMAIN in hass.data and entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.info("Removed entry data for: %s", entry.entry_id)

    # Tjek om der stadig er fødselsdage tilbage
    remaining_entries = [
        e for e in hass.config_entries.async_entries(DOMAIN) if e.entry_id != entry.entry_id
    ]

    if not remaining_entries:
        _LOGGER.info("Last birthday instance removed, but keeping calendar and global binary sensor.")

    _LOGGER.info("Successfully unloaded Birthdays integration for entry: %s", entry.entry_id)
    return success

async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle cleanup when an entry is removed.

    Denne funktion sørger for, at den centrale "Birthdays" kalender **ikke fjernes** ved sidste fødselsdagssletning.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The configuration entry being removed.
    """
    _LOGGER.debug("Removing Birthdays integration entry: %s", entry.entry_id)

    entity_registry = async_get_entity_registry(hass)

    # Tjek om der stadig findes fødselsdage
    remaining_entries = [
        ent for ent in hass.config_entries.async_entries(DOMAIN) if ent.entry_id != entry.entry_id
    ]

    if not remaining_entries:
        _LOGGER.info("Last birthday removed. Keeping Birthdays calendar.")

    # Fjern domænedata, hvis ingen entries er tilbage, men bevar kalenderen
    if DOMAIN in hass.data and not hass.data[DOMAIN]:
        _LOGGER.info("All individual birthday entries removed, but keeping calendar entity.")

    _LOGGER.info("Cleanup complete for Birthdays integration entry: %s", entry.entry_id)
