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

# Calendar details
CALENDAR_NAME = "Birthdays"                 # Name of the calendar entity
CALENDAR_ENTITY_ID = "calendar.birthdays"   # Entity ID for the calendar

# Sensor entity name templates
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
ICON_BINARY_SENSOR = "mdi:cake"
