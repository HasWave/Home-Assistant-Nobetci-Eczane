# 💊 HasWave Nöbetçi Eczane

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.6%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**İl ve ilçe bazlı nöbetçi eczane bilgilerini Home Assistant'a sensor olarak ekler**

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

<a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=HasWave&repository=HACS-Nobetci-Eczane&category=Integration" target="_blank">
  <img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.">
</a>

</div>

---

## 📋 Özellikler

* 💊 **Nöbetçi Eczaneler** - İl ve ilçe bazlı güncel nöbetçi eczane bilgileri
* ✅ **Config Flow** - Kolay kurulum ve yapılandırma
* 📍 **Adres ve Telefon** - Eczane adresi, telefon ve harita linki
* 🔄 **Otomatik Güncelleme** - Belirli aralıklarla otomatik veri güncelleme
* 🗺️ **Harita Entegrasyonu** - Google Maps linkleri
* 📞 **Telefon Formatı** - Otomatik telefon numarası formatlama
* 📊 **Statistics** - Home Assistant statistics sayfasında görünür

## 🚀 Hızlı Başlangıç

### 1️⃣ HACS ile Kurulum

1. Home Assistant → **HACS** → **Integrations**
2. Sağ üstteki **⋮** menüsünden **Custom repositories** seçin
3. Repository URL: `https://github.com/HasWave/HACS-Nobetci-Eczane`
4. Category: **Integration** seçin
5. **Add** butonuna tıklayın
6. HACS → Integrations → **HasWave Nöbetçi Eczane**'yi bulun
7. **Download** butonuna tıklayın
8. Home Assistant'ı yeniden başlatın

### 2️⃣ Manuel Kurulum

1. Bu repository'yi klonlayın veya indirin
2. `custom_components/haswave_nobetci_eczane` klasörünü Home Assistant'ın `config/custom_components/` klasörüne kopyalayın
3. Home Assistant'ı yeniden başlatın

### 3️⃣ Integration Ekleme

1. Home Assistant → **Settings** → **Devices & Services**
2. Sağ alttaki **+ ADD INTEGRATION** butonuna tıklayın
3. **HasWave Nöbetçi Eczane** arayın ve seçin
4. Yapılandırma formunu doldurun:
   - **İl**: Büyük harf ile il adı (örn: `TEKİRDAĞ`, `İSTANBUL`, `ANKARA`)
   - **İlçe**: Büyük harf ile ilçe adı (örn: `ÇERKEZKÖY`, `KADIKÖY`, `ÇANKAYA`)
   - **API URL**: Varsayılan: `https://api.haswave.com/api/v1/eczane`
   - **Güncelleme Aralığı**: Saniye cinsinden (varsayılan: 3600 = 1 saat)
   - **Limit**: Maksimum eczane sayısı (0 = tümü, varsayılan: 0)
5. **Submit** butonuna tıklayın

**✅ Sensor'lar Otomatik Oluşturulur:** Integration eklendiğinde sensor'lar direkt Home Assistant'a eklenir. Hiçbir ek kurulum gerekmez!

## 📖 Kullanım

### Home Assistant Sensor'ları

Integration otomatik olarak şu sensor'ları oluşturur:

#### `sensor.haswave_nobetci_eczane_count`
Nöbetçi eczane sayısı (statistics için)

#### `sensor.haswave_nobetci_eczane_1`
1. eczane adı (attributes içinde telefon, adres, harita linki)

#### `sensor.haswave_nobetci_eczane_2`
2. eczane adı (attributes içinde telefon, adres, harita linki)

#### ... (maksimum 5 eczane)

Her eczane sensor'ının attributes'ları:
- `phone`: Formatlanmış telefon numarası (örn: `0282 717 8529`)
- `address`: Eczane adresi
- `map_link`: Google Maps linki

### Dashboard Kartı

#### Basit Entities Kartı

Lovelace UI'da kart ekleyin:

```yaml
type: entities
title: Nöbetçi Eczaneler
entities:
  - entity: sensor.haswave_nobetci_eczane_count
    name: Nöbetçi Eczane Sayısı
    icon: mdi:stethoscope
  - entity: sensor.haswave_nobetci_eczane_1
    name: En Yakın Eczane
    icon: mdi:stethoscope
```

