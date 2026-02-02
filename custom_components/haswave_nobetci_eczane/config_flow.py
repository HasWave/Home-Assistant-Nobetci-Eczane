from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

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
    step_strings = strings.get("config", {}).get("step", {}).get("user", {})
    return vol.Schema(
        {
            vol.Required("city", default=""): str,
            vol.Optional("district", default=""): str,
        }
    )


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HasWave Nöbetçi Eczane (iframe)."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step — sadece il ve ilçe (API yok)."""
        strings = _load_strings()
        step_strings = strings.get("config", {}).get("step", {}).get("user", {})

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=_get_schema(strings),
            )

        city = (user_input.get("city") or "").strip()
        district = (user_input.get("district") or "").strip()

        if not city:
            return self.async_show_form(
                step_id="user",
                data_schema=_get_schema(strings),
                errors={"base": "city_required"},
            )

        title = f"Nöbetçi Eczane — {city}"
        if district:
            title += f" / {district}"

        return self.async_create_entry(title=title, data=user_input)
