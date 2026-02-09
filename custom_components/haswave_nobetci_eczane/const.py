"""Constants for HasWave Nöbetçi Eczane integration."""

DOMAIN = "haswave_nobetci_eczane"
# Eczaneleri.net iframe kaynağı
ECZANELERI_NET_URL = "https://eczaneleri.net/api/new-iframe?type=default-iframe&city={city}&county={county}&color1=00d2d3&color2=17a2b8"
# Güncelleme sıklığı (saniye) - kullanıcı ayarlardan seçer
CONF_UPDATE_INTERVAL = "update_interval"
DEFAULT_UPDATE_INTERVAL = 3600  # 1 saat
UPDATE_INTERVAL_1_HOUR = 3600
UPDATE_INTERVAL_24_HOURS = 86400
DEFAULT_SENSOR_COUNT = 5
