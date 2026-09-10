# Changelog

Bu projedeki önemli değişiklikler bu dosyada tutulur. Format
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) temel alınarak
düzenlenmiştir.

## [Yayınlanmamış]

### Eklendi

- `main.py` (~1400 satır), test edilebilir ve bakımı kolay bir `pixeldrop/`
  paketine bölündü: `config`, `i18n`, `notify`, `core/` (timer, tracker,
  idle, startup) ve `ui/` (widget, settings, tray, mascot). Kök dizindeki
  `main.py` artık sadece bu paketi çağıran ince bir başlatıcı —
  `python main.py` ve `exe_olustur.bat` eskisi gibi çalışmaya devam eder.
- Diller koddan çıkarılıp `pixeldrop/i18n/tr.json` ve `en.json`
  dosyalarına taşındı; üçüncü bir dil eklemek artık kod değişikliği
  gerektirmiyor.
- Tek bir `__version__` (`pixeldrop/__init__.py`) eklendi; ayarlar
  penceresinde ve tepsi ikonunun ipucunda görünüyor.
- `ruff` + `mypy`, `pyproject.toml` ile yapılandırıldı
  (`requirements-dev.txt`).
- `core/timer.py` ve `core/tracker.py`'deki gün dönümü, seri hesabı,
  geçmiş budama mantığı saf fonksiyonlara ayrıldı (tarih/zaman parametre
  olarak alınır, `datetime.now()` çağrılmaz) ve 38 `pytest` testiyle
  kaplandı: gün dönümü, seri artışı/sıfırlanması, atlanan günler, 14 günlük
  geçmiş budaması, bozuk `config.json`'dan kurtarma, eski isimden
  (`SuIcmeHatirlatici`) göç, çeviri anahtarı geri dönüşü.
- Her push'ta testleri otomatik çalıştıran bir GitHub Actions iş akışı
  eklendi (`.github/workflows/tests.yml`).

### Değişti

- `exe_olustur.bat`, yeni `pixeldrop/i18n/*.json` dosyalarını pakete dahil
  etmesi için `--add-data` parametresiyle güncellendi.

### Eklenecek

- Bkz. [pixeldropyolharitasi.md](pixeldropyolharitasi.md) — kalan yeni
  özellikler (ml bazlı miktar takibi, bildirimden kayıt, sessiz saatler,
  maskot çeşitleri, genişletilmiş istatistikler ve daha fazlası) için
  planlanan yol haritası.

## [1.0.0] - 2026-08

İlk yayın. Proje eskiden "Su İçme Hatırlatıcı" adıyla geliştirildi, bu
sürümde **PixelDrop** olarak yeniden markalandı.

### Eklendi

- Ekranda yaşayan, sürüklenebilir, çerçevesiz piksel-art bir su damlası
  maskotu; zamanla mutlu → nötr → susamış → acil durumuna geçen ifadeler.
- Tek tıkla "su içtim" kaydı, sürükle-bırak ile konum değiştirme.
- Fareyle üzerine gelince beliren erteleme (💤), ayarlar (⚙) ve gizleme (✕)
  simgeleri.
- Kademeli kuruma efekti: su içilmedikçe karakterin rengi yavaşça
  soluklaşır/kırmızımsıya döner.
- İlerleme çubuğu ve geri sayım metni.
- Günlük hedef + seri (streak) takibi: bardak simgeleriyle günlük ilerleme,
  gece yarısı otomatik sıfırlama, hedefe ulaşılan günlerde seri artışı.
- Boşta/uzaktayken otomatik duraklama (`GetLastInputInfo` ile).
- Bildirimden hızlı erteleme (5 dakika).
- Ayarlar penceresinde son 7 günün mini geçmiş grafiği.
- Türkçe / İngilizce tam arayüz desteği (widget, tepsi menüsü, ayarlar,
  bildirimler).
- Sistem tepsisi (tray) entegrasyonu — `pystray` ile.
- Ayarlanabilir hatırlatma aralığı (15–120 dk) ve günlük hedef (4–15 bardak).
- Duraklat/devam et, bildirim sesi aç/kapa, Windows başlangıcında çalıştır.
- Native Windows 10/11 toast bildirimi (`winotify`) + yedek sistem sesi
  (`winsound`).
- Tek klasörlük, konsolsuz `.exe` paketleme desteği (PyInstaller).
- `SuIcmeHatirlatici` → `PixelDrop` adı ve `config.json` konumu için
  kayıpsız, tek seferlik otomatik geçiş (migration).

### Değişti

- Paketleme `--onefile` yerine `--onedir` + `--noupx` moduna geçirildi;
  PyInstaller ile derlenmiş exe'lerde sık görülen antivirüs/Chrome yanlış
  pozitiflerini azaltmak için.

### Düzeltildi

- Windows'un `-transparentcolor` katmanlı penceresinin kısmi saydam
  pikselleri (anti-alias yazı, emoji, yumuşak kenarlı ikonlar) arka plan
  rengiyle karıştırıp bıraktığı pembe/mor halka artefaktı — tüm özel
  çizimler artık tam opak (binarize edilmiş alfa) olarak render ediliyor.
