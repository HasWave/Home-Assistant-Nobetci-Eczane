"""Sensor platform for HasWave Nöbetçi Eczane."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def format_phone_number(phone: str) -> str:
    """Format phone number."""
    if not phone:
        return phone
    
    digits = ''.join(filter(str.isdigit, phone))
    
    if not digits:
        return phone
    
    if len(digits) == 12 and digits.startswith('90'):
        digits = '0' + digits[2:]
    
    if len(digits) == 11:
        if digits.startswith('05'):
            return f"{digits[:4]} {digits[4:7]} {digits[7:]}"
        elif digits.startswith('0'):
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
    
    entities = []
    
    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title or "Nöbetçi Eczane",
        manufacturer="HasWave",
    )
    for i in range(1, sensor_count + 1):
        entities.append(HasWaveEczaneSensor(coordinator, entry.entry_id, i, device_info))
    async_add_entities(entities)


class HasWaveEczaneSensor(CoordinatorEntity, SensorEntity):
    """Representation of a pharmacy sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry_id: str,
        index: int,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator)
        self._index = index
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{index}"
        self._attr_name = f"Nöbetçi Eczane {index}"
        self._attr_icon = "mdi:stethoscope"
        self._attr_device_info = device_info
    
    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            _LOGGER.debug(f"Eczane sensor {self._index}: Coordinator data is None")
            return None
        
        pharmacies = self.coordinator.data
        _LOGGER.debug(f"Eczane sensor {self._index}: {len(pharmacies)} eczane bulundu")
        
        # Veri yoksa None döndür (sensor unavailable olur)
        if self._index > len(pharmacies):
            return None
        
        name = pharmacies[self._index - 1].get("name")
        if not name:
            return None
        
        _LOGGER.debug(f"Eczane sensor {self._index}: {name}")
        return name
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if self.coordinator.data is None:
            return {}
        
        pharmacies = self.coordinator.data
        
        # Veri yoksa boş attributes döndür
        if self._index > len(pharmacies):
            return {}
        
        pharmacy = pharmacies[self._index - 1]
        if not pharmacy:
            return {}
        
        attributes = {}
        
        phone = pharmacy.get("phone")
        if phone:
            attributes["phone"] = format_phone_number(phone)
        
        address = pharmacy.get("address")
        if address:
            attributes["address"] = address
        
        map_link = pharmacy.get("map_link")
        if map_link:
            attributes["map_link"] = map_link
        
        return attributes

