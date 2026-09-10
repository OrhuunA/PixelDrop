"""PixelDrop giris noktasi (`python -m pixeldrop` ile de calistirilabilir)."""

import sys

from .config import load_config
from .i18n import tr_text
from .notify import HAS_WINOTIFY, notify


def main():
    if "--test-notify" in sys.argv:
        cfg = load_config()
        notify(tr_text(cfg, "notify_test_title"), tr_text(cfg, "notify_test_msg"), cfg)
        print("Test bildirimi gonderildi (winotify kullanildi mi:", HAS_WINOTIFY, ")")
        return

    # tkinter/pystray'e bagimli WaterReminderApp'i sadece gercekten
    # gerektiginde import ediyoruz ki `--test-notify` ve testler bu
    # agir/Windows'a bagimli baglantiyi tetiklemesin.
    from .ui.widget import WaterReminderApp

    app = WaterReminderApp()
    app.run()


if __name__ == "__main__":
    main()
