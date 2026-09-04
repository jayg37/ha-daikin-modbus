"""Read-only register entities."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import DaikinConfigEntry, DaikinCoordinator
from .entity import DaikinEntity

SENSORS = (
    ("fan_percentage", "Fan percentage", PERCENTAGE),
    ("louver", "Louver state", None),
    ("available_modes", "Available modes", None),
    ("available_speeds", "Available speeds", None),
    ("slave_address", "Modbus slave address", None),
    ("baud_configuration", "Baud configuration", None),
    ("parity_configuration", "Parity configuration", None),
)


async def async_setup_entry(hass: HomeAssistant, entry: DaikinConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    """Set up read-only Daikin register sensors."""
    async_add_entities(
        DaikinRegisterSensor(entry.runtime_data, field, name, unit)
        for field, name, unit in SENSORS
    )


class DaikinRegisterSensor(DaikinEntity, SensorEntity):
    """Expose a read-only device register."""

    def __init__(self, coordinator: DaikinCoordinator, field: str, name: str, unit: str | None) -> None:
        super().__init__(coordinator, field)
        self._field = field
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit

    @property
    def native_value(self):
        """Return the latest register value."""
        return getattr(self.coordinator.data, self._field)
