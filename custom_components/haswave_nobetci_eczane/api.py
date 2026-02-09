"""Eczaneleri.net iframe kaynağından nöbetçi eczane verisi çeker."""
from __future__ import annotations

import logging
import re
from typing import Any
from urllib.parse import quote

from bs4 import BeautifulSoup

from .const import ECZANELERI_NET_URL

_LOGGER = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def _normalize_phone(phone: str) -> str:
    digits = "".join(filter(str.isdigit, phone))
    if len(digits) == 12 and digits.startswith("90"):
        digits = "0" + digits[2:]
    return digits or phone


def _parse_eczaneleri_net_html(
    html: str, limit: int, il_adi: str, ilce_adi: str
) -> list[dict[str, Any]]:
    """
    Eczaneleri.net iframe HTML'ini parse eder.
    İçeriğe göre eşleştirir: tel: -> phone, maps -> map_link, eczaneleri.net link -> name, uzun metin -> address.
    """
    pharmacies: list[dict[str, Any]] = []
    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception as e:
        _LOGGER.warning("HTML parse hatası: %s", e)
        return []

    # list-group sınıfına sahip ul veya herhangi çok sayıda li içeren ul
    def _has_list_group(c: Any) -> bool:
        if not c:
            return False
        classes = c if isinstance(c, list) else (c.split() if isinstance(c, str) else [])
        return "list-group" in classes

    ul_list = soup.find_all("ul", class_=_has_list_group)
    if not ul_list:
        # Alternatif: class içinde "list" geçen ul
        ul_list = soup.find_all("ul", class_=re.compile(r"list", re.I))

    for ul in ul_list:
        if len(pharmacies) >= limit:
            break
        list_items = ul.find_all("li")
        if len(list_items) < 2:
            continue

        item = {
            "name": "",
            "address": "",
            "phone": "",
            "map_link": "",
            "il_ilce": f"{il_adi} / {ilce_adi}",
        }

        for li in list_items:
            text = li.get_text(strip=True)
            # Telefon: tel: içeren link
            a_tel = li.find("a", href=re.compile(r"^tel:", re.I))
            if a_tel:
                item["phone"] = _normalize_phone(a_tel.get_text(strip=True) or a_tel.get("href", ""))

            # Harita: google maps linki
            a_map = li.find("a", href=re.compile(r"google\.com/maps|maps\.google|maps\?q=", re.I))
            if a_map and a_map.get("href"):
                item["map_link"] = (a_map["href"] or "").strip()

            # Eczane adı: eczaneleri.net detay sayfası linki (il.eczaneleri.net/...)
            a_eczane = li.find("a", href=re.compile(r"eczaneleri\.net", re.I))
            if a_eczane and a_eczane.get("href") and "iframe" not in (a_eczane.get("href") or ""):
                name_candidate = a_eczane.get_text(strip=True)
                if name_candidate and len(name_candidate) > 2:
                    item["name"] = name_candidate

            # Adres: uzun metin satırı (genelde büyük harf, 20+ karakter, tel/maps linki değil)
            if len(text) > 20 and not text.startswith("http") and "Tekirdağ" not in text and " - " not in text[:30]:
                if not li.find("a", href=re.compile(r"^tel:", re.I)) and not li.find("a", href=re.compile(r"maps")):
                    if len(text) > len(item["address"]):
                        item["address"] = text

        # Eczane adı bulunamadıysa: ilk anlamlı li metnini (kısa isim) veya son li'yi dene
        if not item["name"] and list_items:
            for li in list_items:
                t = li.get_text(strip=True)
                if 3 <= len(t) <= 80 and not t.startswith("0") and "Yol Tarifi" not in t and "Ara" != t:
                    if not re.match(r"^[\d\s\-+]+$", t) and "http" not in t:
                        item["name"] = t
                        break
            if not item["name"] and list_items:
                item["name"] = list_items[-1].get_text(strip=True) or list_items[0].get_text(strip=True)

        if item["name"]:
            pharmacies.append(item)

    return pharmacies


async def fetch_pharmacies_async(
    session, city: str, district: str = "", limit: int = 5
) -> list[dict[str, Any]] | None:
    """
    Eczaneleri.net iframe URL'sinden veri çeker (aiohttp session ile).
    session: aiohttp ClientSession (hass.helpers.aiohttp_client.async_get_clientsession)
    """
    city = (city or "").strip()
    district = (district or "").strip()
    limit = max(1, min(20, limit))
    ilce_adi = district if district else city

    url = ECZANELERI_NET_URL.format(
        city=quote(city, safe=""),
        county=quote(ilce_adi, safe=""),
    )
    _LOGGER.debug("Eczaneleri.net isteği: %s", url)

    try:
        from aiohttp import ClientTimeout
        timeout = ClientTimeout(total=15)
        resp = await session.get(
            url,
            timeout=timeout,
            headers={"User-Agent": USER_AGENT},
        )
        resp.raise_for_status()
        raw = await resp.read()
        text = raw.decode("utf-8", errors="replace")
        if not text.strip():
            _LOGGER.warning("Eczaneleri.net boş yanıt (İl: %s, İlçe: %s)", city, district or "Yok")
            return []

        pharmacies = _parse_eczaneleri_net_html(text, limit, city, ilce_adi)
        if pharmacies:
            _LOGGER.info(
                "Eczaneleri.net: %s eczane alındı (İl: %s, İlçe: %s)",
                len(pharmacies),
                city,
                district or "Yok",
            )
        else:
            _LOGGER.warning(
                "Eczaneleri.net: eczane bulunamadı veya parse edilemedi (İl: %s, İlçe: %s)",
                city,
                district or "Yok",
            )
        return pharmacies
    except Exception as e:
        _LOGGER.error("Eczaneleri.net hatası: %s", e, exc_info=True)
        return None


class HasWaveEczaneAPI:
    """Eczaneleri.net iframe'den nöbetçi eczane verisi (async veya sync wrapper)."""

    def __init__(self, city: str, district: str = "", limit: int = 5) -> None:
        self.city = (city or "").strip()
        self.district = (district or "").strip()
        self.limit = max(1, min(20, limit))

    async def async_fetch(self, session) -> list[dict[str, Any]] | None:
        """Async: aiohttp session ile veri çek."""
        return await fetch_pharmacies_async(
            session, self.city, self.district, self.limit
        )

    def fetch_pharmacies(self) -> list[dict[str, Any]] | None:
        """Sync: requests ile (config flow / executor için)."""
        try:
            import requests
            ilce_adi = self.district if self.district else self.city
            url = ECZANELERI_NET_URL.format(
                city=quote(self.city, safe=""),
                county=quote(ilce_adi, safe=""),
            )
            response = requests.get(
                url,
                timeout=15,
                headers={"User-Agent": USER_AGENT},
            )
            response.raise_for_status()
            response.encoding = "utf-8"
            text = response.text
            if not text.strip():
                return []
            return _parse_eczaneleri_net_html(
                text, self.limit, self.city, ilce_adi
            )
        except Exception as e:
            _LOGGER.error("Eczaneleri.net (sync) hatası: %s", e, exc_info=True)
            return None
