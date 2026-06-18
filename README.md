# Mindfun

> Not a blocker — a mindful pause.

Mindfun is a Windows application built on the principle of **Behavioral Friction**. Instead of banishing games entirely, it creates an intentional, structured pause before you play — giving your rational mind a chance to intervene over impulse.

---

## How It Works

1. 🎮 **Game Detection**: Polling active processes every 3 seconds using `psutil`. The monitoring is lightweight, case-insensitive, and operates without kernel hooks or drivers.
2. 🖥️ **Always-on-Top Overlay**: When a target game is detected (and not yet whitelisted), Mindfun creates a frameless, semi-transparent window overlay (800x600, centered on screen, draggable, and resizable) above the game.
3. ⏸️ **Window Minimization**: To resolve fullscreen overlay bypasses and secure the screen space, the target game's windows are automatically minimized (`ShowWindow(hwnd, SW_MINIMIZE)` via Windows API) during the active countdown.
4. 🔒 **Anti-Bypass Protection**: Keyboard shortcuts and window close commands (Alt+F4) are intercepted via native Win32 messages (`WM_SYSCOMMAND / SC_CLOSE`) during the countdown, preventing the user from bypassing the pause.
5. 📋 **Checklist & Questions Carousel**: The countdown duration is divided equally among enabled task groups (configured in Settings). The user reads reflection prompts or works through checklists, clicking **Next** to cycle through screens.
6. ⚖️ **Your Decision**: Once the timer expires:
   - Clicking **PLAY** whitelists the game for the session (until 05:00 next morning) and restores the game window.
   - Clicking **QUIT** restores the game window and displays a top-right banner reminding the user to manually exit the game process (which auto-closes once the game PID terminates).

---

## Commitment Levels

Users can configure one of four commitment modes which dictate the wait time, checklist restrictions, and nighttime enforcement behaviors:

| Mode | Name | Wait Time | Night Guard Behavior | Checklist Constraint |
|:---:|:---:|:---:|:---:|:---:|
| 🟢 **1** | **Reminder** | 15 seconds | Send toast notification | Reminder only |
| 🟡 **2** | **Discipline** | 1 minute | Send toast notification | Reminder only |
| 🟠 **3** | **Rehab** | 3 minutes | Trigger Lockscreen overlay + toast warning | Reminder only |
| 🔴 **4** | **Hardcore** | 5 minutes | Trigger Lockscreen overlay + toast warning | **Strict Block**: PLAY button is disabled until all checklist items are ticked |

*In Mode 4 (Hardcore), if any checklist items remain unchecked, the PLAY button is disabled and displays a red warning: `COMPLETE TASKS TO PLAY`.*

---

## Night Guard (Sleep Lock)

Monitors gaming activity during your configured bedtime hours (default `23:00` – `05:00`):

* **Mode 1 & 2 (Reminder & Discipline)**: Sends a toast notification on game launch and quietly logs violation minutes. Upon game exit, a summary toast is shown (e.g., *"You played X minutes past curfew"*). If the PC is shut down before exit, this notification is displayed upon next boot.
* **Mode 3 & 4 (Rehab & Hardcore)**: Instantly triggers the Lockscreen overlay to interrupt gameplay and sends a strong warning toast. Bedtime violations are recorded in the logs as `force_killed` (signifying forced Lockscreen intervention).
* **Daily Reset**: Every morning at `05:00` (or past the configured Day Start time on next launch), the session whitelist is cleared and daily checklist tasks are reset.

---

## Friction Lock (Anti-Cheat)

An optional setting that disables the **Quit Mindfun** and **Pause for Today** options in the system tray icon menu. 

* When enabled, you cannot close Mindfun directly — you must open the Windows Task Manager to kill `mindfun.exe`. This extra step introduces crucial behavioral friction to interrupt impulsive overrides.
* Can be toggled off in the Settings window under the **General Settings** tab, requiring a 5-second confirmation delay dialogue.

---

## Installation & Files

Mindfun is packaged as a standard installer executable (`MindfunSetup.exe`) using **Inno Setup 6**.

### Deployment Paths
* **Application Files**: The executable (`mindfun.exe`) and icons are placed in the program directory:
  ```
  C:\Program Files (x86)\Mindfun\   (or User-configured path)
  ```
