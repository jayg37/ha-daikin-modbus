"""Read-only register entities."""

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import DaikinConfigEntry


SENSORS = (
    ("fan_percentage", "Fan percentage", PERCENTAGE, SensorDeviceClass.POWER_FACTOR),
    ("louver", "Louver state", None, None),
    ("available_modes", "Available modes", None, None),
    ("available_speeds", "Available speeds", None, None),
    ("slave_address", "Modbus slave address", None, None),
    ("baud_configuration", "Baud configuration", None, None),
    ("parity_configuration", "Parity configuration", None, None),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DaikinConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up read-only Daikin register sensors."""
    async_add_entities(DaikinRegisterSensor(entry.runtime_data, field, name, unit, device_class) for field, name, unit, device_class in SENSORS)


class DaikinRegisterSensor(SensorEntity):
    """Expose an unverified/read-only register without allowing writes."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, field: str, name: str, unit: str | None, device_class: SensorDeviceClass | None) -> None:
        self.coordinator = coordinator
        self._field = field
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{field}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_device_info = {
            "identifiers": {("daikin_modbus", coordinator.config_entry.entry_id)},
            "manufacturer": "Daikin",
            "model": "Airzone Aidoo Modbus",
            "name": "Daikin HVAC",
        }

    @property
    def native_value(self):
        """Return the latest register value."""
        return getattr(self.coordinator.data, self._field)

    @property
    def available(self) -> bool:
        """Return whether the coordinator has data."""
        return self.coordinator.last_update_success
