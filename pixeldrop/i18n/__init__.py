"""Turkce/Ingilizce arayuz metinleri.

Metinler artik koddan degil, bu paketin yaninda duran `tr.json` /
`en.json` dosyalarindan okunuyor (bkz. pixeldropyolharitasi.md, madde
3.2) - ucuncu bir dil eklemek icin sadece yeni bir `<kod>.json` dosyasi
yeterli, kod degisikligi gerekmiyor."""

import json
from pathlib import Path

_DIR = Path(__file__).resolve().parent
_DEFAULT_LANG = "tr"
_cache = {}


def _load(lang):
    if lang not in _cache:
        path = _DIR / f"{lang}.json"
        with open(path, "r", encoding="utf-8") as f:
            _cache[lang] = json.load(f)
    return _cache[lang]


def available_languages():
    """Yaninda `<kod>.json` dosyasi bulunan dil kodlarini dondurur."""
    return sorted(p.stem for p in _DIR.glob("*.json"))


def tr_text(cfg, key, **kwargs):
    lang = cfg.get("language", _DEFAULT_LANG)
    try:
        table = _load(lang)
    except Exception:
        table = {}
    try:
        fallback = _load(_DEFAULT_LANG)
    except Exception:
        fallback = {}
    s = table.get(key, fallback.get(key, key))
    if kwargs:
        try:
            return s.format(**kwargs)
        except Exception:
            return s
    return s
