"""API client for HasWave Nöbetçi Eczane."""
from __future__ import annotations

import logging
from typing import Any
import requests

_LOGGER = logging.getLogger(__name__)


class HasWaveEczaneAPI:
    """API client for HasWave Nöbetçi Eczane."""
    
    def __init__(self, api_url: str, city: str, district: str = "", limit: int = 0) -> None:
        """Initialize the API client."""
        self.api_url = api_url
        self.city = city
        self.district = district
        self.limit = limit
    
    def fetch_pharmacies(self) -> list[dict[str, Any]] | None:
        """Fetch pharmacies from the API."""
        try:
            params = {
                "il": self.city,
            }
            
            if self.district:
                params["ilce"] = self.district
            
            if self.limit > 0:
                params["limit"] = self.limit
            
            response = requests.get(self.api_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                _LOGGER.debug(f"API yanıtı: {type(data)}, Keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
                
                if isinstance(data, dict):
                    pharmacies = data.get("data") or data.get("eczaneler", [])
                    _LOGGER.info(f"API'den {len(pharmacies)} eczane verisi alındı")
                    return pharmacies
                elif isinstance(data, list):
                    _LOGGER.info(f"API'den {len(data)} eczane verisi alındı (liste formatında)")
                    return data
            else:
                _LOGGER.error(f"HTTP hatası: {response.status_code} - {response.text}")
                
        except Exception as e:
            _LOGGER.error(f"API bağlantı hatası: {e}")
        
        return []

