# PixelDrop

[Türkçe](README.md)

![License](https://img.shields.io/github/license/OrhuunA/PixelDrop)
![Platform](https://img.shields.io/badge/platform-Windows-0078D6)
![Python](https://img.shields.io/badge/python-3.9%2B-3776AB)
![Latest release](https://img.shields.io/github/v/release/OrhuunA/PixelDrop)
![Downloads](https://img.shields.io/github/downloads/OrhuunA/PixelDrop/total)

A lightweight Windows desktop tool that reminds you to drink water with a
pixel-art water drop mascot living on your screen (in the spirit of
TBH: Task Bar Hero).

## Screenshots

The mascot's states — from happy to thirsty:

![Mascot states](docs/img/mascot_states.png)

> A desktop screenshot, settings window, 7-day chart screenshot, and a
> short demo GIF are on the way (see the [roadmap](pixeldropyolharitasi.md),
> Turkish only for now).

## Download

**[Download the latest release (GitHub Releases)](https://github.com/OrhuunA/PixelDrop/releases/latest)**

> **Note:** Unsigned `.exe` files are sometimes flagged as "malware" by
> Windows SmartScreen, Chrome, or Windows Defender — a well-known false
> positive with PyInstaller-built apps in general, not a sign of actual
> malicious behavior in this code. See
> [Windows SmartScreen and antivirus warning](#windows-smartscreen-and-antivirus-warning)
> below for details and fixes.

Prefer to run from source instead? See
[Running (development)](#running-development) below.

## Features

- **Desktop widget**: A small, borderless, transparent, always-on-top
  character. Its expression changes over time: happy → neutral →
  thirsty → urgent (red, blinking). Drinking water makes it happy again
  with a short "cheer" animation.
- **Drag and drop**: Click-and-drag the character anywhere on screen
  (position is saved). A single click (no drag) = "I drank water".
- **Hovering** reveals three icons in the top-right corner: **💤** snoozes
  the next reminder by 5 minutes, **⚙** opens a small settings window
  (interval, size, daily goal, pause, auto-pause, sound, run at startup —
  all from the widget, no need to go to the tray), **✕** hides the
  widget (bring it back from the tray menu's "Show widget"). There's
  spacing between them to avoid mis-clicks, and whichever icon you click
  closer to is the one that gets picked.
- **Gradual drying**: the character's color slowly fades from a lively
  happy blue to a pale/reddish "dried out" look as time passes without
  drinking (brightness/moisture impression fades too), as a smooth,
  continuous transition rather than a sudden jump.
- **Progress bar**: A small bar plus countdown text below the widget
  showing time left until the next reminder.
- **Daily goal + streak**: Above the countdown, the widget shows a row of
  small cup icons for how many cups you've had today (filled/blue =
  drunk, empty/pale outline = remaining) — if the goal is above 8 it
  switches to text like "3/10 cups" due to space. Reaching the goal
  (default 8 cups, changeable in settings) makes the character cheer
  longer/more energetically and triggers a celebration notification.
  Past midnight (even if the app stayed open) the counter resets
  automatically; if yesterday's goal was met, the streak (consecutive
  days you hit your goal) increases by one, otherwise it resets. The
  streak count is shown in the settings window.
- **Auto-pause when idle/away**: If keyboard/mouse haven't been used for
  10 minutes, the reminder switches to "away" and pauses automatically
  (no notifications); once you're back, the timer resets and resumes
  normally, so reminders don't pile up while you're away from the
  computer. Can be turned off in settings.
- **Quick snooze from the reminder**: The 💤 icon on the widget, or "Snooze
  5 min" from the tray menu, delays the next reminder by 5 minutes.
- **7-day mini history in settings**: The settings window shows a small
  bar chart of how much water you drank over the last 7 days; days where
  you hit your goal are highlighted.
- **Language (Turkish / English)**: Switchable from the settings window;
  the widget, tray menu, settings window, and notification text (title/
  body) follow the selected language. Turkish is the default.
- **Tray icon**: The same mascot, in a smaller size, also sits in the
  system tray; right-click for all settings.
- **Interval**: Choose between 15/30/45/60/90/120 minutes.
- **Daily goal**: Choose between 4/6/8/10/12/15 cups.
- **Pause/Resume**, **Toggle notification sound**.
- **Run at Windows startup**: Starts automatically on boot.
- Native Windows 10/11 toast notifications (`winotify`) for reminders,
  plus a system sound (`winsound`) beep — the toast's own sound can
  sometimes be silenced by Windows notification settings (especially
  Focus Assist/game mode), so this second sound path is more reliable.

## Usage

- **Single click** the mascot on screen = I drank water (counter resets,
  one step closer to today's goal).
- **Drag** the mascot = move it.
- **💤** on the top-right of the mascot = snooze the next reminder by 5
  minutes, **⚙** = settings, **✕** = hide the widget (the app keeps
  running in the background from the tray icon).
- **Right-click** the tray icon = all settings (interval, daily goal,
  snooze, pause, auto-pause, show widget again, sound, run at startup,
  quit).

Settings (interval, daily goal, widget position/size, daily counter,
streak, history, etc.) are stored in
`%APPDATA%\PixelDrop\config.json`. (The app used to be called
"Su İçme Hatırlatıcı" — if the old
`%APPDATA%\SuIcmeHatirlatici\config.json` exists, it's automatically
copied to the new location once on first launch; no data is lost.)

## Running (development)

```
pip install -r requirements.txt
python main.py
```

To run silently in the background with no console window:

```
pythonw main.py
```

Easiest path: double-click `kur_ve_test_et.bat` — it installs
dependencies, sends a test notification, and starts the app (Turkish
prompts, but works regardless of your system language).

## Packaging as an .exe

Double-click `exe_olustur.bat` (or run it from a terminal). Output:
`dist\PixelDrop\PixelDrop.exe` (alongside a few support files, in a
single folder).

After packaging, toggle "Run at Windows startup" off and back on once so
the startup entry points at the .exe instead of the .py file.

### Windows SmartScreen and antivirus warning

Executables built with PyInstaller (especially the old single-file
`--onefile` mode) are frequently flagged by Windows Defender, Chrome's
safe browsing, and Google as "malware", because of how they extract
themselves to a temp folder at runtime. This is a well-known issue
affecting nearly every PyInstaller-based project — it does not mean the
code actually does anything malicious. The reason is simple: **a free,
unsigned open-source project has no code-signing certificate** (those
are paid, yearly certificates).

If you see a "Windows protected your PC" (SmartScreen) warning on the
downloaded file:

1. Click **"More info"** in the warning window.
2. Then click the **"Run anyway"** button that appears.

If Google/Chrome or Windows Defender is mistakenly blocking a specific
file, you can report it as a false positive:
[Microsoft file submission](https://www.microsoft.com/en-us/wdsi/filesubmission) ·
[Google Safe Browsing false-positive report](https://safebrowsing.google.com/safebrowsing/report_error/)
— review usually takes a few days.

To further reduce this:

- `exe_olustur.bat` now builds in `--onedir` (folder) mode with
  `--noupx`, which triggers fewer false positives than the single-file
  build.
- When sharing, zip the entire `dist\PixelDrop\` folder instead of
  sharing the bare `PixelDrop.exe`.

**The source code is fully open** — if you don't trust the download, you
can build it yourself on your own machine with `exe_olustur.bat`; an exe
you built yourself on your own computer won't trigger any download
warning at all.

## Notes / architecture

The code is split into modules under the `pixeldrop/` package (the
top-level `main.py` is now a thin launcher that calls
`pixeldrop.__main__` — `python main.py` and `exe_olustur.bat` keep
working exactly as before):

```
pixeldrop/
├── __main__.py      # entry point
├── config.py        # config.json read/write, migration from the old name, defaults
├── i18n/             # tr.json / en.json translation files + loader
├── notify.py         # winotify + winsound notifications
├── core/
│   ├── timer.py      # timing / snooze (pure functions)
│   ├── tracker.py    # day-rollover, goal, streak, history (pure functions)
│   ├── idle.py        # GetLastInputInfo wrapper
│   └── startup.py     # Windows startup registry entry
└── ui/
    ├── widget.py       # main mascot window
    ├── settings.py     # settings window
    ├── tray.py         # pystray integration
    └── mascot.py       # pixel-art drawing with Pillow
```

- UI: a transparent, borderless `tkinter` Toplevel window (stdlib, no
  extra install needed). The character's pixel-art is drawn with Pillow
  at runtime (no external image files).
- Tray icon: `pystray`, run via `run_detached()` so it doesn't block
  tkinter's main loop.
- Timing: instead of an extra thread/`sleep` loop, tkinter's `after()`
  calls are used (a state check once a second, a subtle "breathing"
  animation roughly every ~70ms) — keeping idle CPU usage close to zero.
- Auto-pause when idle/away measures time since the last keyboard/mouse
  input via Windows' `GetLastInputInfo` API (through stdlib `ctypes`, no
  extra install needed); the feature silently disables itself outside
  Windows or if the API isn't reachable.
- Daily goal/streak and the 7-day history are computed from the last 14
  days kept in `config.json`'s `history` field (date → cups drunk);
  day-rollover lives as a pure function in `core/tracker.py` (today's
  date is passed in, it never calls `datetime.now()` itself), and
  `_tick` checks it every second, so it resets correctly at midnight
  even if the app has been open all night.
- Languages now live outside the code, in `pixeldrop/i18n/tr.json` and
  `en.json`; the choice is stored in `config.json`'s `language` field.
  Widget/tray text re-reads the current language on every refresh; the
  settings window's static labels are updated by reopening the window
  when the language changes.
- A single `__version__` (`pixeldrop/__init__.py`) is shown in both the
  settings window and the tray icon's tooltip.
- `ruff` + `mypy` are configured via `pyproject.toml`; install with
  `pip install -r requirements-dev.txt`.
- The pure functions in `core/timer.py` and `core/tracker.py` are
  covered by `pytest` (day-rollover, streak math, history pruning,
  recovering from a corrupted config, migration from the old app name).
  Run the tests with `pytest` from the repo root after installing
  `requirements-dev.txt`.

## Contributing

Open an issue on the [Issues](https://github.com/OrhuunA/PixelDrop/issues)
tab for bugs or feature ideas — the templates there will ask for the
details needed (Windows version, steps, etc.). See the
[roadmap](pixeldropyolharitasi.md) (Turkish) for planned development
direction.

## License

[MIT](LICENSE)
