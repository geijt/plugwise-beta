"""Generic Plugwise Entity Class."""

from __future__ import annotations

from plugwise.constants import GwEntityData

from homeassistant.const import ATTR_NAME, ATTR_VIA_DEVICE, CONF_HOST
from homeassistant.helpers.device_registry import (
    CONNECTION_NETWORK_MAC,
    CONNECTION_ZIGBEE,
    DeviceInfo,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    AVAILABLE,
    DOMAIN,
    FIRMWARE,
    GATEWAY_ID,
    HARDWARE,
    MAC_ADDRESS,
    MODEL,
    MODEL_ID,
    SMILE_NAME,
    VENDOR,
    ZIGBEE_MAC_ADDRESS,
)

# Upstream consts
from .coordinator import PlugwiseDataUpdateCoordinator


class PlugwiseEntity(CoordinatorEntity[PlugwiseDataUpdateCoordinator]):
    """Represent a PlugWise Entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PlugwiseDataUpdateCoordinator,
        pw_entity_id: str,
    ) -> None:
        """Initialise the gateway."""
        super().__init__(coordinator)
        self._pw_ent_id = pw_entity_id

        configuration_url: str | None = None
        if entry := self.coordinator.config_entry:
            configuration_url = f"http://{entry.data[CONF_HOST]}"

        data = coordinator.data.entities[pw_entity_id]
        connections = set()
        if mac := data.get(MAC_ADDRESS):
            connections.add((CONNECTION_NETWORK_MAC, mac))
        if mac := data.get(ZIGBEE_MAC_ADDRESS):
            connections.add((CONNECTION_ZIGBEE, mac))

        self._attr_device_info = DeviceInfo(
            configuration_url=configuration_url,
            identifiers={(DOMAIN, pw_entity_id)},
            connections=connections,
            manufacturer=data.get(VENDOR),
            model=data.get(MODEL),
            model_id=data.get(MODEL_ID),
            name=coordinator.data.gateway[SMILE_NAME],
            sw_version=data.get(FIRMWARE),
            hw_version=data.get(HARDWARE),
        )

        if pw_entity_id != coordinator.data.gateway[GATEWAY_ID]:
            self._attr_device_info.update(
                {
                    ATTR_NAME: data.get(ATTR_NAME),
                    ATTR_VIA_DEVICE: (
                        DOMAIN,
                        str(self.coordinator.data.gateway[GATEWAY_ID]),
                    ),
                }
            )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            # Upstream: Do not change the AVAILABLE line below: some Plugwise devices and zones
            # Upstream: do not provide their availability-status!
            self._pw_ent_id in self.coordinator.data.entities
            and (AVAILABLE not in self.pw_entity or self.pw_entity[AVAILABLE] is True)
            and super().available
        )

    @property
    def pw_entity(self) -> GwEntityData:
        """Return the plugwise entity connected to the pw_entity_id."""
        return self.coordinator.data.entities[self._pw_ent_id]


    async def async_added_to_hass(self) -> None:
        """Subscribe to updates."""
        self._handle_coordinator_update()
        await super().async_added_to_hass()
