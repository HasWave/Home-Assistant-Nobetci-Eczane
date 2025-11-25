"""Sensor platform for HasWave Nöbetçi Eczane."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import DOMAIN


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
    
    entities = [HasWaveEczaneCountSensor(coordinator)]
    
    # Her eczane için ayrı sensor oluştur (maksimum 10)
    pharmacies = coordinator.data or []
    for i, pharmacy in enumerate(pharmacies[:10]):
        entities.append(HasWaveEczaneSensor(coordinator, i + 1))
    
    async_add_entities(entities)


class HasWaveEczaneCountSensor(CoordinatorEntity, SensorEntity):
    """Representation of pharmacy count sensor."""
    
    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_count"
        self._attr_name = "Nöbetçi Eczane Sayısı"
        self._attr_icon = "mdi:pharmacy"
        self._attr_state_class = SensorStateClass.MEASUREMENT
    
    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        return len(self.coordinator.data or [])


class HasWaveEczaneSensor(CoordinatorEntity, SensorEntity):
    """Representation of a pharmacy sensor."""
    
    def __init__(self, coordinator: DataUpdateCoordinator, index: int) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._index = index
        self._attr_unique_id = f"{DOMAIN}_{index}"
        self._attr_name = f"Nöbetçi Eczane {index}"
        self._attr_icon = "mdi:pharmacy"
    
    @property
    def native_value(self) -> str:
        """Return the state of the sensor."""
        pharmacies = self.coordinator.data or []
        if self._index <= len(pharmacies):
            return pharmacies[self._index - 1].get("name", "N/A")
        return "N/A"
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        pharmacies = self.coordinator.data or []
        if self._index <= len(pharmacies):
            pharmacy = pharmacies[self._index - 1]
            return {
                "phone": format_phone_number(pharmacy.get("phone", "")),
                "address": pharmacy.get("address", ""),
                "map_link": pharmacy.get("map_link", ""),
            }
        return {}

