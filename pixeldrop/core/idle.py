"""Bosta/uzaktayken otomatik duraklama icin son kullanici girdisinden bu
yana gecen sureyi Windows API'siyle olcer. Baska platformda / hata
halinde 0 donup ozellik sessizce devre disi kalir."""

import os

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
