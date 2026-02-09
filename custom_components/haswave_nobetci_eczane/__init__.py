"""The HasWave Nöbetçi Eczane integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DEFAULT_UPDATE_INTERVAL, DOMAIN
from .api import HasWaveEczaneAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HasWave Nöbetçi Eczane from a config entry."""
    data = entry.data or {}
    opts = entry.options or {}
    sensor_count = data.get("sensor_count", 5)
    try:
        sensor_count = max(1, min(20, int(sensor_count)))
    except (TypeError, ValueError):
        sensor_count = 5
    api = HasWaveEczaneAPI(
        city=data.get("city", ""),
        district=data.get("district", ""),
        limit=sensor_count,
    )

    async def async_update_data():
        """Eczaneleri.net iframe'den veri çek (aiohttp)."""
        try:
            session = async_get_clientsession(hass)
            result = await api.async_fetch(session)
            if result is not None:
                _LOGGER.debug("Eczaneleri.net: %s eczane verisi alındı", len(result))
            else:
                _LOGGER.warning("Eczaneleri.net veri alınamadı")
            return result if result is not None else []
        except Exception as err:
            _LOGGER.error("Veri güncelleme hatası: %s", err, exc_info=True)
            return []

    update_interval = opts.get("update_interval", data.get("update_interval", DEFAULT_UPDATE_INTERVAL))
    try:
        update_interval = int(update_interval)
    except (TypeError, ValueError):
        update_interval = DEFAULT_UPDATE_INTERVAL
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
        "sensor_count": sensor_count,
    }
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_options))
    return True


async def _async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Seçenekler değişince entegrasyonu yeniden yükle (güncelleme sıklığı güncellenir)."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok

