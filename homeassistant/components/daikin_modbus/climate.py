"""Climate platform."""

from typing import Any

from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACAction, HVACMode
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import DaikinConfigEntry, DaikinCoordinator
from .entity import DaikinEntity

_MODE_TO_HA = {1: HVACMode.AUTO, 2: HVACMode.COOL, 3: HVACMode.HEAT, 4: HVACMode.FAN_ONLY, 5: HVACMode.DRY}
_HA_TO_MODE = {value: key for key, value in _MODE_TO_HA.items()}
_FAN_TO_NAME = {0: "auto", 1: "1", 2: "2", 3: "3"}
_NAME_TO_FAN = {value: key for key, value in _FAN_TO_NAME.items()}


async def async_setup_entry(hass: HomeAssistant, entry: DaikinConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    """Set up the Daikin climate entity."""
    async_add_entities([DaikinClimate(entry.runtime_data)])


class DaikinClimate(DaikinEntity, ClimateEntity):
    """Daikin climate entity using verified writable registers."""

    _attr_name = None
    _attr_temperature_unit = UnitOfTemperature.FAHRENHEIT
    _attr_min_temp = 60
    _attr_max_temp = 86
    _attr_target_temperature_step = 1
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.AUTO, HVACMode.COOL, HVACMode.HEAT, HVACMode.FAN_ONLY, HVACMode.DRY]
    _attr_fan_modes = list(_NAME_TO_FAN)

    def __init__(self, coordinator: DaikinCoordinator) -> None:
        super().__init__(coordinator, "climate")

    @property
    def current_temperature(self) -> float | None:
        return self.coordinator.data.room_temperature

    @property
    def target_temperature(self) -> float | None:
        return self.coordinator.data.setpoint

    @property
    def hvac_mode(self) -> HVACMode | None:
        if self.coordinator.data.power is False:
            return HVACMode.OFF
        return _MODE_TO_HA.get(self.coordinator.data.hvac_mode)

    @property
    def hvac_action(self) -> HVACAction | None:
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
        return _FAN_TO_NAME.get(self.coordinator.data.fan_speed)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            await self.coordinator.device.write("setpoint", temperature)
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode is HVACMode.OFF:
            await self.coordinator.device.write("power", False)
        else:
            await self.coordinator.device.write("power", True)
            await self.coordinator.device.write("hvac_mode", _HA_TO_MODE[hvac_mode])
        await self.coordinator.async_request_refresh()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        await self.coordinator.device.write("fan_speed", _NAME_TO_FAN[fan_mode])
        await self.coordinator.async_request_refresh()
