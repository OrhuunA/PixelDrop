"""Sistem tepsisi (tray) entegrasyonu - pystray.

Buradaki fonksiyonlar bir `app` nesnesi alir (pixeldrop.ui.widget.
WaterReminderApp): dogrudan pystray'e bagimli kodu widget'in geri kalanindan
ayirmak icin `self` yerine `app` parametre olarak geciliyor, ama davranis
(menu ogeleri, checked/radio durumlari) birebir ayni."""

import threading

import pystray

from .. import __version__
from ..config import APP_NAME, INTERVAL_CHOICES
from ..core.timer import SNOOZE_MINUTES
from .mascot import draw_character


def _tray_title(app):
    return f"{app.t('app_title')} v{__version__}"


def build_menu(app):
    def interval_item(minutes):
        return pystray.MenuItem(
            lambda item, m=minutes: app.t("tray_interval_item", m=m),
            lambda icon, item, m=minutes: app.set_interval(m),
            checked=lambda item, m=minutes: app.cfg["interval_minutes"] == m,
            radio=True,
        )

    return pystray.Menu(
        pystray.MenuItem(
            lambda item: app.t(
                "tray_today",
                drank=app.cfg['drank_today'],
                goal=app.cfg.get('daily_goal', 8),
                streak=app.cfg.get('streak', 0),
            ),
            None, enabled=False,
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(lambda item: app.t("tray_drank"), lambda icon, item: app.mark_drank()),
        pystray.MenuItem(lambda item: app.t("tray_snooze", m=SNOOZE_MINUTES),
                          lambda icon, item: app.snooze()),
        pystray.MenuItem(
            lambda item: app.t("tray_show_widget") if not app.cfg["widget_visible"]
            else app.t("tray_hide_widget"),
            app._toggle_widget,
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(lambda item: app.t("tray_interval"),
                          pystray.Menu(*[interval_item(m) for m in INTERVAL_CHOICES])),
        pystray.MenuItem(
            lambda item: app.t("tray_resume") if app.cfg["paused"] else app.t("tray_pause"),
            app.toggle_pause,
        ),
        pystray.MenuItem(
            lambda item: app.t("tray_auto_pause"), app.toggle_auto_pause,
            checked=lambda item: app.cfg.get("auto_pause_enabled", True),
        ),
        pystray.MenuItem(lambda item: app.t("tray_sound"), app.toggle_sound,
                          checked=lambda item: app.cfg["sound"]),
        pystray.MenuItem(
            lambda item: app.t("tray_startup"), app.toggle_startup,
            checked=lambda item: app.cfg["run_at_startup"],
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(lambda item: app.t("tray_quit"), app.quit_app),
    )


def build_tray_icon(app):
    icon = pystray.Icon(APP_NAME, draw_character("happy", 64), _tray_title(app), menu=build_menu(app))
    try:
        icon.run_detached()
    except AttributeError:
        threading.Thread(target=icon.run, daemon=True).start()
    return icon


def refresh_title(app):
    """Dil degistiginde tepsi ikonunun ipucu (tooltip) metnini gunceller."""
    try:
        app.icon.title = _tray_title(app)
    except Exception:
        pass
