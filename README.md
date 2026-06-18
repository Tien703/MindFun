# Mindfun

> Not a blocker — a mindful pause.

Mindfun is a Windows app built on **Behavioral Friction**: instead of banning games, it creates a brief, intentional pause before you play — giving your rational mind a chance to decide, not your impulse.

---

## How It Works

1. 🎮 **You launch a game** → Mindfun detects it within 3 seconds via process polling
2. ⏸ **Game freezes instantly** → `NtSuspendProcess` suspends the entire process tree (no memory hacking, no anti-cheat flags)
3. 💭 **Mindful popup appears** → An always-on-top window (800×600, centered) shows a reflection question or checklist you configured
4. ⏱ **Countdown runs** → 15s / 1m / 3m / 5m depending on your Commitment Level
5. ✅ **Your choice** → Press **PLAY** to resume the game, or **QUIT** to close it
6. 📓 **All sessions logged** → Playtime and night violations are recorded locally

---

## Commitment Levels

| Mode | Wait Time | Night Guard |
|------|-----------|-------------|
| 🟢 Reminder | 15 seconds | Toast notification |
| 🟡 Discipline | 1 minute | Toast notification |
| 🟠 Rehab | 3 minutes | Toast warning |
| 🔴 Martial Law | 5 minutes | Toast warning |

---

## Night Guard (Sleep Lock)

Monitors gaming during your configured sleep hours (default 23:00–05:00):

- **All modes**: When a game is detected at night, sends a toast notification immediately
- **Mode 3–4**: Sends a stronger warning toast
- **On game exit**: Sends a summary toast ("you played X minutes past curfew")
- All violations are recorded in the Log tab with date, game, and duration

---

## Mindful Popup

The pause window is an **always-on-top floating panel** (800×600, centered on screen) — not a fullscreen cover. It:
- Uses `Qt.WindowStaysOnTopHint` and re-asserts `HWND_TOPMOST` every 500ms so it stays above the game
- Intercepts Alt+F4 via `WM_SYSCOMMAND` to prevent closing during countdown
- Disables PLAY/QUIT buttons until the countdown finishes
- Can be dragged to reposition
- Shows checklist tasks or random reflection questions from your configured groups

---

## Friction Lock (Anti-Cheat)

An optional setting that disables the **Quit** and **Pause** buttons in the system tray icon. When enabled:
- You cannot close Mindfun from the tray — you must open Task Manager
- This creates just enough friction to interrupt impulsive bypass
- Can be toggled off in Settings at any time (with a 5-second confirmation delay)

---

## Auto-Start

After installation, Mindfun registers itself to start with Windows via two methods:
1. **Registry Run key** — `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`
2. **Startup folder** — A `.bat` shortcut in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`

---

## Tech Stack

- **Python 3.11** + **PyQt5** — UI and event loop
- **ctypes** → `NtSuspendProcess` / `NtResumeProcess` — freeze/unfreeze game process trees
- **psutil** → 3-second process polling (no hooks, no kernel drivers)
- **winotify** → Windows toast notifications
- **Inno Setup** → Windows installer
- 100% local — zero network, zero telemetry

---

## Installation

Download and run `MindfunSetup.exe` from the [Releases](https://github.com/Tien703/MindFun/releases) page.

- No additional dependencies required
- Mindfun starts automatically with Windows after installation
- Settings are stored in `%APPDATA%\Mindfun\`

---

## Development

```bash
# Clone and install dependencies
git clone https://github.com/Tien703/MindFun.git
cd MindFun
pip install -r requirements.txt

# Run in dev mode
python main.py

# Show settings on startup
python main.py --settings
```

---

## Build

```bash
# Step 1: Package with PyInstaller
pyinstaller --onefile --windowed --icon=assets/icon.ico --name mindfun --add-data "data;data" --add-data "assets;assets" main.py

# Step 2: Build installer with Inno Setup
# Run: ISCC.exe installer/setup.iss
# Output: installer/Output/MindfunSetup.exe
```

---

## Project Structure

```
mindfun/
├── main.py                       # Entry point (Qt app + arg parsing)
├── core/
│   ├── config_manager.py         # Config/report/questions file I/O
│   ├── game_detector.py          # 3s polling, process suspension
│   ├── i18n.py                   # Vietnamese/English string tables
│   ├── night_guard.py            # Sleep lock monitoring (30s interval)
│   ├── process_controller.py     # NtSuspendProcess / NtResumeProcess
│   └── report_logger.py          # Playtime & violation session logging
├── ui/
│   ├── lockscreen.py             # Always-on-top pause popup (800×600)
│   ├── settings_window.py        # 4-tab settings window (PyQt5)
│   ├── tray_icon.py              # System tray icon & menu
│   ├── bar_chart.py              # Playtime bar chart widget
│   ├── game_manager_window.py    # Game list editor dialog
│   ├── quit_popup.py             # "Are you quitting?" follow-up popup
│   └── theme.py                  # Dark/light mode styles
├── service/
│   └── startup_manager.py        # Registry & Startup folder registration
├── data/                         # Default config, questions, presets
├── assets/                       # App icon
└── installer/setup.iss           # Inno Setup installer script
```

---

## Privacy & Ethics

- **Local-only**: Zero network activity. No analytics, no telemetry, no accounts.
- **Voluntary**: You install it because you want it. Uninstall cleanly via Add/Remove Programs.
- **No memory hacking**: Only OS-level process suspend — safe with anti-cheat systems.
- **Open Source**: Full source code available for review.
- **No hard blocking**: You can always choose to play. The goal is awareness, not prohibition.

---

## License

Open Source — MIT License.
