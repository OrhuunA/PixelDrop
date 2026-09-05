"""
PixelDrop - piksel-art maskotlu, masaustunde yasayan hafif bir
su icme hatirlaticisi (Windows).

TBH: Task Bar Hero mantiginda: kucuk bir karakter ekranda durur, zaman
gectikce "susar", tikladiginda / su ictiginde yenilenir. Arka planda
sadece tkinter'in after() dongusu ve pystray'in tepsi simgesi calisir -
ekstra thread/sleep dongusu yok, kaynak kullanimi dusuk kalir.
"""

import json
import os
import sys
import time
import math
from datetime import date, timedelta

import tkinter as tk

import pystray
from PIL import Image, ImageDraw, ImageFont, ImageTk

try:
    from winotify import Notification, audio
    HAS_WINOTIFY = True
except Exception:
    HAS_WINOTIFY = False

try:
    import winsound
    HAS_WINSOUND = True
except Exception:
    HAS_WINSOUND = False

# Bosta/uzaktayken otomatik duraklama icin son kullanici girdisinden bu yana
# gecen sureyi Windows API'siyle olcuyoruz. Baska platformda / hata halinde
# 0 donup ozellik sessizce devre disi kalir.
try:
    import ctypes

    class _LASTINPUTINFO(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

    def get_idle_seconds():
        if os.name != "nt":
            return 0.0
        try:
            lii = _LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(_LASTINPUTINFO)
            if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
                return 0.0
            millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
            return max(0.0, millis / 1000.0)
        except Exception:
            return 0.0
except Exception:
    def get_idle_seconds():
        return 0.0

APP_NAME = "PixelDrop"
APP_TITLE = "PixelDrop"
# Eski isim (Su Icme Hatirlatici) altinda biriken ayar/gecmis kaybolmasin
# diye config_path() bunu bir kereye mahsus goc icin kullanir; Windows
# baslangic kaydinda da eski isimle kalmis olabilecek girdiyi temizlemek
# icin set_startup() bunu kullanir.
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

# ------------------------------------------------------------------- i18n
# Uygulama arayuzu Turkce ve Ingilizce olarak sunuluyor; ayarlardan
# degistirilebiliyor. Windows toast'un uygulama kimligi (APP_TITLE, bkz.
# asagida) dil degisince kaymasin diye sabit tutuluyor - dil sadece
# gorunen metinleri (widget, tepsi menusu, ayarlar, bildirim icerigi)
# etkiliyor.
STRINGS = {
    "tr": {
        "app_title": "PixelDrop",
        "tray_today": "Bugun icilen: {drank}/{goal} bardak (seri: {streak} gun)",
        "tray_drank": "Su ictim ✓",
        "tray_snooze": "{m} dk ertele",
        "tray_show_widget": "Widget'i goster",
        "tray_hide_widget": "Widget'i gizle",
        "tray_interval": "Aralik",
        "tray_interval_item": "{m} dk",
        "tray_resume": "Devam et",
        "tray_pause": "Duraklat",
        "tray_auto_pause": "Uzaktayken otomatik duraklat",
        "tray_sound": "Bildirim sesi",
        "tray_startup": "Windows baslangicinda calistir",
        "tray_quit": "Cikis",
        "widget_paused": "duraklatildi",
        "widget_away": "uzakta",
        "widget_time_up": "su icme vakti!",
        "goal_text_short": "{drank}/{goal} bardak",
        "notify_time_title": "Su icme vakti!",
        "notify_time_msg": "Bir bardak su icmeyi unutma.",
        "notify_goal_title": "Hedefe ulastin! \U0001F389",
        "notify_goal_msg": "Bugun {goal} bardak su ictin, harika gidiyorsun!",
        "notify_test_title": "Test bildirimi",
        "notify_test_msg": "PixelDrop calisiyor. Bildirimler boyle gorunecek.",
        "settings_title": "Ayarlar",
        "settings_count": "Bugun icilen: {drank} / {goal} bardak   |   Seri: {streak} gun",
        "settings_char_size": "Karakter boyutu:",
        "settings_interval": "Aralik:",
        "settings_min": "dk",
        "settings_daily_goal": "Gunluk hedef:",
        "settings_cups": "bardak",
        "settings_last7": "Son 7 gun:",
        "settings_pause": "Duraklat",
        "settings_auto_pause": "Uzaktayken otomatik duraklat",
        "settings_sound": "Bildirim sesi",
        "settings_startup": "Windows baslangicinda calistir",
        "settings_close": "Kapat",
        "settings_language": "Dil:",
        "lang_tr": "Turkce",
        "lang_en": "English",
        "weekdays": ["Pt", "Sa", "Ca", "Pe", "Cu", "Ct", "Pz"],
    },
    "en": {
        "app_title": "PixelDrop",
        "tray_today": "Today: {drank}/{goal} cups (streak: {streak} days)",
        "tray_drank": "I drank water ✓",
        "tray_snooze": "Snooze {m} min",
        "tray_show_widget": "Show widget",
        "tray_hide_widget": "Hide widget",
        "tray_interval": "Interval",
        "tray_interval_item": "{m} min",
        "tray_resume": "Resume",
        "tray_pause": "Pause",
        "tray_auto_pause": "Auto-pause when away",
        "tray_sound": "Notification sound",
        "tray_startup": "Run at Windows startup",
        "tray_quit": "Quit",
        "widget_paused": "paused",
        "widget_away": "away",
        "widget_time_up": "time to drink!",
        "goal_text_short": "{drank}/{goal} cups",
        "notify_time_title": "Time to drink water!",
        "notify_time_msg": "Don't forget to drink a glass of water.",
        "notify_goal_title": "Goal reached! \U0001F389",
        "notify_goal_msg": "You drank {goal} cups today, great job!",
        "notify_test_title": "Test notification",
        "notify_test_msg": "PixelDrop is running. Notifications will look like this.",
        "settings_title": "Settings",
        "settings_count": "Today: {drank} / {goal} cups   |   Streak: {streak} days",
        "settings_char_size": "Character size:",
        "settings_interval": "Interval:",
        "settings_min": "min",
        "settings_daily_goal": "Daily goal:",
        "settings_cups": "cups",
        "settings_last7": "Last 7 days:",
        "settings_pause": "Pause",
        "settings_auto_pause": "Auto-pause when away",
        "settings_sound": "Notification sound",
        "settings_startup": "Run at Windows startup",
        "settings_close": "Close",
        "settings_language": "Language:",
        "lang_tr": "Turkce",
        "lang_en": "English",
        "weekdays": ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
    },
}


def tr_text(cfg, key, **kwargs):
    lang = cfg.get("language", "tr")
    table = STRINGS.get(lang, STRINGS["tr"])
    s = table.get(key, STRINGS["tr"].get(key, key))
    if kwargs:
        try:
            return s.format(**kwargs)
        except Exception:
            return s
    return s


# ------------------------------------------------------------------ config

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


# ------------------------------------------------------------- pixel maskot

GRID = 16
CELL = 10

PALETTES = {
    "happy":   {"body": (66, 186, 255), "shade": (30, 140, 220), "face": (12, 32, 52)},
    "neutral": {"body": (79, 168, 232), "shade": (45, 120, 180), "face": (18, 38, 58)},
    "thirsty": {"body": (168, 186, 195), "shade": (125, 145, 155), "face": (55, 65, 75)},
    "urgent":  {"body": (255, 120, 100), "shade": (215, 80, 65),  "face": (60, 12, 12)},
    "urgent2": {"body": (255, 150, 90),  "shade": (225, 100, 55), "face": (60, 12, 12)},
    "paused":  {"body": (150, 150, 155), "shade": (110, 110, 115), "face": (60, 60, 65)},
}


def _drop_mask(g=GRID):
    mask = [[False] * g for _ in range(g)]
    cx = g / 2
    cy_circle = g * 0.64
    r = g * 0.34
    for y in range(g):
        for x in range(g):
            dx, dy = (x + 0.5 - cx), (y + 0.5 - cy_circle)
            if (dx * dx) / (r * r) + (dy * dy) / (r * r) <= 1.0:
                mask[y][x] = True
    tip_top = g * 0.08
    tip_bottom = cy_circle - r * 0.15
    for y in range(int(tip_top), int(tip_bottom) + 1):
        t = (y - tip_top) / max(1.0, (tip_bottom - tip_top))
        half_w = (r * 0.95) * t
        for x in range(g):
            if abs(x + 0.5 - cx) <= half_w:
                mask[y][x] = True
    return mask


DROP_MASK = _drop_mask()


def _px(d, x, y, w, h, color):
    d.rectangle([x * CELL, y * CELL, (x + w) * CELL - 1, (y + h) * CELL - 1], fill=color)


def _draw_body_colors(d, body, shade, dryness=0.0):
    for y in range(GRID):
        for x in range(GRID):
            if DROP_MASK[y][x]:
                col = shade if y > GRID * 0.74 else body
                _px(d, x, y, 1, 1, col)
    # susuz kaldikca parlakligi (nem hissi) soluyor. Kismi saydam (alpha<255)
    # bir piksel KULLANMIYORUZ: Windows'un "-transparentcolor" katmanli
    # penceresi tam saydam olmayan pikselleri pencerenin arka plan rengiyle
    # (macenta anahtar renk) karistirip belirgin pembe bir leke birakiyor.
    # Bunun yerine hep tam opak (alpha=255) kalip parlakligi dogrudan RGB
    # renginde (beyazdan govde rengine dogru) soldurarak ayni etkiyi
    # aliyoruz.
    t = max(0.0, min(1.0, 0.65 * dryness))
    sparkle = tuple(int(round(255 * (1 - t) + c * t)) for c in body) + (255,)
    _px(d, GRID * 0.30, GRID * 0.42, 1, 1, sparkle)


PALETTE_STOPS = [(0.0, "happy"), (0.5, "neutral"), (0.8, "thirsty"), (1.0, "urgent")]


def _interp_colors(fraction):
    """Zaman gectikce (susama orani 0..1) govde rengini kademeli olarak
    canliliktan (mutlu-mavi) kurumusluga (kirmizimsi/soluk) gecirir."""
    f = max(0.0, min(1.0, fraction))
    for i in range(len(PALETTE_STOPS) - 1):
        f0, k0 = PALETTE_STOPS[i]
        f1, k1 = PALETTE_STOPS[i + 1]
        if f <= f1 or i == len(PALETTE_STOPS) - 2:
            t = 0.0 if f1 == f0 else (f - f0) / (f1 - f0)
            t = max(0.0, min(1.0, t))
            p0, p1 = PALETTES[k0], PALETTES[k1]
            body = tuple(int(round(a + (b - a) * t)) for a, b in zip(p0["body"], p1["body"]))
            shade = tuple(int(round(a + (b - a) * t)) for a, b in zip(p0["shade"], p1["shade"]))
            face = p1["face"] if t > 0.5 else p0["face"]
            return body, shade, face
    pal = PALETTES["urgent"]
    return pal["body"], pal["shade"], pal["face"]


def _draw_face(d, state, face):
    lx, rx, ey = 5, 9, 8
    if state == "happy":
        _px(d, lx, ey, 1, 1, face); _px(d, rx, ey, 1, 1, face)
        _px(d, lx, ey + 2, 1, 1, face); _px(d, rx, ey + 2, 1, 1, face)
        _px(d, lx + 1, ey + 3, 3, 1, face)
    elif state == "neutral":
        _px(d, lx, ey, 1, 1, face); _px(d, rx, ey, 1, 1, face)
        _px(d, lx, ey + 3, 5, 1, face)
    elif state == "thirsty":
        _px(d, lx - 1, ey + 1, 2, 1, face); _px(d, rx, ey + 1, 2, 1, face)
        _px(d, lx + 1, ey + 4, 1, 1, face); _px(d, lx + 2, ey + 5, 1, 1, face); _px(d, lx + 3, ey + 4, 1, 1, face)
        _px(d, lx, ey + 3, 1, 1, face); _px(d, rx + 1, ey + 3, 1, 1, face)
    elif state in ("urgent", "urgent2"):
        _px(d, lx - 1, ey - 1, 2, 3, face); _px(d, rx, ey - 1, 2, 3, face)
        _px(d, lx + 1, ey + 3, 3, 2, face)
    elif state == "paused":
        _px(d, lx - 1, ey + 1, 2, 1, face); _px(d, rx, ey + 1, 2, 1, face)


_ICON_CACHE = {}


def draw_character(state, size=128, fraction=None):
    """fraction verilirse (0..1+, gecen suredeki susama orani) govde rengi ve
    parlakligi kademeli olarak kurur; None ise state'in sabit paleti kullanilir."""
    if len(_ICON_CACHE) > 400:
        _ICON_CACHE.clear()

    key = state if state in PALETTES else "neutral"
    cache_key = (key, size, round(fraction, 2) if fraction is not None else None)
    if cache_key in _ICON_CACHE:
        return _ICON_CACHE[cache_key]

    dryness = max(0.0, min(1.0, fraction)) if fraction is not None else 0.0
    if fraction is not None and key not in ("paused", "urgent2"):
        body, shade, face = _interp_colors(fraction)
    else:
        pal = PALETTES[key]
        body, shade, face = pal["body"], pal["shade"], pal["face"]

    base = Image.new("RGBA", (GRID * CELL, GRID * CELL), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    _draw_body_colors(d, body, shade, dryness)
    _draw_face(d, key, face)
    img = base.resize((size, size), Image.NEAREST)

    if dryness > 0:
        # hafifce buruserek/kucularak "kurumus" hissi ver
        shrink = 1 - 0.06 * dryness
        new_sz = max(1, int(round(size * shrink)))
        small = img.resize((new_sz, new_sz), Image.NEAREST)
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        off = (size - new_sz) // 2
        canvas.paste(small, (off, off), small)
        img = canvas

    _ICON_CACHE[cache_key] = img
    return img


def rounded_bar_image(width, height, fraction, fg_color, bg_color=(58, 58, 63, 255), radius=None):
    """0..1 dolu bir 'hap' seklinde (kose yuvarlatilmis) ilerleme cubugu."""
    if radius is None:
        radius = height // 2
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, width - 1, height - 1], radius=radius, fill=bg_color)
    bar_w = max(0, min(width, int(round(width * fraction))))
    if bar_w > 0:
        r2 = max(1, min(radius, bar_w // 2, height // 2))
        d.rounded_rectangle([0, 0, bar_w - 1, height - 1], radius=r2, fill=fg_color)
    return _binarize_alpha(img)


def _draw_cup_icon(d, x, y, w, h, filled):
    """Kucuk bir bardak siluetini cizer: bos ise sadece soluk bir cerceve,
    dolu ise mavi 'su' ile dolu gorunur - noktalardan (●/○) daha acik
    anlasilir bir gunluk hedef gostergesi."""
    outline = (150, 150, 158, 255)
    water = (79, 168, 232, 255)
    radius = max(1, w // 4)
    d.rounded_rectangle([x, y, x + w - 1, y + h - 1], radius=radius, outline=outline, width=1)
    if filled:
        pad = 1
        water_top = y + max(1, int(round(h * 0.34)))
        r2 = max(1, radius - 1)
        d.rounded_rectangle([x + pad, water_top, x + w - 1 - pad, y + h - 1 - pad],
                             radius=r2, fill=water)


def _binarize_alpha(img, threshold=90):
    """RGBA goruntudeki kismi saydam (anti-alias) kenar piksellerini tam
    saydam ya da tam opak yapar. Windows'un "-transparentcolor" katmanli
    penceresi kismi saydam pikselleri pencerenin arka plan rengiyle
    (macenta anahtar renk) karistirip belirgin pembe/bulanik lekeler
    biraktigi icin, canvas'a cizilen kucuk gorsellerde (cubuk, bardaklar,
    metin) bunu uyguluyoruz - kenarlar hafif kesikli ama temiz kaliyor."""
    r, g, b, a = img.split()
    a = a.point(lambda v: 255 if v >= threshold else 0)
    return Image.merge("RGBA", (r, g, b, a))


_FONT_CACHE = {}
_FONT_PATHS = (
    r"C:\Windows\Fonts\segoeuib.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\consola.ttf",
)


def _load_font(size):
    if size in _FONT_CACHE:
        return _FONT_CACHE[size]
    font = None
    for path in _FONT_PATHS:
        try:
            font = ImageFont.truetype(path, size)
            break
        except Exception:
            continue
    if font is None:
        try:
            font = ImageFont.load_default(size=size)
        except Exception:
            font = ImageFont.load_default()
    _FONT_CACHE[size] = font
    return font


def render_pixel_text(text, size, color):
    """Geri sayim / hedef metni gibi kucuk yazilari duz canvas create_text
    yerine bir PIL bitmap'i olarak cizer. Neden: sistem fontunun normal
    anti-alias'li kenarlari, -transparentcolor penceresinde macenta ile
    karisip metnin butun bir pembe lekeye donusmesine yol aciyordu
    (ozellikle kucuk punto boyutlarinda okunaksiz/kotu gorunuyordu).
    Alfa kanalini binarize ederek bu sorunu tamamen ortadan kaldiriyoruz."""
    font = _load_font(size)
    tmp = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    bbox = ImageDraw.Draw(tmp).textbbox((0, 0), text, font=font)
    w = max(1, bbox[2] - bbox[0] + 2)
    h = max(1, bbox[3] - bbox[1] + 2)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((-bbox[0] + 1, -bbox[1] + 1), text, font=font, fill=color + (255,))
    return _binarize_alpha(img)


def cups_row_image(drank, goal, cup_w, cup_h, gap):
    """Gunluk hedefi kucuk bardak simgeleri dizisi olarak cizer (dolu =
    icildi, bos = kaldi). Tasan bardaklar (hedefin uzerinde icilenler) icin
    sagina kucuk bir '+N' etiketi eklenir."""
    goal = max(1, goal)
    width = goal * cup_w + max(0, goal - 1) * gap
    extra = max(0, drank - goal)
    extra_w = 22 if extra > 0 else 0
    img = Image.new("RGBA", (max(1, width + extra_w), cup_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i in range(goal):
        x = i * (cup_w + gap)
        _draw_cup_icon(d, x, 0, cup_w, cup_h, i < drank)
    img = _binarize_alpha(img)
    if extra > 0:
        try:
            extra_font_size = max(9, min(13, cup_h))
            extra_img = render_pixel_text(f"+{extra}", extra_font_size, (120, 190, 230))
            img.paste(extra_img, (width + 3, max(0, (cup_h - extra_img.height) // 2)), extra_img)
        except Exception:
            pass
    return img


def _icon_close_image(size, color):
    """Kucuk bir X (kapat) simgesi."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = max(1, round(size * 0.2))
    w = max(1, round(size * 0.16))
    d.line([pad, pad, size - 1 - pad, size - 1 - pad], fill=color, width=w)
    d.line([size - 1 - pad, pad, pad, size - 1 - pad], fill=color, width=w)
    return _binarize_alpha(img)


def _icon_gear_image(size, color):
    """Kucuk bir disli (ayarlar) simgesi."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = size / 2
    outer_r = size * 0.36
    inner_r = size * 0.16
    tooth_r = size * 0.46
    tooth_d = max(2, round(size * 0.20))
    n_teeth = 6
    for i in range(n_teeth):
        ang = 2 * math.pi * i / n_teeth
        tx = cx + tooth_r * math.cos(ang)
        ty = cy + tooth_r * math.sin(ang)
        d.ellipse([tx - tooth_d / 2, ty - tooth_d / 2, tx + tooth_d / 2, ty + tooth_d / 2], fill=color)
    ring_w = max(1, round(size * 0.14))
    d.ellipse([cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r], outline=color, width=ring_w)
    d.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r], fill=color)
    return _binarize_alpha(img)


def _icon_snooze_image(size, color):
    """Kucuk bir 'Z' (ertele) simgesi - eskiden kullanilan 💤 renkli emoji,
    Windows'un -transparentcolor penceresinde belirgin bir pembe/mor lekeye
    donusuyordu (renkli emoji glifleri kismi saydam kenarlarla dolu).
    Duz cizilmis bu simge tamamen opak, o yuzden asla lekelenmiyor."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pad = max(1, round(size * 0.2))
    w = max(1, round(size * 0.15))
    top_y = pad
    bot_y = size - 1 - pad
    left_x = pad
    right_x = size - 1 - pad
    d.line([left_x, top_y, right_x, top_y], fill=color, width=w)
    d.line([right_x, top_y, left_x, bot_y], fill=color, width=w)
    d.line([left_x, bot_y, right_x, bot_y], fill=color, width=w)
    return _binarize_alpha(img)


def state_for_fraction(fraction, paused):
    if paused:
        return "paused"
    if fraction < 0.5:
        return "happy"
    if fraction < 0.8:
        return "neutral"
    if fraction < 1.0:
        return "thirsty"
    return "urgent"


# --------------------------------------------------------------- bildirim

def notify(title, msg, cfg):
    shown = False
    if HAS_WINOTIFY:
        try:
            toast = Notification(app_id=APP_TITLE, title=title, msg=msg, duration="short")
            if cfg.get("sound", True):
                toast.set_audio(audio.Default, loop=False)
            toast.show()
            shown = True
        except Exception:
            pass
    if not shown:
        print(f"[BILDIRIM] {title}: {msg}")

    # Toast'un kendi sesi; sistem bildirim ayarlari (kayitli olmayan app_id,
    # Odaklanma Yardimcisi/oyun modu, PowerShell icin ses kapali vb.) yuzunden
    # sessiz kalabiliyor. winsound dogrudan sistem sesi caldigi icin bu
    # ayarlardan bagimsiz calisir - "hala ses gelmiyor" sorununun asil cozumu.
    if cfg.get("sound", True) and HAS_WINSOUND:
        try:
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass


def set_startup(enable):
    if os.name != "nt":
        return
    import winreg

    key = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0,
        winreg.KEY_SET_VALUE,
    )
    try:
        # Eski isimle (Su Icme Hatirlatici) kalmis olabilecek baslangic
        # kaydini her durumda temizle - yoksa iki ayri girdi (biri eski,
        # gecersiz yolu gosteren) birikebilir.
        try:
            winreg.DeleteValue(key, OLD_APP_NAME)
        except FileNotFoundError:
            pass

        if enable:
            if getattr(sys, "frozen", False):
                cmd = f'"{sys.executable}"'
            else:
                pythonw = sys.executable.replace("python.exe", "pythonw.exe")
                script = os.path.abspath(__file__)
                cmd = f'"{pythonw}" "{script}"'
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
    finally:
        winreg.CloseKey(key)


# ------------------------------------------------------------------- app

WIDGET_SIZE_DEFAULT = 140    # karakter boyutunun varsayilani (ayarlardan degistirilebilir)
WIDGET_MIN = 90
WIDGET_MAX = 220
WIDGET_PADDING_TOP_DEFAULT = 14   # bob animasyonu icin ust bosluk
FOOTER_DEFAULT = 52               # ilerleme cubugu + hedef bardaklari + etiket alani
BAR_MARGIN_DEFAULT = 10
BAR_H_DEFAULT = 7
TRANSPARENT_KEY = "#ff00fe"
LABEL_TEXT_COLOR = (150, 150, 158)   # geri sayim yazisi - soluk ama artik net (pembe leke yok)
GOAL_TEXT_COLOR = (122, 172, 202)    # buyuk hedeflerde ("N/M bardak") kullanilan metin yedegi
HOVER_ICON_COLOR = (172, 172, 178)   # 💤/⚙/✕ ucu - uc simge de artik ayni renk, elle cizilmis
CLOSE_BTN_R = 6
SNOOZE_MINUTES = 5
AUTO_PAUSE_IDLE_MINUTES = 10
HISTORY_DAYS_KEPT = 14

# Ayarlar penceresi - koyu tema
SETTINGS_BG = "#1e1e22"
SETTINGS_FG = "#e6e6e6"
SETTINGS_MUTED = "#9a9a9a"
SETTINGS_FIELD_BG = "#2a2a30"
SETTINGS_BTN_BG = "#33333a"
SETTINGS_BTN_ACTIVE = "#3d3d46"
SETTINGS_ACCENT = "#4fa8e8"


class WaterReminderApp:
    def __init__(self):
        self.cfg = load_config()
        self._roll_day_if_needed()

        self.next_at = time.time() + self.cfg["interval_minutes"] * 60
        self.notified = False
        self.celebrate_until = 0.0
        self.blink_on = False
        self._hovering = False
        self._auto_paused = False
        self._drag = {"active": False, "moved": False, "start_x": 0, "start_y": 0,
                       "win_x": 0, "win_y": 0, "on_close": False, "on_gear": False,
                       "on_snooze": False}
        self._settings_win = None

        self.widget_size = self.cfg.get("widget_size", WIDGET_SIZE_DEFAULT)
        self._recompute_dims()

        self.root = tk.Tk()
        self.root.withdraw()  # ana pencereyi gizle, sadece overlay kullanacagiz
        self.root.title(APP_TITLE)

        self._build_widget()
        self._build_tray()

        if not self.cfg.get("widget_visible", True):
            self.overlay.withdraw()

        self.root.after(60, self._animate)
        self.root.after(1000, self._tick)

    # ---------------- gun donusu / hedef / seri ----------------
    def _roll_day_if_needed(self):
        """Gece yarisini gecince (uygulama acik kalsa bile) gunluk sayaci
        sifirlar, onceki gunu gecmise kaydeder ve seriyi gunceller. Her
        _tick'te cagirildigi icin gece boyunca acik kalan uygulamada da
        dogru calisir (onceden sadece baslangicta calisiyordu)."""
        today_dt = date.today()
        today_str = str(today_dt)
        last_str = self.cfg.get("last_reset_date") or today_str
        if last_str == today_str:
            return

        try:
            last_dt = date.fromisoformat(last_str)
            gap_days = (today_dt - last_dt).days
        except Exception:
            gap_days = 1

        prev_count = self.cfg.get("drank_today", 0)
        goal = self.cfg.get("daily_goal", 8)

        history = dict(self.cfg.get("history", {}))
        history[last_str] = prev_count
        if len(history) > HISTORY_DAYS_KEPT:
            for k in sorted(history.keys())[:-HISTORY_DAYS_KEPT]:
                del history[k]
        self.cfg["history"] = history

        if gap_days == 1 and prev_count >= goal:
            self.cfg["streak"] = self.cfg.get("streak", 0) + 1
        else:
            # bir gun atlandi (uygulama kapaliyken) ya da hedefe ulasilamadi
            self.cfg["streak"] = 0

        self.cfg["drank_today"] = 0
        self.cfg["last_reset_date"] = today_str
        save_config(self.cfg)
        self._refresh_tray_menu()

    def t(self, key, **kwargs):
        return tr_text(self.cfg, key, **kwargs)

    def _goal_progress_text(self):
        # Bardak simgeleri cok genis olacagi (10'dan fazla bardak) durumlar
        # icin kisa metin yedegi.
        drank = self.cfg.get("drank_today", 0)
        goal = max(1, self.cfg.get("daily_goal", 8))
        return self.t("goal_text_short", drank=drank, goal=goal)

    # ---------------- boyuta gore olculer ----------------
    def _recompute_dims(self):
        ratio = self.widget_size / WIDGET_SIZE_DEFAULT
        self.padding_top = max(8, round(WIDGET_PADDING_TOP_DEFAULT * ratio))
        self.window_w = self.widget_size
        self.bar_margin = max(6, round(BAR_MARGIN_DEFAULT * ratio))
        self.bar_h = max(5, round(BAR_H_DEFAULT * ratio))
        self.bar_w = self.window_w - 2 * self.bar_margin
        self.cup_w = max(6, round(9 * ratio))
        self.cup_h = max(7, round(11 * ratio))
        self.cup_gap = max(1, round(2 * ratio))

        # Alt bolgeyi asagidan yukariya dogru hesapliyoruz (etiket -> bardak
        # sirasi -> ilerleme cubugu) ki widget boyutu ne olursa olsun ogeler
        # asla ust uste binmesin: footer, bu sıraların gerektirdigi asgari
        # yukseklikten kucuk olamaz (sadece FOOTER_DEFAULT'a degil, gercek
        # icerige gore hesaplanir).
        top_gap = max(2, round(4 * ratio))
        row_gap = max(3, round(4 * ratio))
        bottom_pad = max(4, round(6 * ratio))
        # Geri sayim yazisi eskiden sabit 8pt'ti (karaktere gore cok kucuk
        # kaliyordu); artik widget boyutuyla birlikte buyuyor. Yuksekligi
        # tahmin etmek yerine gercekten olceriz ki dizilim asla yanlis
        # olmasin.
        self.label_font_size = max(11, round(15 * ratio))
        label_h = render_pixel_text("00:00", self.label_font_size, (0, 0, 0)).height

        footer_needed = top_gap + self.bar_h + row_gap + self.cup_h + row_gap + label_h + bottom_pad
        footer = max(footer_needed, round(FOOTER_DEFAULT * ratio))
        self.window_h = self.widget_size + self.padding_top + footer

        self.label_y = self.window_h - bottom_pad - label_h
        self.goal_y = self.label_y - row_gap - self.cup_h
        self.bar_top = self.goal_y - row_gap - self.bar_h

        self.icon_y = max(8, round(10 * ratio))
        self.hover_icon_size = max(11, round(15 * ratio))
        self.gear_offset_x = max(32, round(44 * ratio))
        self.close_offset_x = max(12, round(12 * ratio))
        self.snooze_offset_x = max(64, round(78 * ratio))

    def _apply_size(self, new_size):
        new_size = max(WIDGET_MIN, min(WIDGET_MAX, int(float(new_size))))
        if new_size == self.widget_size:
            return
        self.widget_size = new_size
        self.cfg["widget_size"] = new_size
        save_config(self.cfg)

        x, y = self.overlay.winfo_x(), self.overlay.winfo_y()
        self._recompute_dims()
        self.overlay.geometry(f"{self.window_w}x{self.window_h}+{x}+{y}")
        self.canvas.config(width=self.window_w, height=self.window_h)
        self._snooze_tk = ImageTk.PhotoImage(_icon_snooze_image(self.hover_icon_size, HOVER_ICON_COLOR))
        self.canvas.itemconfig(self._snooze_item, image=self._snooze_tk)
        self.canvas.coords(self._snooze_item, self.window_w - self.snooze_offset_x, self.icon_y)
        self._gear_tk = ImageTk.PhotoImage(_icon_gear_image(self.hover_icon_size, HOVER_ICON_COLOR))
        self.canvas.itemconfig(self._gear_item, image=self._gear_tk)
        self.canvas.coords(self._gear_item, self.window_w - self.gear_offset_x, self.icon_y)
        self._close_tk = ImageTk.PhotoImage(_icon_close_image(self.hover_icon_size, HOVER_ICON_COLOR))
        self.canvas.itemconfig(self._close_item, image=self._close_tk)
        self.canvas.coords(self._close_item, self.window_w - self.close_offset_x, self.icon_y)
        self.canvas.coords(self._goal_cups_item, self.window_w // 2, self.goal_y)
        self.canvas.coords(self._goal_item, self.window_w // 2, self.goal_y)
        self.canvas.coords(self._label, self.window_w // 2, self.label_y)
        self.canvas.coords(self._bar_item, self.bar_margin, self.bar_top)
        # karakter ve cubuk gorseli bir sonraki _animate/_tick kareside kendiliginden yeniden cizilir

    # ---------------- widget (overlay) ----------------
    def _build_widget(self):
        ov = tk.Toplevel(self.root)
        self.overlay = ov
        ov.overrideredirect(True)
        ov.wm_attributes("-topmost", True)
        try:
            ov.wm_attributes("-transparentcolor", TRANSPARENT_KEY)
        except tk.TclError:
            pass
        ov.configure(bg=TRANSPARENT_KEY)

        x = self.cfg.get("widget_x")
        y = self.cfg.get("widget_y")
        if x is None or y is None:
            sw = ov.winfo_screenwidth()
            sh = ov.winfo_screenheight()
            x = sw - self.window_w - 40
            y = sh - self.window_h - 90
        ov.geometry(f"{self.window_w}x{self.window_h}+{int(x)}+{int(y)}")

        self.canvas = tk.Canvas(ov, width=self.window_w, height=self.window_h,
                                 bg=TRANSPARENT_KEY, highlightthickness=0)
        self.canvas.pack()

        self._char_img_tk = None
        self._char_item = self.canvas.create_image(self.window_w // 2, self.padding_top, anchor="n")
        self._bar_img_tk = None
        self._bar_item = self.canvas.create_image(self.bar_margin, self.bar_top, anchor="nw")
        self._goal_cups_tk = None
        self._goal_cups_item = self.canvas.create_image(self.window_w // 2, self.goal_y, anchor="n")
        # Geri sayim ve hedef-metni ogeleri PIL bitmap olarak ciziliyor
        # (bkz. render_pixel_text): duz canvas create_text kullaninca
        # sistem fontunun anti-alias kenarlari -transparentcolor
        # penceresinde macenta ile karisip metnin pembe/bulanik
        # gorunmesine yol aciyordu.
        self._goal_img_tk = None
        self._goal_item = self.canvas.create_image(self.window_w // 2, self.goal_y, anchor="n")
        self.canvas.itemconfigure(self._goal_item, state="hidden")
        self._label_img_tk = None
        self._label = self.canvas.create_image(self.window_w // 2, self.label_y, anchor="n")
        # Ucu de kendi cizdigimiz duz simgeler (bkz. _icon_*_image): eskiden
        # 💤/⚙ Unicode/emoji glifleriydi ve Windows'un -transparentcolor
        # penceresinde belirgin bir pembe/mor lekeye donusuyordu (renkli
        # emoji ve bazi sembol glifleri kismi saydam kenarlarla dolu).
        # Tamamen opak, elle cizilmis bu simgeler asla lekelenmiyor ve
        # ucu de garanti ayni renkte cikiyor.
        self._snooze_tk = ImageTk.PhotoImage(_icon_snooze_image(self.hover_icon_size, HOVER_ICON_COLOR))
        self._snooze_item = self.canvas.create_image(self.window_w - self.snooze_offset_x, self.icon_y,
                                                       image=self._snooze_tk)
        self._gear_tk = ImageTk.PhotoImage(_icon_gear_image(self.hover_icon_size, HOVER_ICON_COLOR))
        self._gear_item = self.canvas.create_image(self.window_w - self.gear_offset_x, self.icon_y,
                                                     image=self._gear_tk)
        self._close_tk = ImageTk.PhotoImage(_icon_close_image(self.hover_icon_size, HOVER_ICON_COLOR))
        self._close_item = self.canvas.create_image(self.window_w - self.close_offset_x, self.icon_y,
                                                      image=self._close_tk)
        for _hover_item in (self._gear_item, self._close_item, self._snooze_item):
            self.canvas.itemconfigure(_hover_item, state="hidden")

        self.canvas.tag_bind("all", "<ButtonPress-1>", self._on_press)
        self.canvas.tag_bind("all", "<B1-Motion>", self._on_motion)
        self.canvas.tag_bind("all", "<ButtonRelease-1>", self._on_release)
        ov.protocol("WM_DELETE_WINDOW", self._hide_widget)

    def _check_hover(self):
        # Pencere -transparentcolor ile "tiklama gecirgen" oldugu icin
        # canvas'in kendi <Enter>/<Leave> olaylari saydam bosluklarda
        # guvenilir degil (karakterle butonlar arasinda erken kapaniyordu).
        # Bunun yerine fare imlecinin ekran konumunu dogrudan pencere
        # dikdortgeniyle karsilastiriyoruz - tum widget alani tek hitbox olur.
        try:
            px = self.root.winfo_pointerx()
            py = self.root.winfo_pointery()
        except tk.TclError:
            return
        wx, wy = self.overlay.winfo_x(), self.overlay.winfo_y()
        hovering = (px >= 0 and py >= 0 and wx <= px <= wx + self.window_w
                    and wy <= py <= wy + self.window_h)
        if hovering != self._hovering:
            self._hovering = hovering
            state = "normal" if hovering else "hidden"
            self.canvas.itemconfigure(self._close_item, state=state)
            self.canvas.itemconfigure(self._gear_item, state=state)
            self.canvas.itemconfigure(self._snooze_item, state=state)

    def _hit(self, item, event, pad=CLOSE_BTN_R):
        bbox = self.canvas.bbox(item)
        return bool(bbox and bbox[0] - pad <= event.x <= bbox[2] + pad
                    and bbox[1] - pad <= event.y <= bbox[3] + pad)

    def _on_press(self, event):
        d = self._drag
        d["active"] = True
        d["moved"] = False
        d["start_x"] = event.x_root
        d["start_y"] = event.y_root
        d["win_x"] = self.overlay.winfo_x()
        d["win_y"] = self.overlay.winfo_y()

        # Uc kucuk simge (💤/⚙/✕) yan yana oldugu icin tiklama alanlari
        # ust uste binebiliyor; en yakin merkeze sahip olani seciyoruz ki
        # ikisi de "hit" oldugunda yanlis butona basilmasin.
        candidates = []
        for key, item in (("close", self._close_item), ("gear", self._gear_item),
                           ("snooze", self._snooze_item)):
            if self._hit(item, event):
                bbox = self.canvas.bbox(item)
                cx = (bbox[0] + bbox[2]) / 2
                candidates.append((key, abs(event.x - cx)))
        chosen = min(candidates, key=lambda c: c[1])[0] if candidates else None
        d["on_close"] = chosen == "close"
        d["on_gear"] = chosen == "gear"
        d["on_snooze"] = chosen == "snooze"

    def _on_motion(self, event):
        d = self._drag
        if not d["active"] or d["on_close"] or d["on_gear"] or d["on_snooze"]:
            return
        dx = event.x_root - d["start_x"]
        dy = event.y_root - d["start_y"]
        if abs(dx) > 3 or abs(dy) > 3:
            d["moved"] = True
        self.overlay.geometry(f"+{d['win_x'] + dx}+{d['win_y'] + dy}")

    def _on_release(self, event):
        d = self._drag
        if d["on_close"]:
            self._hide_widget()
        elif d["on_gear"]:
            self._open_settings()
        elif d["on_snooze"]:
            self.snooze()
        elif not d["moved"]:
            self.mark_drank()
        else:
            self.cfg["widget_x"] = self.overlay.winfo_x()
            self.cfg["widget_y"] = self.overlay.winfo_y()
            save_config(self.cfg)
        d["active"] = False

    def _hide_widget(self):
        self.cfg["widget_visible"] = False
        save_config(self.cfg)
        self.overlay.withdraw()
        self._refresh_tray_menu()

    def show_widget(self):
        self.cfg["widget_visible"] = True
        save_config(self.cfg)
        self.overlay.deiconify()
        self._refresh_tray_menu()

    def _open_settings(self):
        win = self._settings_win
        if win is not None:
            try:
                win.deiconify()
                win.lift()
                win.focus_force()
                return
            except tk.TclError:
                self._settings_win = None

        win = tk.Toplevel(self.root)
        self._settings_win = win
        win.title(self.t("settings_title"))
        win.resizable(False, False)
        win.attributes("-topmost", True)
        win.configure(bg=SETTINGS_BG)

        ox, oy = self.overlay.winfo_x(), self.overlay.winfo_y()
        win.geometry(f"+{max(0, ox - 220)}+{max(0, oy)}")

        pad = {"padx": 12, "pady": 5}

        def label(master, **kw):
            kw.setdefault("bg", SETTINGS_BG)
            kw.setdefault("fg", SETTINGS_FG)
            return tk.Label(master, **kw)

        def checkbutton(master, **kw):
            return tk.Checkbutton(
                master, bg=SETTINGS_BG, fg=SETTINGS_FG,
                activebackground=SETTINGS_BG, activeforeground=SETTINGS_FG,
                selectcolor=SETTINGS_FIELD_BG, highlightthickness=0,
                bd=0, **kw,
            )

        def option_menu(master, var, choices, command):
            menu = tk.OptionMenu(master, var, *choices, command=command)
            menu.configure(bg=SETTINGS_FIELD_BG, fg=SETTINGS_FG,
                            activebackground=SETTINGS_BTN_ACTIVE, activeforeground=SETTINGS_FG,
                            highlightthickness=0, bd=0)
            menu["menu"].configure(bg=SETTINGS_FIELD_BG, fg=SETTINGS_FG,
                                    activebackground=SETTINGS_ACCENT, activeforeground="#111111")
            return menu

        count_label = label(win, font=("Segoe UI", 9))
        count_label.pack(anchor="w", **pad)

        char_size_label = label(win, text=self.t("settings_char_size"))
        char_size_label.pack(anchor="w", padx=12, pady=(4, 0))
        size_var = tk.IntVar(value=self.widget_size)
        tk.Scale(win, from_=WIDGET_MIN, to=WIDGET_MAX, orient="horizontal", length=200,
                 resolution=10, variable=size_var, showvalue=True,
                 command=lambda v: self._apply_size(v),
                 bg=SETTINGS_BG, fg=SETTINGS_FG, troughcolor=SETTINGS_FIELD_BG,
                 activebackground=SETTINGS_ACCENT, highlightthickness=0,
                 bd=0).pack(anchor="w", padx=6, pady=(0, 5))

        row = tk.Frame(win, bg=SETTINGS_BG)
        row.pack(anchor="w", **pad)
        interval_label = label(row, text=self.t("settings_interval"))
        interval_label.pack(side="left")
        interval_var = tk.IntVar(value=self.cfg["interval_minutes"])
        option_menu(row, interval_var, INTERVAL_CHOICES,
                    lambda v: self.set_interval(int(v))).pack(side="left", padx=6)
        interval_unit_label = label(row, text=self.t("settings_min"))
        interval_unit_label.pack(side="left")

        row2 = tk.Frame(win, bg=SETTINGS_BG)
        row2.pack(anchor="w", **pad)
        goal_label = label(row2, text=self.t("settings_daily_goal"))
        goal_label.pack(side="left")
        goal_var = tk.IntVar(value=self.cfg.get("daily_goal", 8))
        option_menu(row2, goal_var, GOAL_CHOICES,
                    lambda v: self.set_daily_goal(int(v))).pack(side="left", padx=6)
        goal_unit_label = label(row2, text=self.t("settings_cups"))
        goal_unit_label.pack(side="left")

        row3 = tk.Frame(win, bg=SETTINGS_BG)
        row3.pack(anchor="w", **pad)
        lang_label = label(row3, text=self.t("settings_language"))
        lang_label.pack(side="left")
        lang_display = [self.t("lang_tr"), self.t("lang_en")]
        lang_var = tk.StringVar(value=self.t("lang_tr") if self.cfg.get("language", "tr") == "tr"
                                 else self.t("lang_en"))
        option_menu(row3, lang_var, lang_display,
                    lambda v: self.set_language("tr" if v == self.t("lang_tr") else "en")).pack(side="left", padx=6)

        last7_label = label(win, text=self.t("settings_last7"))
        last7_label.pack(anchor="w", padx=12, pady=(6, 0))
        hist_canvas = tk.Canvas(win, width=204, height=68, bg=SETTINGS_BG, highlightthickness=0)
        hist_canvas.pack(anchor="w", padx=10, pady=(2, 4))

        def draw_history():
            hist_canvas.delete("all")
            goal = max(1, self.cfg.get("daily_goal", 8))
            history = self.cfg.get("history", {})
            today = date.today()
            days = []
            for i in range(6, -1, -1):
                d_ = today - timedelta(days=i)
                count = self.cfg.get("drank_today", 0) if d_ == today else history.get(str(d_), 0)
                days.append((d_, count))
            max_val = max(goal, max((c for _, c in days), default=0), 1)
            weekday_names = self.t("weekdays")
            bar_w, gap, base_y, top_h = 22, 6, 48, 40
            x = 4
            for d_, count in days:
                h = int(round((count / max_val) * top_h)) if count > 0 else 0
                h = max(2, h) if count > 0 else 0
                color = SETTINGS_ACCENT if count >= goal else SETTINGS_FIELD_BG
                hist_canvas.create_rectangle(x, base_y - h, x + bar_w, base_y, fill=color, outline="")
                hist_canvas.create_text(x + bar_w / 2, base_y + 9, text=weekday_names[d_.weekday()],
                                         fill=SETTINGS_MUTED, font=("Segoe UI", 7))
                x += bar_w + gap

        draw_history()

        paused_var = tk.BooleanVar(value=self.cfg["paused"])
        pause_cb = checkbutton(win, text=self.t("settings_pause"), variable=paused_var,
                                command=lambda: self.toggle_pause())
        pause_cb.pack(anchor="w", **pad)

        autopause_var = tk.BooleanVar(value=self.cfg.get("auto_pause_enabled", True))
        autopause_cb = checkbutton(win, text=self.t("settings_auto_pause"), variable=autopause_var,
                                    command=lambda: self.toggle_auto_pause())
        autopause_cb.pack(anchor="w", **pad)

        sound_var = tk.BooleanVar(value=self.cfg["sound"])
        sound_cb = checkbutton(win, text=self.t("settings_sound"), variable=sound_var,
                                command=lambda: self.toggle_sound())
        sound_cb.pack(anchor="w", **pad)

        startup_var = tk.BooleanVar(value=self.cfg["run_at_startup"])
        startup_cb = checkbutton(win, text=self.t("settings_startup"), variable=startup_var,
                                  command=lambda: self.toggle_startup())
        startup_cb.pack(anchor="w", **pad)

        close_btn = tk.Button(win, text=self.t("settings_close"), command=win.destroy,
                               bg=SETTINGS_BTN_BG, fg=SETTINGS_FG,
                               activebackground=SETTINGS_BTN_ACTIVE, activeforeground=SETTINGS_FG,
                               highlightthickness=0, bd=0, padx=10, pady=3)
        close_btn.pack(anchor="e", padx=12, pady=(4, 10))

        def refresh_vars(event=None):
            goal = self.cfg.get("daily_goal", 8)
            streak = self.cfg.get("streak", 0)
            count_label.config(
                text=self.t("settings_count", drank=self.cfg['drank_today'], goal=goal, streak=streak)
            )
            size_var.set(self.widget_size)
            interval_var.set(self.cfg["interval_minutes"])
            goal_var.set(goal)
            lang_var.set(self.t("lang_tr") if self.cfg.get("language", "tr") == "tr" else self.t("lang_en"))
            paused_var.set(self.cfg["paused"])
            autopause_var.set(self.cfg.get("auto_pause_enabled", True))
            sound_var.set(self.cfg["sound"])
            startup_var.set(self.cfg["run_at_startup"])
            draw_history()

        refresh_vars()
        win.bind("<FocusIn>", refresh_vars)

        def on_destroy(event):
            if event.widget is win:
                self._settings_win = None
        win.bind("<Destroy>", on_destroy)

    # ---------------- tray ----------------
    def _build_tray(self):
        self.icon = pystray.Icon(APP_NAME, draw_character("happy", 64), self.t("app_title"),
                                  menu=self._build_menu())
        try:
            self.icon.run_detached()
        except AttributeError:
            import threading
            threading.Thread(target=self.icon.run, daemon=True).start()

    def _build_menu(self):
        def interval_item(minutes):
            return pystray.MenuItem(
                lambda item, m=minutes: self.t("tray_interval_item", m=m),
                lambda icon, item: self.set_interval(minutes),
                checked=lambda item, m=minutes: self.cfg["interval_minutes"] == m,
                radio=True,
            )

        return pystray.Menu(
            pystray.MenuItem(
                lambda item: self.t(
                    "tray_today",
                    drank=self.cfg['drank_today'],
                    goal=self.cfg.get('daily_goal', 8),
                    streak=self.cfg.get('streak', 0),
                ),
                None, enabled=False,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lambda item: self.t("tray_drank"), lambda icon, item: self.mark_drank()),
            pystray.MenuItem(lambda item: self.t("tray_snooze", m=SNOOZE_MINUTES),
                              lambda icon, item: self.snooze()),
            pystray.MenuItem(
                lambda item: self.t("tray_show_widget") if not self.cfg["widget_visible"]
                else self.t("tray_hide_widget"),
                self._toggle_widget,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lambda item: self.t("tray_interval"),
                              pystray.Menu(*[interval_item(m) for m in INTERVAL_CHOICES])),
            pystray.MenuItem(
                lambda item: self.t("tray_resume") if self.cfg["paused"] else self.t("tray_pause"),
                self.toggle_pause,
            ),
            pystray.MenuItem(
                lambda item: self.t("tray_auto_pause"), self.toggle_auto_pause,
                checked=lambda item: self.cfg.get("auto_pause_enabled", True),
            ),
            pystray.MenuItem(lambda item: self.t("tray_sound"), self.toggle_sound,
                              checked=lambda item: self.cfg["sound"]),
            pystray.MenuItem(
                lambda item: self.t("tray_startup"), self.toggle_startup,
                checked=lambda item: self.cfg["run_at_startup"],
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lambda item: self.t("tray_quit"), self.quit_app),
        )

    def _refresh_tray_menu(self):
        try:
            self.icon.menu = self._build_menu()
        except Exception:
            pass

    def _toggle_widget(self, icon=None, item=None):
        if self.cfg["widget_visible"]:
            self.root.after(0, self._hide_widget)
        else:
            self.root.after(0, self.show_widget)

    # ---------------- actions ----------------
    def mark_drank(self):
        goal = self.cfg.get("daily_goal", 8)
        was_below_goal = self.cfg.get("drank_today", 0) < goal
        self.cfg["drank_today"] += 1
        now_at_goal = self.cfg["drank_today"] >= goal
        self.next_at = time.time() + self.cfg["interval_minutes"] * 60
        self.notified = False
        if was_below_goal and now_at_goal:
            self.celebrate_until = time.time() + 3.0
            notify(self.t("notify_goal_title"), self.t("notify_goal_msg", goal=goal), self.cfg)
        else:
            self.celebrate_until = time.time() + 1.2
        save_config(self.cfg)
        self._refresh_tray_menu()

    def set_interval(self, minutes):
        self.cfg["interval_minutes"] = minutes
        self.next_at = time.time() + minutes * 60
        self.notified = False
        save_config(self.cfg)
        self._refresh_tray_menu()

    def set_daily_goal(self, goal):
        self.cfg["daily_goal"] = goal
        save_config(self.cfg)
        self._refresh_tray_menu()

    def set_language(self, lang):
        if lang not in ("tr", "en") or self.cfg.get("language", "tr") == lang:
            return
        self.cfg["language"] = lang
        save_config(self.cfg)
        self._refresh_tray_menu()
        try:
            self.icon.title = self.t("app_title")
        except Exception:
            pass
        # Ayarlar penceresindeki sabit etiketler (checkbox/label metinleri)
        # canli guncellenmiyor - en basit ve guvenilir yol pencereyi yeni
        # dille yeniden acmak.
        win = self._settings_win
        if win is not None:
            try:
                win.destroy()
            except Exception:
                pass
            self._settings_win = None
            self._open_settings()

    def snooze(self, icon=None, item=None):
        self.next_at = time.time() + SNOOZE_MINUTES * 60
        self.notified = False
        save_config(self.cfg)
        self._refresh_tray_menu()

    def toggle_pause(self, icon=None, item=None):
        self.cfg["paused"] = not self.cfg["paused"]
        if not self.cfg["paused"]:
            self.next_at = time.time() + self.cfg["interval_minutes"] * 60
            self.notified = False
        save_config(self.cfg)
        self._refresh_tray_menu()

    def toggle_auto_pause(self, icon=None, item=None):
        self.cfg["auto_pause_enabled"] = not self.cfg.get("auto_pause_enabled", True)
        if not self.cfg["auto_pause_enabled"]:
            self._auto_paused = False
        save_config(self.cfg)
        self._refresh_tray_menu()

    def toggle_sound(self, icon=None, item=None):
        self.cfg["sound"] = not self.cfg["sound"]
        save_config(self.cfg)
        self._refresh_tray_menu()

    def toggle_startup(self, icon=None, item=None):
        self.cfg["run_at_startup"] = not self.cfg["run_at_startup"]
        try:
            set_startup(self.cfg["run_at_startup"])
        except Exception as e:
            print(f"[UYARI] baslangic ayari degistirilemedi: {e}")
        save_config(self.cfg)
        self._refresh_tray_menu()

    def quit_app(self, icon=None, item=None):
        save_config(self.cfg)
        try:
            self.icon.stop()
        except Exception:
            pass
        self.root.after(0, self.root.destroy)

    # ---------------- loops ----------------
    def _current_fraction(self):
        total = max(1, self.cfg["interval_minutes"] * 60)
        remaining = self.next_at - time.time()
        elapsed = total - remaining
        return max(0.0, elapsed / total)

    def _tick(self):
        self._roll_day_if_needed()

        # Bosta/uzaktayken otomatik duraklama: kullanici bir sureden beri
        # klavye/fare kullanmadiysa hatirlaticiyi gecici olarak durdurur,
        # geri donunce sayaci sifirlayip aninda bildirim gelmesini onler.
        idle_pause = False
        if self.cfg.get("auto_pause_enabled", True):
            idle_pause = get_idle_seconds() >= AUTO_PAUSE_IDLE_MINUTES * 60
        if idle_pause and not self._auto_paused:
            self._auto_paused = True
        elif not idle_pause and self._auto_paused:
            self._auto_paused = False
            self.next_at = time.time() + self.cfg["interval_minutes"] * 60
            self.notified = False

        fraction = self._current_fraction()
        effective_paused = self.cfg["paused"] or self._auto_paused
        state = state_for_fraction(fraction, effective_paused)

        if not effective_paused and fraction >= 1.0 and not self.notified:
            notify(self.t("notify_time_title"), self.t("notify_time_msg"), self.cfg)
            self.notified = True

        if state == "urgent":
            self.blink_on = not self.blink_on
            icon_state = "urgent2" if self.blink_on else "urgent"
        else:
            icon_state = state

        try:
            self.icon.icon = draw_character(icon_state, 64, fraction=fraction)
        except Exception:
            pass

        remaining = max(0, int(self.next_at - time.time()))
        mm, ss = divmod(remaining, 60)
        if self.cfg["paused"]:
            label = self.t("widget_paused")
        elif self._auto_paused:
            label = self.t("widget_away")
        elif remaining <= 0:
            label = self.t("widget_time_up")
        else:
            label = f"{mm:02d}:{ss:02d}"
        try:
            label_img = render_pixel_text(label, self.label_font_size, LABEL_TEXT_COLOR)
            self._label_img_tk = ImageTk.PhotoImage(label_img)
            self.canvas.itemconfig(self._label, image=self._label_img_tk)

            goal = self.cfg.get("daily_goal", 8)
            drank = self.cfg.get("drank_today", 0)
            if goal <= 8:
                cup_img = cups_row_image(drank, goal, self.cup_w, self.cup_h, self.cup_gap)
                self._goal_cups_tk = ImageTk.PhotoImage(cup_img)
                self.canvas.itemconfig(self._goal_cups_item, image=self._goal_cups_tk)
                self.canvas.itemconfigure(self._goal_cups_item, state="normal")
                self.canvas.itemconfigure(self._goal_item, state="hidden")
            else:
                goal_img = render_pixel_text(self._goal_progress_text(), self.label_font_size, GOAL_TEXT_COLOR)
                self._goal_img_tk = ImageTk.PhotoImage(goal_img)
                self.canvas.itemconfig(self._goal_item, image=self._goal_img_tk)
                self.canvas.itemconfigure(self._goal_item, state="normal")
                self.canvas.itemconfigure(self._goal_cups_item, state="hidden")

            frac_bar = min(1.0, fraction)
            remaining_frac = max(0.0, 1 - frac_bar)
            bar_color = "#4fa8e8" if state in ("happy", "neutral") else (
                "#c9c9cc" if state == "paused" else ("#e8a24f" if state == "thirsty" else "#e8544f"))
            bar_img = rounded_bar_image(self.bar_w, self.bar_h, remaining_frac, bar_color)
            self._bar_img_tk = ImageTk.PhotoImage(bar_img)
            self.canvas.itemconfig(self._bar_item, image=self._bar_img_tk)
        except Exception:
            pass

        self._widget_state = icon_state
        self._widget_fraction = fraction
        self.root.after(1000, self._tick)

    def _animate(self):
        t = time.time()
        state = getattr(self, "_widget_state", "happy")
        fraction = getattr(self, "_widget_fraction", 0.0)
        amp = 3
        speed = 1.6
        if t < self.celebrate_until:
            amp = 7
            speed = 6.0
        bob = int(round(math.sin(t * speed) * amp))
        try:
            img = draw_character(state, self.widget_size, fraction=fraction)
            self._char_img_tk = ImageTk.PhotoImage(img)
            self.canvas.itemconfig(self._char_item, image=self._char_img_tk)
            self.canvas.coords(self._char_item, self.window_w // 2, self.padding_top + bob)
        except Exception:
            pass
        self._check_hover()
        self.root.after(70, self._animate)

    def run(self):
        self.root.mainloop()

def main():
    if "--test-notify" in sys.argv:
        cfg = load_config()
        notify(tr_text(cfg, "notify_test_title"), tr_text(cfg, "notify_test_msg"), cfg)
        print("Test bildirimi gonderildi (winotify kullanildi mi:", HAS_WINOTIFY, ")")
        return
    app = WaterReminderApp()
    app.run()


if __name__ == "__main__":
    main()
