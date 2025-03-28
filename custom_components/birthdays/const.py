"""Constants for the Birthdays integration.

This file defines all constant values used throughout the integration.
"""

# Domain name of the integration
DOMAIN = "birthdays"

# Configuration keys used in config flow
CONF_NAME = "name"      # Name of the person
CONF_YEAR = "year"      # Year of birth
CONF_MONTH = "month"    # Month of birth
CONF_DAY = "day"        # Day of birth

# Default calendar details
CALENDAR_NAME = "Birthdays"                 # Default name for the calendar
CALENDAR_ENTITY_ID = "calendar.birthdays"   # Fixed Entity ID for the calendar

# Sensor and binary sensor entity name templates
SENSOR_NAME_TEMPLATE = "sensor.birthdays_{name}_{sensor_type}"
BINARY_SENSOR_NAME_TEMPLATE = "binary_sensor.birthdays_{name}_today"

# Device identifiers
DEVICE_ID_TEMPLATE = "birthdays_{name}"

# Manufacturer & Model
MANUFACTURER = "UnoSite"
MODEL = "Birthdays Integration"

# Icons
ICON_BIRTHDAY = "mdi:cake-variant"
ICON_NEXT_BIRTHDAY = "mdi:calendar-clock"
ICON_DATE_OF_BIRTH = "mdi:calendar"
ICON_YEARS_OLD = "mdi:numeric"
ICON_BINARY_SENSOR = "mdi:cake-variant"  # Tilføjet for binær sensor

# Default sensor scan interval (optional)
DEFAULT_SCAN_INTERVAL = 3600  # 1 time (i sekunder)

# Logging messages
LOG_BIRTHDAY_ADDED = "Added birthday event: %s on %s"
LOG_BIRTHDAY_REMOVED = "Removed birthday events for entry: %s"
LOG_CALENDAR_CREATED = "Birthdays calendar entity added: %s"
LOG_CALENDAR_REMOVED = "Removed Birthdays calendar entity as no birthdays remain."
LOG_ENTRY_MISSING_DATA = "Entry is missing required data fields: %s"
LOG_SENSOR_UPDATE = "Updating sensor for %s"
LOG_INVALID_DATE = "Invalid date provided: %s-%s-%s"
LOG_DUPLICATE_ENTRY = "Duplicate entry detected: %s"
