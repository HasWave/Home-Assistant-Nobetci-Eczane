"""Config flow for HasWave Nöbetçi Eczane integration."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, DEFAULT_API_URL, DEFAULT_UPDATE_INTERVAL, DEFAULT_SENSOR_COUNT
from .api import HasWaveEczaneAPI

_LOGGER = logging.getLogger(__name__)


def _load_strings() -> dict:
    """Load strings.json file."""
    strings_path = Path(__file__).parent / "strings.json"
    try:
        with open(strings_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        _LOGGER.warning(f"Strings dosyası yüklenemedi: {e}")
        return {}

def _get_schema(strings: dict | None = None) -> vol.Schema:
    """Get schema with localized strings."""
    if strings is None:
        strings = _load_strings()
    
    step_strings = strings.get("config", {}).get("step", {}).get("user", {})
    data_strings = step_strings.get("data", {})
    
    # Home Assistant otomatik olarak strings.json'dan label'ları alır
    # Ama manuel olarak da ekleyebiliriz
    return vol.Schema(
        {
            vol.Required("city"): str,
            vol.Optional("district", default=""): str,
            vol.Optional("api_url", default=DEFAULT_API_URL): str,
            vol.Optional("update_interval", default=DEFAULT_UPDATE_INTERVAL): int,
            vol.Optional("limit", default=0): int,
            vol.Optional("sensor_count", default=DEFAULT_SENSOR_COUNT): vol.Coerce(int),
        }
    )


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    # Sensor count kontrolü
    sensor_count = data.get("sensor_count", DEFAULT_SENSOR_COUNT)
    if isinstance(sensor_count, str):
        try:
            sensor_count = int(sensor_count)
        except (ValueError, TypeError):
            sensor_count = DEFAULT_SENSOR_COUNT
    
    if sensor_count < 1 or sensor_count > 10:
        raise ValueError("Sensor sayısı 1-10 arası olmalıdır")
    
    api = HasWaveEczaneAPI(
        api_url=data.get("api_url", DEFAULT_API_URL),
        city=data["city"],
        district=data.get("district", ""),
        limit=data.get("limit", 0),
    )
    
    result = await hass.async_add_executor_job(api.fetch_pharmacies)
    
    # None dönerse hata var demektir
    if result is None:
        raise CannotConnect
    
    # Boş liste de geçerli bir sonuçtur (sadece il ile de çalışabilir, eczane olmayabilir)
    if isinstance(result, list):
        if len(result) == 0:
            _LOGGER.info(f"API'den eczane verisi dönmedi (boş liste). İl: {data['city']}, İlçe: {data.get('district', 'Yok')}. Bu normal olabilir.")
        else:
            _LOGGER.info(f"API bağlantısı başarılı: {len(result)} eczane bulundu")
    
    return {"title": f"Nöbetçi Eczane - {data['city']}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HasWave Nöbetçi Eczane."""
    
    VERSION = 1
    
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        strings = _load_strings()
        step_strings = strings.get("config", {}).get("step", {}).get("user", {})
        error_strings = strings.get("config", {}).get("error", {})
        
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=_get_schema(strings),
            )
        
        errors = {}
        
        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = error_strings.get("cannot_connect", "cannot_connect")
        except ValueError as e:
            errors["base"] = error_strings.get("invalid_sensor_count", "invalid_sensor_count")
            _LOGGER.error(f"Geçersiz sensor sayısı: {e}")
        except Exception:
            _LOGGER.exception("Unexpected exception")
            errors["base"] = error_strings.get("unknown", "unknown")
        else:
            return self.async_create_entry(title=info["title"], data=user_input)
        
        return self.async_show_form(
            step_id="user",
            data_schema=_get_schema(strings),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

