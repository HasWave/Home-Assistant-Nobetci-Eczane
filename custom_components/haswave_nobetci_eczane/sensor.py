"""Sensor platform for HasWave Nöbetçi Eczane."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def format_phone_number(phone: str) -> str:
    """Format phone number."""
    if not phone:
        return phone
    digits = "".join(filter(str.isdigit, phone))
    if not digits:
        return phone
    if len(digits) == 12 and digits.startswith("90"):
        digits = "0" + digits[2:]
    if len(digits) == 11 and digits.startswith(("0", "05")):
        return f"{digits[:4]} {digits[4:7]} {digits[7:]}"
    return phone


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    sensor_count = hass.data[DOMAIN][entry.entry_id].get("sensor_count", 5)
    entry_id = entry.entry_id

    entities = [
        HasWaveEczaneSensor(coordinator, entry_id, i)
        for i in range(1, sensor_count + 1)
    ]
    async_add_entities(entities)


class HasWaveEczaneSensor(CoordinatorEntity, SensorEntity):
    """Representation of a pharmacy sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry_id: str,
        index: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._index = index
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{index}"
        self._attr_name = f"Nöbetçi Eczane {index}"
        self._attr_icon = "mdi:pharmacy"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        pharmacies = self.coordinator.data
        if self._index > len(pharmacies):
            return None
        name = pharmacies[self._index - 1].get("name")
        return name or None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if self.coordinator.data is None:
            return {}
        pharmacies = self.coordinator.data
        if self._index > len(pharmacies):
            return {}
        pharmacy = pharmacies[self._index - 1]
        if not pharmacy:
            return {}
        attrs: dict[str, Any] = {}
        if pharmacy.get("phone"):
            attrs["phone"] = format_phone_number(pharmacy["phone"])
        if pharmacy.get("address"):
            attrs["address"] = pharmacy["address"]
        if pharmacy.get("map_link"):
            attrs["map_link"] = pharmacy["map_link"]
        return attrs
