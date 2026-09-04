"""Climate entity for the Daikin/Airzone Aidoo."""

from typing import Any

from daikin_modbus import DaikinAidoo

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACAction, HVACMode
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import DaikinConfigEntry, DaikinCoordinator

_MODE_TO_HA = {
    1: HVACMode.AUTO,
    2: HVACMode.COOL,
    3: HVACMode.HEAT,
    4: HVACMode.FAN_ONLY,
    5: HVACMode.DRY,
}
_HA_TO_MODE = {value: key for key, value in _MODE_TO_HA.items()}
_FAN_TO_NAME = {0: "auto", 1: "1", 2: "2", 3: "3"}
_NAME_TO_FAN = {value: key for key, value in _FAN_TO_NAME.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DaikinConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Daikin climate entity."""
    async_add_entities([DaikinClimate(entry.runtime_data)])


class DaikinClimate(ClimateEntity):
    """Represent the verified Daikin controls as a climate entity."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.FAHRENHEIT
    _attr_min_temp = 60
    _attr_max_temp = 86
    _attr_target_temperature_step = 1
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.AUTO, HVACMode.COOL, HVACMode.HEAT, HVACMode.FAN_ONLY, HVACMode.DRY]
    _attr_fan_modes = list(_NAME_TO_FAN)

    def __init__(self, coordinator: DaikinCoordinator) -> None:
        """Initialize the climate entity."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_climate"
        self._attr_device_info = {
            "identifiers": {("daikin_modbus", coordinator.config_entry.entry_id)},
            "manufacturer": "Daikin",
            "model": "Airzone Aidoo Modbus",
            "name": "Daikin HVAC",
        }

    @property
    def available(self) -> bool:
        """Return whether the coordinator has data."""
        return self.coordinator.last_update_success

    @property
    def current_temperature(self) -> float | None:
        """Return the room temperature."""
        return self.coordinator.data.room_temperature

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        return self.coordinator.data.setpoint

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return the HVAC mode."""
        if self.coordinator.data.power == 0:
            return HVACMode.OFF
        return _MODE_TO_HA.get(self.coordinator.data.hvac_mode)

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the available action based on commanded mode."""
        mode = self.hvac_mode
        if mode is None:
            return None
        if mode is HVACMode.OFF:
            return HVACAction.OFF
        if mode is HVACMode.COOL:
            return HVACAction.COOLING
        if mode is HVACMode.HEAT:
            return HVACAction.HEATING
        return HVACAction.IDLE

    @property
    def fan_mode(self) -> str | None:
        """Return the fan mode."""
        return _FAN_TO_NAME.get(self.coordinator.data.fan_speed)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set the temperature in Fahrenheit."""
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            await self.coordinator.device.write("setpoint", temperature)
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set power and HVAC mode."""
        if hvac_mode is HVACMode.OFF:
            await self.coordinator.device.write("power", 0)
        else:
            await self.coordinator.device.write("power", 1)
            await self.coordinator.device.write("hvac_mode", _HA_TO_MODE[hvac_mode])
        await self.coordinator.async_request_refresh()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set the numeric fan speed."""
        await self.coordinator.device.write("fan_speed", _NAME_TO_FAN[fan_mode])
        await self.coordinator.async_request_refresh()
