"""
PixelDrop baslatma dosyasi (geriye donuk uyumluluk icin).

Uygulama kodu artik `pixeldrop/` paketi altinda modullere ayrilmis
durumda (bkz. pixeldropyolharitasi.md, madde 3.1: config, i18n, notify,
core/, ui/). Bu dosya sadece eskiden beri kullanilan calistirma
yollarini (`python main.py`, `pythonw main.py`, exe_olustur.bat) hic
bozmadan kucuk bir baslatici olarak kaliyor - PyInstaller de giris
noktasi olarak bunu kullanmaya devam ediyor.
"""

from pixeldrop.__main__ import main

if __name__ == "__main__":
    main()
