"""
PixelDrop - piksel-art maskotlu, masaustunde yasayan hafif bir
su icme hatirlaticisi (Windows).

Uygulama kodu burada modullere ayrilmis durumda (bkz. kok dizindeki
pixeldropyolharitasi.md, madde 3.1):

- config: config.json okuma/yazma, gocler, varsayilanlar
- i18n: Turkce/Ingilizce metinler (i18n/tr.json, i18n/en.json)
- notify: winotify/winsound bildirimleri
- core.timer: hatirlatma zamanlamasi, erteleme (saf fonksiyonlar)
- core.tracker: gunluk sayac, hedef, seri, gecmis (saf fonksiyonlar)
- core.idle: bosta/uzakta suresi olcumu (Windows API)
- core.startup: Windows baslangicinda calistirma kaydi
- ui.mascot: Pillow ile piksel-art karakter/simge cizimi
- ui.widget: ana maskot penceresi (WaterReminderApp)
- ui.settings: ayarlar penceresi
- ui.tray: sistem tepsisi entegrasyonu (pystray)
"""

__version__ = "1.0.0"
