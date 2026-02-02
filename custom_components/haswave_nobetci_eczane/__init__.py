from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL
from .api import fetch_pharmacies

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HasWave Nöbetçi Eczane from a config entry."""
    city = (entry.data.get("city") or "").strip()
    district = (entry.data.get("district") or "").strip()
    if not city:
        city = "TEKİRDAĞ"
    if not district:
        district = city
    limit = entry.data.get("limit", 0) or 0
    update_interval = entry.data.get("update_interval", DEFAULT_UPDATE_INTERVAL) or DEFAULT_UPDATE_INTERVAL

    async def async_update_data():
        """Eczaneleri.net'ten veri çek."""
        return await hass.async_add_executor_job(
            fetch_pharmacies,
            city,
            district,
            limit,
        )

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=update_interval),
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.warning("İlk veri yükleme hatası (devam ediliyor): %s", err)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "sensor_count": entry.data.get("sensor_count", 5),
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
