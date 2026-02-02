"""HasWave Nöbetçi Eczane — iframe panel (API kullanılmaz)."""
from __future__ import annotations

import logging
from urllib.parse import urlencode

from homeassistant.components import frontend
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, DEFAULT_IFRAME_BASE

_LOGGER = logging.getLogger(__name__)


def _panel_key(entry_id: str) -> str:
    """Her entry için benzersiz panel anahtarı."""
    return f"haswave_nobetci_eczane_{entry_id}"


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HasWave Nöbetçi Eczane from a config entry — iframe panel."""
    city = (entry.data.get("city") or "").strip()
    district = (entry.data.get("district") or "").strip()
    if not city:
        _LOGGER.warning("İl bilgisi eksik, varsayılan kullanılıyor")
        city = "TEKİRDAĞ"
    if not district:
        district = city

    params = {"il": city, "ilce": district}
    iframe_url = f"{DEFAULT_IFRAME_BASE}?{urlencode(params)}"

    panel_key = _panel_key(entry.entry_id)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"iframe_url": iframe_url, "panel_key": panel_key}

    # Panel kaydet — sidebar'da "Nöbetçi Eczane" görünür
    await frontend.async_register_built_in_panel(
        hass,
        "iframe",
        "Nöbetçi Eczane",
        "mdi:pharmacy",
        panel_key,
        {"url": iframe_url},
    )

    _LOGGER.info("Nöbetçi Eczane paneli eklendi: %s / %s", city, district)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry — panel kaldır."""
    data = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if data and "panel_key" in data:
        frontend.async_remove_panel(hass, data["panel_key"])
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True
