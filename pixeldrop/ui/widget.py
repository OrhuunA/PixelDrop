"""Ana maskot penceresi (WaterReminderApp) - surukleme, hover ikonlari,
ilerleme cubugu, gunluk hedef gostergesi ve tum tick/animasyon dongusu."""

import math
import time
import tkinter as tk
from datetime import date

from PIL import ImageTk

from ..config import (
    APP_NAME,
    APP_TITLE,
    OLD_APP_NAME,
    WIDGET_MAX,
    WIDGET_MIN,
    WIDGET_SIZE_DEFAULT,
    load_config,
    save_config,
)
from ..core import tracker
from ..core.idle import get_idle_seconds
from ..core.startup import set_startup
from ..core.timer import AUTO_PAUSE_IDLE_MINUTES, SNOOZE_MINUTES, current_fraction, state_for_fraction
from ..i18n import tr_text
from ..notify import notify
from . import settings as settings_ui
from . import tray
from .mascot import (
    cups_row_image,
    draw_character,
    render_pixel_text,
    rounded_bar_image,
    _icon_close_image,
    _icon_gear_image,
    _icon_snooze_image,
)

WIDGET_PADDING_TOP_DEFAULT = 14   # bob animasyonu icin ust bosluk
FOOTER_DEFAULT = 52               # ilerleme cubugu + hedef bardaklari + etiket alani
BAR_MARGIN_DEFAULT = 10
BAR_H_DEFAULT = 7
TRANSPARENT_KEY = "#ff00fe"
LABEL_TEXT_COLOR = (150, 150, 158)   # geri sayim yazisi - soluk ama artik net (pembe leke yok)
GOAL_TEXT_COLOR = (122, 172, 202)    # buyuk hedeflerde ("N/M bardak") kullanilan metin yedegi
HOVER_ICON_COLOR = (172, 172, 178)   # 💤/⚙/✕ ucu - uc simge de artik ayni renk, elle cizilmis
CLOSE_BTN_R = 6


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
        dogru calisir. Asil mantik core.tracker.roll_day icinde saf bir
        fonksiyon olarak yasiyor (bkz. testler)."""
        new_cfg = tracker.roll_day(self.cfg, date.today())
        if new_cfg is not self.cfg:
            self.cfg = new_cfg
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
        # Ucu de kendi cizdigimiz duz simgeler (bkz. mascot._icon_*_image):
        # eskiden 💤/⚙ Unicode/emoji glifleriydi ve Windows'un
        # -transparentcolor penceresinde belirgin bir pembe/mor lekeye
        # donusuyordu (renkli emoji ve bazi sembol glifleri kismi saydam
        # kenarlarla dolu). Tamamen opak, elle cizilmis bu simgeler asla
        # lekelenmiyor ve ucu de garanti ayni renkte cikiyor.
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
        settings_ui.open_settings(self)

    # ---------------- tray ----------------
    def _build_tray(self):
        self.icon = tray.build_tray_icon(self)

    def _build_menu(self):
        return tray.build_menu(self)

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
        tray.refresh_title(self)
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
            set_startup(self.cfg["run_at_startup"], APP_NAME, OLD_APP_NAME)
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
        return current_fraction(self.next_at, self.cfg["interval_minutes"], time.time())

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
