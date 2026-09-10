"""Ayarlar penceresi (tkinter Toplevel).

`open_settings(app)` orijinal `WaterReminderApp._open_settings` metodunun
birebir tasinmis hali; `self` yerine `app` parametresi kullaniliyor ki bu
modul widget.py'den bagimsiz kalabilsin."""

import tkinter as tk
from datetime import date, timedelta

from .. import __version__
from ..config import GOAL_CHOICES, INTERVAL_CHOICES, WIDGET_MAX, WIDGET_MIN

# Ayarlar penceresi - koyu tema
SETTINGS_BG = "#1e1e22"
SETTINGS_FG = "#e6e6e6"
SETTINGS_MUTED = "#9a9a9a"
SETTINGS_FIELD_BG = "#2a2a30"
SETTINGS_BTN_BG = "#33333a"
SETTINGS_BTN_ACTIVE = "#3d3d46"
SETTINGS_ACCENT = "#4fa8e8"


def open_settings(app):
    win = app._settings_win
    if win is not None:
        try:
            win.deiconify()
            win.lift()
            win.focus_force()
            return
        except tk.TclError:
            app._settings_win = None

    win = tk.Toplevel(app.root)
    app._settings_win = win
    win.title(app.t("settings_title"))
    win.resizable(False, False)
    win.attributes("-topmost", True)
    win.configure(bg=SETTINGS_BG)

    ox, oy = app.overlay.winfo_x(), app.overlay.winfo_y()
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

    char_size_label = label(win, text=app.t("settings_char_size"))
    char_size_label.pack(anchor="w", padx=12, pady=(4, 0))
    size_var = tk.IntVar(value=app.widget_size)
    tk.Scale(win, from_=WIDGET_MIN, to=WIDGET_MAX, orient="horizontal", length=200,
             resolution=10, variable=size_var, showvalue=True,
             command=lambda v: app._apply_size(v),
             bg=SETTINGS_BG, fg=SETTINGS_FG, troughcolor=SETTINGS_FIELD_BG,
             activebackground=SETTINGS_ACCENT, highlightthickness=0,
             bd=0).pack(anchor="w", padx=6, pady=(0, 5))

    row = tk.Frame(win, bg=SETTINGS_BG)
    row.pack(anchor="w", **pad)
    interval_label = label(row, text=app.t("settings_interval"))
    interval_label.pack(side="left")
    interval_var = tk.IntVar(value=app.cfg["interval_minutes"])
    option_menu(row, interval_var, INTERVAL_CHOICES,
                lambda v: app.set_interval(int(v))).pack(side="left", padx=6)
    interval_unit_label = label(row, text=app.t("settings_min"))
    interval_unit_label.pack(side="left")

    row2 = tk.Frame(win, bg=SETTINGS_BG)
    row2.pack(anchor="w", **pad)
    goal_label = label(row2, text=app.t("settings_daily_goal"))
    goal_label.pack(side="left")
    goal_var = tk.IntVar(value=app.cfg.get("daily_goal", 8))
    option_menu(row2, goal_var, GOAL_CHOICES,
                lambda v: app.set_daily_goal(int(v))).pack(side="left", padx=6)
    goal_unit_label = label(row2, text=app.t("settings_cups"))
    goal_unit_label.pack(side="left")

    row3 = tk.Frame(win, bg=SETTINGS_BG)
    row3.pack(anchor="w", **pad)
    lang_label = label(row3, text=app.t("settings_language"))
    lang_label.pack(side="left")
    lang_display = [app.t("lang_tr"), app.t("lang_en")]
    lang_var = tk.StringVar(value=app.t("lang_tr") if app.cfg.get("language", "tr") == "tr"
                             else app.t("lang_en"))
    option_menu(row3, lang_var, lang_display,
                lambda v: app.set_language("tr" if v == app.t("lang_tr") else "en")).pack(side="left", padx=6)

    last7_label = label(win, text=app.t("settings_last7"))
    last7_label.pack(anchor="w", padx=12, pady=(6, 0))
    hist_canvas = tk.Canvas(win, width=204, height=68, bg=SETTINGS_BG, highlightthickness=0)
    hist_canvas.pack(anchor="w", padx=10, pady=(2, 4))

    def draw_history():
        hist_canvas.delete("all")
        goal = max(1, app.cfg.get("daily_goal", 8))
        history = app.cfg.get("history", {})
        today = date.today()
        days = []
        for i in range(6, -1, -1):
            d_ = today - timedelta(days=i)
            count = app.cfg.get("drank_today", 0) if d_ == today else history.get(str(d_), 0)
            days.append((d_, count))
        max_val = max(goal, max((c for _, c in days), default=0), 1)
        weekday_names = app.t("weekdays")
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

    paused_var = tk.BooleanVar(value=app.cfg["paused"])
    pause_cb = checkbutton(win, text=app.t("settings_pause"), variable=paused_var,
                            command=lambda: app.toggle_pause())
    pause_cb.pack(anchor="w", **pad)

    autopause_var = tk.BooleanVar(value=app.cfg.get("auto_pause_enabled", True))
    autopause_cb = checkbutton(win, text=app.t("settings_auto_pause"), variable=autopause_var,
                                command=lambda: app.toggle_auto_pause())
    autopause_cb.pack(anchor="w", **pad)

    sound_var = tk.BooleanVar(value=app.cfg["sound"])
    sound_cb = checkbutton(win, text=app.t("settings_sound"), variable=sound_var,
                            command=lambda: app.toggle_sound())
    sound_cb.pack(anchor="w", **pad)

    startup_var = tk.BooleanVar(value=app.cfg["run_at_startup"])
    startup_cb = checkbutton(win, text=app.t("settings_startup"), variable=startup_var,
                              command=lambda: app.toggle_startup())
    startup_cb.pack(anchor="w", **pad)

    bottom_row = tk.Frame(win, bg=SETTINGS_BG)
    bottom_row.pack(fill="x", padx=12, pady=(4, 10))
    version_label = label(bottom_row, text=f"PixelDrop v{__version__}",
                           fg=SETTINGS_MUTED, font=("Segoe UI", 8))
    version_label.pack(side="left")
    close_btn = tk.Button(bottom_row, text=app.t("settings_close"), command=win.destroy,
                           bg=SETTINGS_BTN_BG, fg=SETTINGS_FG,
                           activebackground=SETTINGS_BTN_ACTIVE, activeforeground=SETTINGS_FG,
                           highlightthickness=0, bd=0, padx=10, pady=3)
    close_btn.pack(side="right")

    def refresh_vars(event=None):
        goal = app.cfg.get("daily_goal", 8)
        streak = app.cfg.get("streak", 0)
        count_label.config(
            text=app.t("settings_count", drank=app.cfg['drank_today'], goal=goal, streak=streak)
        )
        size_var.set(app.widget_size)
        interval_var.set(app.cfg["interval_minutes"])
        goal_var.set(goal)
        lang_var.set(app.t("lang_tr") if app.cfg.get("language", "tr") == "tr" else app.t("lang_en"))
        paused_var.set(app.cfg["paused"])
        autopause_var.set(app.cfg.get("auto_pause_enabled", True))
        sound_var.set(app.cfg["sound"])
        startup_var.set(app.cfg["run_at_startup"])
        draw_history()

    refresh_vars()
    win.bind("<FocusIn>", refresh_vars)

    def on_destroy(event):
        if event.widget is win:
            app._settings_win = None
    win.bind("<Destroy>", on_destroy)