#### Mushroom Template Card Örneği (Önerilen)

Daha güzel görünüm için Mushroom Template Card kullanabilirsiniz:

```yaml
type: vertical-stack
cards:
  - type: horizontal-stack
    cards:
      - type: custom:mushroom-template-card
        primary: "{{ states('sensor.haswave_nobetci_eczane_1') }}"
        secondary: |-
          📞 {{ state_attr('sensor.haswave_nobetci_eczane_1', 'phone') }}
        icon: mdi:stethoscope
        icon_color: red
        entity: sensor.haswave_nobetci_eczane_1
      - type: custom:mushroom-template-card
        primary: "{{ states('sensor.haswave_nobetci_eczane_2') }}"
        secondary: |-
          📞 {{ state_attr('sensor.haswave_nobetci_eczane_2', 'phone') }}
        icon: mdi:stethoscope
        icon_color: red
        entity: sensor.haswave_nobetci_eczane_2
```

**Not:** Mushroom Cards kullanmak için [Mushroom Cards](https://github.com/piitaya/lovelace-mushroom) eklentisini yüklemeniz gerekir.

### Otomasyon Örneği

Eczane bilgilerini kullanarak bildirim gönderme:

```yaml
automation:
  - alias: "Nöbetçi Eczane Bilgisi"
    trigger:
      - platform: time
        at: "20:00:00"  # Her akşam 20:00'de
    action:
      - service: notify.mobile_app
        data:
          title: "💊 Nöbetçi Eczane"
          message: >
            {{ states('sensor.haswave_nobetci_eczane_1') }}
            📞 {{ state_attr('sensor.haswave_nobetci_eczane_1', 'phone') }}
            📍 {{ state_attr('sensor.haswave_nobetci_eczane_1', 'address') }}
```

## 🔧 Gelişmiş Kullanım

### Eczane Sayısı Limitleme

Belirli sayıda eczane göstermek için integration ayarlarından `limit` değerini ayarlayabilirsiniz. Bu ayar ile sadece ilk N eczane gösterilir.

### Performans Optimizasyonu

* **Güncelleme Aralığı** değerini artırarak API çağrı sayısını azaltabilirsiniz (eczane bilgileri günlük değiştiği için 1 saat yeterlidir)
* **Limit** değerini ayarlayarak sadece ihtiyacınız olan kadar eczane bilgisi alabilirsiniz

### Sorun Giderme

#### Sensor'lar Görünmüyor

* Integration'ın eklendiğini kontrol edin: **Settings** → **Devices & Services**
* Home Assistant'ı yeniden başlatın
* Sensor'ları **Settings** → **Devices & Services** → **Entities** bölümünden kontrol edin
* Logları kontrol edin: **Settings** → **System** → **Logs**

#### API Hatası

* İnternet bağlantınızı kontrol edin
* API URL ayarının doğru olduğundan emin olun
* İl ve ilçe değerlerinin büyük harf olduğundan emin olun
* Logları kontrol edin

#### Eczane Bilgileri Güncellenmiyor

* Güncelleme aralığı değerini kontrol edin
* Logları kontrol edin: **Settings** → **System** → **Logs**
* API'nin çalıştığını kontrol edin: `https://api.haswave.com/api/v1/eczane?il=TEKİRDAĞ&ilce=ÇERKEZKÖY`

#### Integration Ekleme Hatası

* HACS üzerinden doğru şekilde yüklendiğinden emin olun
* Home Assistant'ı yeniden başlatın
* `custom_components` klasörünün doğru konumda olduğundan emin olun

## 📁 Dosya Yapısı

```
HACS-Nobetci-Eczane/
├── custom_components/
│   └── haswave_nobetci_eczane/
│       ├── __init__.py
│       ├── manifest.json
│       ├── const.py
│       ├── api.py
│       ├── sensor.py
│       └── config_flow.py
├── hacs.json
└── README.md
```

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen:

1. Bu repository'yi fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Bir Pull Request açın

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👨‍💻 Geliştirici

**HasWave**

🌐 [HasWave](https://haswave.com) | 📱 [Telegram](https://t.me/HasWave) | 📦 [GitHub](https://github.com/HasWave)

---

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!

Made with ❤️ by HasWave
