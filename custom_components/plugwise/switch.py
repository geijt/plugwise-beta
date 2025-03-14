"""Plugwise Switch component for HomeAssistant."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from plugwise.constants import SwitchType

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import (
    COOLING_ENA_SWITCH,
    DHW_CM_SWITCH,
    LOCK,
    LOGGER,  # pw-beta
    MEMBERS,
    RELAY,
    SWITCHES,
)

# Upstream consts
from .coordinator import PlugwiseConfigEntry, PlugwiseDataUpdateCoordinator
from .entity import PlugwiseEntity
from .util import plugwise_command

PARALLEL_UPDATES = 0


@dataclass(frozen=True)
class PlugwiseSwitchEntityDescription(SwitchEntityDescription):
    """Describes Plugwise switch entity."""

    key: SwitchType


# Upstream consts
PLUGWISE_SWITCHES: tuple[PlugwiseSwitchEntityDescription, ...] = (
    PlugwiseSwitchEntityDescription(
        key=DHW_CM_SWITCH,
        translation_key=DHW_CM_SWITCH,
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
    ),
    PlugwiseSwitchEntityDescription(
        key=LOCK,
        translation_key=LOCK,
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
    ),
    PlugwiseSwitchEntityDescription(
        key=RELAY,
        translation_key=RELAY,
        device_class=SwitchDeviceClass.SWITCH,
    ),
    PlugwiseSwitchEntityDescription(
        key=COOLING_ENA_SWITCH,
        translation_key=COOLING_ENA_SWITCH,
        device_class=SwitchDeviceClass.SWITCH,
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PlugwiseConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Plugwise switches from a config entry."""
    coordinator = entry.runtime_data

    @callback
    def _add_entities() -> None:
        """Add Entities."""
        if not coordinator.new_devices:
            return

        # Upstream consts
        # async_add_entities(
        #     PlugwiseSwitchEntity(coordinator, device_id, description)
        #     for device_id in coordinator.new_devices
        #     if (switches := coordinator.data.devices[device_id].get(SWITCHES))
        #     for description in PLUGWISE_SWITCHES
        #     if description.key in switches
        # )
        # pw-beta alternative for debugging
        entities: list[PlugwiseSwitchEntity] = []
        for device_id in coordinator.new_devices:
            device = coordinator.data[device_id]
            if not (switches := device.get(SWITCHES)):
                continue
            for description in PLUGWISE_SWITCHES:
                if description.key not in switches:
                    continue
                entities.append(PlugwiseSwitchEntity(coordinator, device_id, description))
                LOGGER.debug(
                    "Add %s %s switch", device["name"], description.translation_key
                )
        async_add_entities(entities)

    _add_entities()
    entry.async_on_unload(coordinator.async_add_listener(_add_entities))


class PlugwiseSwitchEntity(PlugwiseEntity, SwitchEntity):
    """Representation of a Plugwise plug."""

    entity_description: PlugwiseSwitchEntityDescription

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        device_id: str,
        description: PlugwiseSwitchEntityDescription,
    ) -> None:
        """Set up the Plugwise API."""
        super().__init__(coordinator, device_id)
        self.entity_description = description
        self._attr_unique_id = f"{device_id}-{description.key}"

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return self.device[SWITCHES][self.entity_description.key]  # Upstream const

    @plugwise_command
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        await self.coordinator.api.set_switch_state(
            self._dev_id,
            self.device.get(MEMBERS),
            self.entity_description.key,
            "on",
        )  # Upstream const

    @plugwise_command
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        await self.coordinator.api.set_switch_state(
            self._dev_id,
            self.device.get(MEMBERS),
            self.entity_description.key,
            "off",
        )  # Upstream const
