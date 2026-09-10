"""Config.json okuma/yazma, eski isimden goc, varsayilan degerler."""

import json
import os
from datetime import date

APP_NAME = "PixelDrop"
APP_TITLE = "PixelDrop"
# Eski isim (Su Icme Hatirlatici) altinda biriken ayar/gecmis kaybolmasin
# diye config_path() bunu bir kereye mahsus goc icin kullanir; Windows
# baslangic kaydinda da eski isimle kalmis olabilecek girdiyi temizlemek
# icin core.startup.set_startup() bunu kullanir.
OLD_APP_NAME = "SuIcmeHatirlatici"

DEFAULT_CONFIG = {
    "interval_minutes": 45,
    "paused": False,
    "drank_today": 0,
    "last_reset_date": str(date.today()),
    "run_at_startup": False,
    "sound": True,
    "widget_visible": True,
    "widget_x": None,
    "widget_y": None,
    "widget_size": 140,
    "daily_goal": 8,
    "streak": 0,
    "history": {},
    "auto_pause_enabled": True,
    "language": "tr",
}

INTERVAL_CHOICES = [15, 30, 45, 60, 90, 120]
GOAL_CHOICES = [4, 6, 8, 10, 12, 15]

# Widget (karakter) boyutu sinirlari - ayarlar penceresindeki kaydiraktan
# secilebilir aralik.
WIDGET_SIZE_DEFAULT = 140
WIDGET_MIN = 90
WIDGET_MAX = 220


def config_path():
    base = os.getenv("APPDATA") or os.path.expanduser("~")
    d = os.path.join(base, APP_NAME)
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "config.json")


def _old_config_path():
    base = os.getenv("APPDATA") or os.path.expanduser("~")
    return os.path.join(base, OLD_APP_NAME, "config.json")


def _migrate_old_config_if_needed():
    """Uygulama "Su Icme Hatirlatici" -> "PixelDrop" olarak yeniden
    adlandirilinca config klasoru de degisti; eski klasordeki (gunluk
    sayac, seri, gecmis, widget konumu vb.) ayarlari bir kereye mahsus
    yeni klasore kopyalar ki gecmis veri kaybolmasin."""
    new_path = config_path()
    if os.path.exists(new_path):
        return
    old_path = _old_config_path()
    if not os.path.exists(old_path):
        return
    try:
        with open(old_path, "r", encoding="utf-8") as f:
            data = f.read()
        with open(new_path, "w", encoding="utf-8") as f:
            f.write(data)
    except Exception:
        pass


def load_config():
    """config.json'u okur; dosya yoksa, bozuksa ya da eksik alanlar
    icerse varsayilanlar uzerine guvenli sekilde katmanlanir - uygulama
    hicbir zaman bozuk bir config yuzunden coker."""
    _migrate_old_config_if_needed()
    path = config_path()
    cfg = dict(DEFAULT_CONFIG)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg.update(json.load(f))
        except Exception:
            pass
    return cfg


def save_config(cfg):
    try:
        with open(config_path(), "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass
