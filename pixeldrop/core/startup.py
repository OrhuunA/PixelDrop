"""Windows baslangicinda calistirma kaydi (HKCU...\\Run)."""

import os
import sys


def set_startup(enable, app_name, old_app_name):
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
            winreg.DeleteValue(key, old_app_name)
        except FileNotFoundError:
            pass

        if enable:
            if getattr(sys, "frozen", False):
                cmd = f'"{sys.executable}"'
            else:
                pythonw = sys.executable.replace("python.exe", "pythonw.exe")
                script = os.path.abspath(sys.argv[0])
                cmd = f'"{pythonw}" "{script}"'
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(key, app_name)
            except FileNotFoundError:
                pass
    finally:
        winreg.CloseKey(key)
