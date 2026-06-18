# Mindfun

> Không cấm đoán — chỉ tạo khoảng dừng tỉnh thức (Mindful Pause)

Mindfun is a Windows utility that uses **Behavioral Friction** to help you control competitive gaming habits. It doesn't block games — it creates a mindful pause before you play, giving your rational mind time to weigh in.

## How It Works

1. 🎮 **You launch a game** → Mindfun detects it within 3 seconds
2. ⏸ **Game freezes** → `NtSuspendProcess` freezes the game (no memory hacking)
3. 💭 **Mindful pause** → A fullscreen overlay shows a reflection question
4. ⏱ **Countdown** → Wait 15s/60s/180s/300s depending on your commitment level
5. ✅ **Your choice** → "I still want to play" or "Quit & do something else"
6. 🔓 **Decision respected** → Game resumes or closes based on YOUR choice

## Modes

| Mode | Wait Time | For... |
|------|-----------|--------|
| 🟢 Reminder | 15 seconds | Good self-control |
| 🟡 Discipline | 1 minute | Easily caught in loops |
| 🟠 Rehab | 3 minutes | Need an emergency brake |
| 🔴 Martial Law | 5 minutes | Night lockdown, no negotiation |

## Night Guard (23:00–05:00)

- **Mode 1-3**: Silent logging — Mindfun tracks how long you play past curfew and shows a summary toast when you're done
- **Mode 4**: Hardcore — game is killed immediately with a notification

## Anti-Bypass Design

Mindfun uses the **"Suspended Game Hostage"** pattern:
- Kill Mindfun from Task Manager → game stays frozen (nobody calls resume)
- Must kill the game too → restart triggers Mindfun again (auto-restart in 10s)
- Bypassing is harder than just waiting through the countdown

## Tech Stack

- **Python 3.11+** with **PyQt5**
- **ctypes** → `NtSuspendProcess` / `NtResumeProcess` (no anti-cheat flags)
- **psutil** → Process detection via polling (no hooks)
- **winotify** → Windows toast notifications
- Local-only, no network, no telemetry

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run in development mode
python main.py

# Run watchdog separately (for testing)
python main.py --watchdog
```

## Build

```bash
# Step 1: Build .exe with PyInstaller
pyinstaller --onefile --noconsole --icon=assets/icon.ico main.py

# Step 2: Build installer with Inno Setup
# Open installer/setup.iss in Inno Setup Compiler and build
```

## Project Structure

```
mindfun/
├── main.py                       # Entry point
├── core/
│   ├── config_manager.py         # Config loading/saving
│   ├── game_detector.py          # 3s polling process scanner
│   ├── i18n.py                   # Vietnamese/English strings
│   ├── night_guard.py            # Night-time rules
│   ├── process_controller.py     # NtSuspendProcess/NtResumeProcess
│   └── report_logger.py          # Violation logging
├── ui/
│   ├── lockscreen.py             # Fullscreen countdown overlay
│   ├── settings_window.py        # 4-tab settings (PyQt5)
│   └── tray_icon.py              # System tray icon
├── service/
│   └── startup_manager.py        # Startup registration (Registry + Startup folder)
├── data/                         # Default data files
├── assets/                       # Icons
└── installer/setup.iss           # Inno Setup script
```

## Privacy & Ethics

- **Local-only**: Zero network activity. No analytics, no telemetry.
- **Voluntary**: You install it because you want it. Clear uninstall via Add/Remove Programs.
- **No memory hacking**: Only OS-level process suspend, no game memory reading/writing.
- **Open Source**: Full source code available for community review.

## License

Open Source — see LICENSE file.
