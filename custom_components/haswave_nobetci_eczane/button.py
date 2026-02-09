"""Güncelle butonu - veriyi anında yeniler (Kontroller sekmesinde)."""
from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Buton platformu kurulumu."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.title or "Nöbetçi Eczane",
        manufacturer="HasWave",
    )
    async_add_entities([NobetciEczaneGuncelleButton(coordinator, entry.entry_id, device_info)])


class NobetciEczaneGuncelleButton(CoordinatorEntity, ButtonEntity):
    """Veriyi hemen güncellemek için buton."""

    _attr_icon = "mdi:refresh"
    _attr_name = "Güncelle"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry_id: str,
        device_info: DeviceInfo,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_guncelle"
        self._attr_device_info = device_info

    async def async_press(self) -> None:
        """Butona basıldığında veriyi yenile."""
        await self.coordinator.async_request_refresh()
