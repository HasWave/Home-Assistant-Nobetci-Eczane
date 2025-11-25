"""The HasWave Nöbetçi Eczane integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL
from .api import HasWaveEczaneAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HasWave Nöbetçi Eczane from a config entry."""
    
    api = HasWaveEczaneAPI(
        api_url=entry.data.get("api_url", "https://api.haswave.com/api/v1/eczane"),
        city=entry.data["city"],
        district=entry.data.get("district", ""),
        limit=entry.data.get("limit", 0),
    )
    
    update_interval = entry.data.get("update_interval", DEFAULT_UPDATE_INTERVAL)
    
    async def async_update_data():
        """Fetch data from API."""
        try:
            data = await hass.async_add_executor_job(api.fetch_pharmacies)
            if data:
                _LOGGER.debug(f"API'den {len(data)} eczane verisi alındı")
            else:
                _LOGGER.warning("API'den veri alınamadı")
            return data
        except Exception as err:
            _LOGGER.error(f"Veri güncelleme hatası: {err}")
            raise
    
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
        _LOGGER.error(f"İlk veri yükleme hatası: {err}")
        # Hata olsa bile devam et, sensor'lar oluşturulsun
    
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
        "sensor_count": entry.data.get("sensor_count", 5),
    }
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok

