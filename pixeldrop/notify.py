"""Windows toast bildirimi (winotify) + yedek sistem sesi (winsound)."""

from .config import APP_TITLE

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
