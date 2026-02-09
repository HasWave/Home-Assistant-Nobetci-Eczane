"""Eczaneleri.net iframe kaynağından nöbetçi eczane verisi çeker."""
from __future__ import annotations

import logging
import re
from typing import Any
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from .const import ECZANELERI_NET_URL

_LOGGER = logging.getLogger(__name__)

USER_AGENT = "HasWave-API/1.0"


def _normalize_phone(phone: str) -> str:
    digits = "".join(filter(str.isdigit, phone))
    if len(digits) == 12 and digits.startswith("90"):
        digits = "0" + digits[2:]
    return digits or phone


def _parse_eczaneleri_net_html(html: str, limit: int, il_adi: str, ilce_adi: str) -> list[dict[str, Any]]:
    """
    Eczaneleri.net iframe HTML'ini parse eder.
    ul.list-group blokları, li[0]=ad, li[2]=adres, li[3]=telefon; harita linki a href'ten.
    """
    pharmacies: list[dict[str, Any]] = []
    soup = BeautifulSoup(html, "html.parser")

    # list-group sınıfına sahip ul elementlerini bul
    def _has_list_group(c: Any) -> bool:
        if not c:
            return False
        classes = c if isinstance(c, list) else (c.split() if isinstance(c, str) else [])
        return "list-group" in classes

    ul_list = soup.find_all("ul", class_=_has_list_group)

    for ul in ul_list:
        if len(pharmacies) >= limit:
            break
        list_items = ul.find_all("li")
        if len(list_items) < 4:
            continue

        # li[0]=ad, li[2]=adres, li[3]=telefon
        name = list_items[0].get_text(strip=True) if list_items else ""
        address = list_items[2].get_text(strip=True) if len(list_items) > 2 else ""
        phone_raw = list_items[3].get_text(strip=True) if len(list_items) > 3 else ""
        phone = _normalize_phone(phone_raw)

        # Yol Tarifi / Harita linki: li içinde google.com/maps veya maps içeren a
        map_link = ""
        for li in list_items:
            a = li.find("a", href=re.compile(r"google\.com/maps|maps\.google|maps\?q=", re.I))
            if a and a.get("href"):
                map_link = (a["href"] or "").strip()
                break

        if not name:
            continue
        pharmacies.append({
            "name": name,
            "address": address,
            "phone": phone,
            "map_link": map_link,
            "il_ilce": f"{il_adi} / {ilce_adi}",
        })
    return pharmacies


class HasWaveEczaneAPI:
    """Eczaneleri.net iframe'den nöbetçi eczane verisi çeker."""

    def __init__(self, city: str, district: str = "", limit: int = 5) -> None:
        self.city = (city or "").strip()
        self.district = (district or "").strip()
        self.limit = max(1, min(20, limit))

    def fetch_pharmacies(self) -> list[dict[str, Any]] | None:
        """Eczaneleri.net iframe URL'sinden veri çeker ve HTML parse eder."""
        try:
            # İlçe boşsa il merkezini kullan; URL encode
            ilce_adi = self.district if self.district else self.city
            url = ECZANELERI_NET_URL.format(
                city=quote(self.city, safe=""),
                county=quote(ilce_adi, safe=""),
            )
            _LOGGER.debug("Eczaneleri.net isteği: %s", url)

            response = requests.get(
                url,
                timeout=15,
                headers={"User-Agent": USER_AGENT},
            )
            response.raise_for_status()
            text = response.text
            if not text.strip():
                _LOGGER.warning(
                    "Eczaneleri.net boş yanıt (İl: %s, İlçe: %s)",
                    self.city,
                    self.district or "Yok",
                )
                return []

            pharmacies = _parse_eczaneleri_net_html(
                text,
                self.limit,
                self.city,
                ilce_adi,
            )
            if pharmacies:
                _LOGGER.info(
                    "Eczaneleri.net: %s eczane alındı (İl: %s, İlçe: %s)",
                    len(pharmacies),
                    self.city,
                    self.district or "Yok",
                )
            else:
                _LOGGER.warning(
                    "Eczaneleri.net: eczane bulunamadı veya parse edilemedi (İl: %s, İlçe: %s)",
                    self.city,
                    self.district or "Yok",
                )
            return pharmacies
        except requests.RequestException as e:
            _LOGGER.error("Eczaneleri.net bağlantı hatası: %s", e, exc_info=True)
            return None
        except Exception as e:
            _LOGGER.error("Eczaneleri.net işlem hatası: %s", e, exc_info=True)
            return None
