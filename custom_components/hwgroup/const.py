"""Constants for the HW Group integration."""
from typing import Final

DOMAIN: Final = "hwgroup"

# Configuration
CONF_DEVICE_TYPE: Final = "device_type"
CONF_DEVICE_NAME: Final = "device_name"

# Device Types
DEVICE_TYPE_POSEIDON_3268: Final = "poseidon_3268"
DEVICE_TYPE_POSEIDON_3266: Final = "poseidon_3266"
DEVICE_TYPE_SMS_GATEWAY: Final = "sms_gateway"

DEVICE_TYPES: Final = [
    DEVICE_TYPE_POSEIDON_3268,
    DEVICE_TYPE_POSEIDON_3266,
    DEVICE_TYPE_SMS_GATEWAY,
]

# Default values
DEFAULT_SCAN_INTERVAL: Final = 30
DEFAULT_PORT: Final = 80
DEFAULT_TIMEOUT: Final = 10

# Sensor types
SENSOR_TYPE_TEMPERATURE: Final = "temperature"
SENSOR_TYPE_HUMIDITY: Final = "humidity"
SENSOR_TYPE_VOLTAGE: Final = "voltage"
SENSOR_TYPE_CURRENT: Final = "current"
SENSOR_TYPE_GENERIC: Final = "generic"

# Binary sensor types
BINARY_SENSOR_TYPE_CONTACT: Final = "contact"
BINARY_SENSOR_TYPE_ALARM: Final = "alarm"

# Update coordinator
UPDATE_LISTENER: Final = "update_listener"
