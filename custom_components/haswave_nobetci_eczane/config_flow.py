"""Config flow for HasWave Nöbetçi Eczane — api.haswave.com kullanılmaz."""
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

from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL, DEFAULT_SENSOR_COUNT
from .api import fetch_pharmacies

_LOGGER = logging.getLogger(__name__)


def _load_strings() -> dict:
    """Load strings.json file."""
    strings_path = Path(__file__).parent / "strings.json"
    try:
        with open(strings_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        _LOGGER.warning("Strings dosyası yüklenemedi: %s", e)
        return {}


def _get_schema(strings: dict | None = None) -> vol.Schema:
    """Get schema with localized strings."""
    if strings is None:
        strings = _load_strings()
    return vol.Schema(
        {
            vol.Required("city", default=""): str,
            vol.Optional("district", default=""): str,
            vol.Optional("update_interval", default=DEFAULT_UPDATE_INTERVAL): int,
            vol.Optional("limit", default=0): int,
            vol.Optional("sensor_count", default=DEFAULT_SENSOR_COUNT): vol.Coerce(int),
        }
    )


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate user input and test eczaneleri.net bağlantısı."""
    city = (data.get("city") or "").strip()
    district = (data.get("district") or "").strip()
    if not city:
        raise ValueError("city_required")
    if not district:
        district = city

    sensor_count = data.get("sensor_count", DEFAULT_SENSOR_COUNT)
    if isinstance(sensor_count, str):
        try:
            sensor_count = int(sensor_count)
        except (ValueError, TypeError):
            sensor_count = DEFAULT_SENSOR_COUNT
    if sensor_count < 1 or sensor_count > 10:
        raise ValueError("invalid_sensor_count")

    result = await hass.async_add_executor_job(
        fetch_pharmacies,
        city,
        district,
        data.get("limit", 0) or 0,
    )
    if result is None:
        raise CannotConnect

    title = f"Nöbetçi Eczane — {city}"
    if district and district != city:
        title += f" / {district}"
    return {"title": title}


class CannotConnect(HomeAssistantError):
    """Bağlantı hatası."""


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for HasWave Nöbetçi Eczane."""

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
        except ValueError as e:
            key = str(e)
            errors["base"] = error_strings.get(key, key)
        except CannotConnect:
            errors["base"] = error_strings.get("cannot_connect", "cannot_connect")
        except Exception:
            _LOGGER.exception("Beklenmeyen hata")
            errors["base"] = error_strings.get("unknown", "unknown")
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_get_schema(strings),
            errors=errors,
        )
