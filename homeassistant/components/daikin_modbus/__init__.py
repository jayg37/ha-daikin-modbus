"""Home Assistant integration for Daikin/Airzone Aidoo Modbus devices."""

from daikin_modbus import DaikinAidoo

from homeassistant.components.modbus_connection import async_get_unit
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_CONNECTION, CONF_UNIT_ID
from .coordinator import DaikinCoordinator

PLATFORMS = [Platform.CLIMATE, Platform.SENSOR]
type DaikinConfigEntry = ConfigEntry[DaikinCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: DaikinConfigEntry) -> bool:
    """Set up a Daikin Modbus device."""
    unit = async_get_unit(hass, entry.data[CONF_CONNECTION], int(entry.data[CONF_UNIT_ID]))
    device = DaikinAidoo(unit)
    coordinator = DaikinCoordinator(hass, entry, device)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator
    entry.async_on_unload(
        unit.on_connection_lost(
            lambda: hass.config_entries.async_schedule_reload(entry.entry_id)
        )
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DaikinConfigEntry) -> bool:
    """Unload a Daikin Modbus device."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
