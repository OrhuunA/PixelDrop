"""Piksel-art karakter, ilerleme cubugu, bardak/simge cizimleri (Pillow).

Sadece Pillow ve stdlib'e bagli - Windows disinda da (ornegin testlerde)
sorunsuz calisir."""

import math

from PIL import Image, ImageDraw, ImageFont

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
