"""Config flow for Daikin Modbus."""

from typing import Any

from modbus_connection import ModbusError
import voluptuous as vol

from homeassistant.components.modbus_connection import ConnectionNotReady, async_get_unit
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.selector import ConfigEntrySelector, ConfigEntrySelectorConfig, NumberSelector, NumberSelectorConfig, NumberSelectorMode

from .const import CONF_CONNECTION, CONF_UNIT_ID, DEFAULT_UNIT_ID, DOMAIN
from daikin_modbus import DaikinAidoo

STEP_USER = vol.Schema(
    {
        vol.Required(CONF_CONNECTION): ConfigEntrySelector(
            ConfigEntrySelectorConfig(integration="modbus_connection")
        ),
        vol.Required(CONF_UNIT_ID, default=DEFAULT_UNIT_ID): NumberSelector(
            NumberSelectorConfig(min=1, max=247, step=1, mode=NumberSelectorMode.BOX)
        ),
    }
)


class DaikinModbusConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle Daikin Modbus setup."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Select the shared Modbus connection and unit ID."""
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(f"{user_input[CONF_CONNECTION]}_{int(user_input[CONF_UNIT_ID])}")
            self._abort_if_unique_id_configured()
            if await self._async_validate(user_input):
                return self.async_create_entry(title="Daikin Modbus", data=user_input)
            errors["base"] = "cannot_connect"
        return self.async_show_form(step_id="user", data_schema=STEP_USER, errors=errors)

    async def _async_validate(self, data: dict[str, Any]) -> bool:
        """Perform a lightweight device read to verify the selected unit."""
        try:
            unit = async_get_unit(self.hass, data[CONF_CONNECTION], int(data[CONF_UNIT_ID]))
            device = DaikinAidoo(unit)
            await device.async_update()
        except (ConnectionNotReady, ModbusError, OSError, ValueError):
            return False
        return True
