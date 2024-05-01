"""Diagnostics support for Plugwise."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.redact import async_redact_data

from .const import (
    AVAILABLE_SCHEDULES,
    COORDINATOR,  # pw-beta
    DEVICES,
    DOMAIN,
    GATEWAY,
    MAC_ADDRESS,
    NONE,
    SELECT_SCHEDULE,
    ZIGBEE_MAC_ADDRESS,
)
from .coordinator import PlugwiseDataUpdateCoordinator

KEYS_TO_REDACT = {
    ATTR_NAME,
    MAC_ADDRESS,
    ZIGBEE_MAC_ADDRESS
}

OFF = "off"

async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: PlugwiseDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        COORDINATOR
    ]

    data = async_redact_data(coordinator.data.devices, KEYS_TO_REDACT)

    for device in data:
        if (key := SELECT_SCHEDULE) in data[device]:
            if (value := data[device][key]) not in (OFF, NONE):
                i = data[device][AVAILABLE_SCHEDULES].index(value)
                data[device][key] = f"**REDACTED_{i}**"

            value = data[device][AVAILABLE_SCHEDULES]
            for j in range(len(value)):
                if value[j] not in (OFF, NONE):
                    value[j] = f"**REDACTED_{j}**"

            data[device][AVAILABLE_SCHEDULES] = value

    return {GATEWAY: coordinator.data.gateway, DEVICES: data}
