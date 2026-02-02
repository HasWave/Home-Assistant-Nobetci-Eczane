from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)


def fetch_pharmacies(city: str, district: str, limit: int = 0) -> list[dict[str, Any]] | None:
    if not city:
        _LOGGER.warning("İl boş, veri çekilmiyor")
        return None
    if not district:
        district = city

    url = (
        "https://eczaneleri.net/api/new-iframe?"
        f"type=default-iframe&city={quote(city)}&county={quote(district)}&color1=00d2d3&color2=17a2b8"
    )

    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "HasWave-HACS/1.0"})
        resp.raise_for_status()
        html = resp.text
    except requests.RequestException as e:
        _LOGGER.error("Eczaneleri.net isteği başarısız: %s", e)
        return None

    try:
        soup = BeautifulSoup(html, "html.parser")
    except Exception as e:
        _LOGGER.error("HTML parse hatası: %s", e)
        return None

    # ul.list-group benzeri tüm ul'ları bul
    uls = soup.find_all("ul", class_=lambda c: c and "list-group" in (c if isinstance(c, str) else " ".join(c)))
    data: list[dict[str, Any]] = []

    for ul in uls:
        lis = ul.find_all("li")
        if len(lis) < 4:
            continue

        name = (lis[0].get_text(strip=True) or "").strip()
        if not name:
            continue

        address = (lis[2].get_text(strip=True) if len(lis) > 2 else "") or ""
        phone = (lis[3].get_text(strip=True) if len(lis) > 3 else "") or ""
        map_link = ""

        for li in lis:
            text = li.get_text(strip=True) or ""
            if "Yol Tarifi" in text or "Harita" in text:
                a = li.find("a", href=True)
                if a and ("google.com/maps" in a["href"] or "maps" in a["href"]):
                    map_link = a["href"].strip()
                    break

        data.append({
            "name": name,
            "il_ilce": f"{city} / {district}",
            "phone": phone,
            "address": address,
            "map_link": map_link,
        })

    if limit > 0:
        data = data[:limit]

    _LOGGER.debug("Eczaneleri.net: %s / %s -> %d eczane", city, district, len(data))
    return data
