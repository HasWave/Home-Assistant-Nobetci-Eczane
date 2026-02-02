# 💊 HasWave Nöbetçi Eczane

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.6%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**İl ve ilçe bazlı nöbetçi eczane bilgilerini iframe panel olarak gösterir (API kullanılmaz)**

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

<a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=HasWave&repository=Home-Assistant-Nobetci-Eczane&category=Integration" target="_blank">
  <img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.">
</a>

</div>

---

## 📋 Özellikler

* 💊 **Nöbetçi Eczaneler** — İl ve ilçe bazlı güncel liste (iframe ile)
* ✅ **API yok** — Veri doğrudan iframe içinde gösterilir, ek API çağrısı yapılmaz
* 🖥️ **Panel** — Home Assistant sidebar'da "Nöbetçi Eczane" paneli
* 📍 **Kolay kurulum** — Sadece il ve ilçe girin

## 🚀 Hızlı Başlangıç

### 1️⃣ HACS ile Kurulum

1. Home Assistant → **HACS** → **Integrations**
2. Sağ üstteki **⋮** menüsünden **Custom repositories** seçin
3. Repository URL: `https://github.com/HasWave/Home-Assistant-Nobetci-Eczane`
4. Category: **Integration** seçin
5. **Add** butonuna tıklayın
6. HACS → Integrations → **HasWave Nöbetçi Eczane**'yi bulun (ikon ve logo görünür)
7. **Download** butonuna tıklayın
8. Home Assistant'ı yeniden başlatın

### 2️⃣ Manuel Kurulum

1. Bu repository'yi klonlayın veya indirin
2. `custom_components/haswave_nobetci_eczane` klasörünü Home Assistant'ın `config/custom_components/` klasörüne kopyalayın
3. `brand` klasörünü (icon.png, logo.png) repository kökünde bırakın — HACS ikon ve logo için kullanır
4. Home Assistant'ı yeniden başlatın

### 3️⃣ Integration Ekleme

1. Home Assistant → **Settings** → **Devices & Services**
2. Sağ alttaki **+ ADD INTEGRATION** butonuna tıklayın
3. **HasWave Nöbetçi Eczane** arayın ve seçin (ikon ve logo görünür)
4. Yapılandırma formunu doldurun:
   - **İl**: Büyük harf ile il adı (örn: `TEKİRDAĞ`, `İSTANBUL`, `ANKARA`)
   - **İlçe**: Büyük harf ile ilçe adı (opsiyonel, örn: `ÇERKEZKÖY`, `KADIKÖY`)
5. **Submit** butonuna tıklayın

**✅ Panel otomatik eklenir:** Sidebar'da **Nöbetçi Eczane** paneli görünür; tıklayınca il/ilçe seçtiğiniz eczane listesi iframe ile açılır.

## 📖 Kullanım

- **Panel:** Sol menüde **Nöbetçi Eczane**'ye tıklayın. İl ve ilçe seçiminize göre eczane listesi (eczaneleri.net iframe) gösterilir.
- **API kullanılmaz** — Tüm veri iframe içinde yüklendiği için ek sunucu/API gerekmez.

## 📁 Dosya Yapısı

```
Home-Assistant-Nobetci-Eczane/
├── brand/
│   ├── icon.png   # HACS / HA entegrasyon listesi ikonu
│   └── logo.png   # HACS detay sayfası logosu
├── custom_components/
│   └── haswave_nobetci_eczane/
│       ├── __init__.py
│       ├── manifest.json
│       ├── const.py
│       ├── config_flow.py
│       ├── strings.json
│       └── api.py  # (boş, geriye dönük uyumluluk)
├── hacs.json
└── README.md
```

## 🔧 Sorun Giderme

* **Panel görünmüyor:** Integration'ı ekledikten sonra Home Assistant'ı yeniden başlatın.
* **Iframe boş:** İnternet bağlantınızı kontrol edin; iframe `https://api.haswave.com/eczane-iframe.php` ve eczaneleri.net erişilebilir olmalı.
* **İkon/logo HACS'ta görünmüyor:** Repository'de `brand/icon.png` ve `brand/logo.png` olduğundan emin olun.

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 👨‍🔧 Geliştirici

**HasWave** — 🌐 [haswave.com](https://haswave.com) | 📦 [GitHub](https://github.com/HasWave)

---

⭐ Beğendiyseniz yıldız vermeyi unutmayın!
