# 💊 HasWave Nöbetçi Eczane

<div align="center">

![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.6%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**İl ve ilçe bazlı nöbetçi eczane bilgilerini Home Assistant sensor olarak ekler**

**api.haswave.com kullanılmaz** — Veri doğrudan **eczaneleri.net**'ten alınır (PHP eczane.php ile aynı mantık).

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

<a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=HasWave&repository=Home-Assistant-Nobetci-Eczane&category=Integration" target="_blank">
  <img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.">
</a>

</div>

---

## 📋 Özellikler

* 💊 **Nöbetçi Eczaneler** — İl ve ilçe bazlı güncel liste
* ✅ **api.haswave.com yok** — Veri doğrudan eczaneleri.net'ten HTML parse edilir (PHP API ile aynı kaynak)
* 📍 **Sensor'lar** — Eczane adı, telefon, adres, harita linki (attributes)
* 🔄 **Otomatik güncelleme** — Güncelleme aralığı ayarlanabilir (varsayılan 1 saat)

## 🚀 Hızlı Başlangıç

### 1️⃣ HACS ile Kurulum

1. Home Assistant → **HACS** → **Integrations**
2. Sağ üstteki **⋮** menüsünden **Custom repositories** seçin
3. Repository URL: `https://github.com/HasWave/Home-Assistant-Nobetci-Eczane`
4. Category: **Integration** seçin
5. **Add** → HACS'ta **HasWave Nöbetçi Eczane**'yi bulun → **Download**
6. Home Assistant'ı yeniden başlatın

### 2️⃣ Integration Ekleme

1. **Settings** → **Devices & Services** → **+ ADD INTEGRATION**
2. **HasWave Nöbetçi Eczane** arayın ve seçin
3. **İl** (örn: TEKİRDAĞ, İSTANBUL), **İlçe** (opsiyonel), güncelleme aralığı, sensor sayısı girin
4. **Submit**

**Sensor'lar otomatik oluşturulur:** `sensor.haswave_nobetci_eczane_1`, `_2`, … (attributes: phone, address, map_link).

## 📖 Kullanım

- **Sensor'lar:** `sensor.haswave_nobetci_eczane_1` vb. — state = eczane adı; attributes: `phone`, `address`, `map_link`.
- **Dashboard:** Entities kartı veya Mushroom kart ile kullanabilirsiniz.

## 📁 Dosya Yapısı

```
custom_components/haswave_nobetci_eczane/
├── __init__.py
├── manifest.json
├── const.py
├── api.py          # eczaneleri.net HTML fetch + parse (api.haswave.com yok)
├── config_flow.py
├── sensor.py
└── strings.json
```

## 🔧 Sorun Giderme

* **Veri gelmiyor:** İl/ilçe büyük harf (TEKİRDAĞ, ÇERKEZKÖY). İnternet erişimi ve eczaneleri.net erişilebilir olmalı.
* **api.haswave.com:** Bu eklenti api.haswave.com sitesini **kullanmaz**; veri doğrudan eczaneleri.net'ten alınır.

## 📝 Lisans

MIT

## 👨‍🔧 Geliştirici

**HasWave** — [haswave.com](https://haswave.com) | [GitHub](https://github.com/HasWave)
