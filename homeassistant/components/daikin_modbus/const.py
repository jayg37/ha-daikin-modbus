"""Constants for the Daikin Modbus integration."""

from datetime import timedelta

DOMAIN = "daikin_modbus"
CONF_CONNECTION = "connection"
CONF_UNIT_ID = "unit_id"
DEFAULT_UNIT_ID = 1
SCAN_INTERVAL = timedelta(seconds=30)