* **User Config & Logs**: Configuration files, questions, and records are stored locally per-user in:
  ```
  %APPDATA%\Mindfun\                (e.g., C:\Users\<Username>\AppData\Roaming\Mindfun)
  ```
  - `config.json`: Core preferences, sleep time, commitment mode, and whitelists.
  - `questions.json`: Mindfulness questions and checklist items (resets daily).
  - `report.json`: Logged gaming sessions, playtimes, and bedtime violations.
  - `logs/mindfun.log`: Running log file of the application background threads.

### Registry Integration
* Mindfun registers itself to start automatically with Windows via the registry key:
  `HKCU\Software\Microsoft\Windows\CurrentVersion\Run\Mindfun`

### Clean Uninstallation
The uninstaller cleanly cleanses the system by:
1. Running a background `taskkill /f /im mindfun.exe` to terminate any running instances.
2. Deleting the registry auto-start key and shortcuts.
3. Prompting the user with a dialogue: *"Do you want to keep your Mindfun settings and logs?"*. Selecting **No** completely wipes the `%APPDATA%\Mindfun\` data directory.

---

## Tech Stack

* **Python 3.11+**
* **PyQt5**: GUI layout, system tray menu, and stacked page carousels.
* **ctypes**: Windows API hooks for:
  - `SetWindowPos` to assert `HWND_TOPMOST` every 500ms.
  - `ShowWindow` with `SW_MINIMIZE` & `SW_RESTORE` to minimize/restore target game windows.
  - Intercepting native events (`WM_SYSCOMMAND / SC_CLOSE`) to block Alt+F4.
* **psutil**: Case-insensitive process enumeration and PID checks (zero-hook, safe against Vanguard / EAC / Ricochet).
* **winotify**: Native Windows toast notification popups.
* **PyInstaller**: Packages the script and data folders into a standalone Windows executable.
* **Inno Setup 6**: Compiles the final setup package.

---

## Development

```bash
# Clone the repository
git clone https://github.com/Tien703/MindFun.git
cd MindFun

# Install requirements
pip install -r requirements.txt

# Run main app (Tray + Detector)
python main.py

# Launch settings directly on startup
python main.py --settings
```

---

## Build

```bash
# Step 1: Package application using PyInstaller
pyinstaller --onefile --windowed --icon=assets/icon.ico --name mindfun --add-data "data;data" --add-data "assets;assets" main.py

# Step 2: Build installer with Inno Setup
# Compile installer/setup.iss using the Inno Setup GUI Compiler or via CLI:
# ISCC.exe installer/setup.iss
```

---

## Project Structure

```
mindfun/
├── main.py                       # Main controller & event loop
├── core/
│   ├── config_manager.py         # Thread-safe config & JSON file I/O
│   ├── game_detector.py          # 3s process scanning and whitelist management
│   ├── i18n.py                   # Localized translation tables (English & Vietnamese)
│   ├── night_guard.py            # Sleep monitoring and nightly curfew rules
│   ├── process_controller.py     # Process checking helpers
│   └── report_logger.py          # Session report logger
├── ui/
│   ├── lockscreen.py             # Frameless always-on-top overlay window
│   ├── settings_window.py        # Tabbed configuration manager
│   ├── tray_icon.py              # Tray interface and friction lock status
│   ├── bar_chart.py              # PyQt Chart widget displaying playtimes
│   ├── game_manager_window.py    # Game presets & custom exe manager dialog
│   ├── quit_popup.py             # Top banner prompting manual game exits
│   └── theme.py                  # Colors & styles for light/dark mode
├── service/
│   └── startup_manager.py        # Startup batch scripts & shortcut config
├── data/                         # Bundled default JSON presets & checklists
├── assets/                       # Icon assets (.ico, .png)
└── installer/
    ├── setup.iss                 # Inno Setup installation script
    └── Output/
        └── MindfunSetup.exe      # Compiled final installer
```

---

## Privacy & Ethics

* **Local-First**: 100% offline. No analytics, no telemetry, no cloud synchronization.
* **Voluntary Control**: You install it because you want it. Can be cleanly uninstalled at any time.
* **Anti-Cheat Safe**: No memory reading, code injection, or process freezing. Safe to run alongside Vanguard, EAC, BattlEye, and Ricochet.
* **No Rigid Blocks**: You are always given the option to play after reflecting. The target is mindfulness, not strict restriction.

---

## License

Open Source — **MIT License**.
