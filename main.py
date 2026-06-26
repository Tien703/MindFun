"""
Mindfun — Main Entry Point

Orchestrates all components:
- Game detector (3s polling)
- Night guard (30s monitoring)
- System tray icon
- Lockscreen popup (on game detection)
- Settings window

Usage:
    python main.py              → Run main app (tray + detection)
    python main.py --settings   → Open settings on startup
"""

import sys
import os
import logging
import argparse
from typing import Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QMetaObject, Qt, Q_ARG, QObject, pyqtSignal, QSharedMemory, pyqtSlot

from core.config_manager import load_config
from core.i18n import set_language
from core.game_detector import GameDetector
from core.night_guard import NightGuard
from service.startup_manager import register_all_startup

# ─── Logging Setup ───────────────────────────────────────────────────

LOG_DIR = os.path.join(os.environ.get("APPDATA", ""), "Mindfun", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "mindfun.log"), encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("mindfun")


# ─── Signals ────────────────────────────────────────────────────────

class AppSignals(QObject):
    game_detected = pyqtSignal(str, int, object, object)

# ─── Application Class ──────────────────────────────────────────────

class MindfunApp(QObject):
    """Main application controller."""

    def __init__(self, show_settings=False):
        super().__init__()
        self._app = QApplication(sys.argv)
        self._app.setQuitOnLastWindowClosed(False)  # Keep running with just the tray

        # Single instance lock
        self._shared_mem = QSharedMemory("MindfunSharedInstanceLock")
        if not self._shared_mem.create(1):
            try:
                from winotify import Notification
                import os
                icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets", "icon.ico"))
                toast = Notification(
                    app_id="Mindfun",
                    title="Mindfun",
                    msg="Mindfun already running!",
                    icon=icon_path if os.path.exists(icon_path) else ""
                )
                toast.show()
            except Exception as e:
                print(f"Toast failed: {e}")
            sys.exit(0)

        # Load config and set language
        config = load_config()
        set_language(config.get("language", "vi"))

        # Import UI components (after QApplication is created)
        from ui.tray_icon import TrayIcon
        from ui.settings_window import SettingsWindow
        from ui.lockscreen import LockScreen

        self._LockScreen = LockScreen  # Store class reference for later instantiation

        # Active lockscreens
        self._active_lockscreens: list = []

        # ── Initialize components ──

        # Game detector
        self._detector = GameDetector(on_game_detected=self._on_game_detected)

        # Determine icon path
        icon_path = self._find_icon()

        # Tray icon
        self._tray = TrayIcon(
            icon_path=icon_path,
            on_open_settings=self._open_settings,
            on_view_log=self._view_log,
            on_pause_today=self._pause_today,
            on_resume=self._resume,
            on_quit=self._quit,
            on_reset_whitelist=self._detector.reset_whitelist,
        )

        # Settings window (lazy, created once)
        self._settings: Optional[SettingsWindow] = None

        # Signals for cross-thread UI updates
        self._signals = AppSignals()
        self._signals.game_detected.connect(self._show_lockscreen)

        # Night guard
        self._night_guard = NightGuard(
            on_whitelist_reset=self._on_whitelist_reset,
            on_toast=self._show_toast,
            on_night_lockdown=lambda exe, pid, is_soft: QMetaObject.invokeMethod(
                self, "_show_sleep_lockscreen", Qt.QueuedConnection,
                Q_ARG(str, exe), Q_ARG(int, pid), Q_ARG(bool, is_soft)
            ),
        )

        if show_settings:
            # We must use a timer to show it after event loop starts
            QTimer.singleShot(500, self._open_settings)

    def _find_icon(self) -> str:
        """Find the application icon file."""
        candidates = [
            os.path.join(os.path.dirname(__file__), "assets", "icon.ico"),
            os.path.join(os.path.dirname(__file__), "assets", "icon.png"),
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
        return ""

    def run(self):
        """Start all components and enter the Qt event loop."""
        logger.info("═══ Mindfun starting ═══")

        # Register startup methods (idempotent)
        try:
            register_all_startup()
        except Exception as e:
            logger.warning("Startup registration failed (non-fatal): %s", e)

        # Start detection
        self._detector.start()
        self._night_guard.start()

        # Show tray icon
        self._tray.show()

        logger.info("All components started, entering event loop")
        exit_code = self._app.exec_()

        # Cleanup
        self._detector.stop()
        self._night_guard.stop()
        logger.info("═══ Mindfun stopped ═══")

        return exit_code

    # ─── Game Detection Callback ─────────────────────────────────────

    def _on_game_detected(self, game_exe: str, game_pid: int,
                          launcher_exe: Optional[str], launcher_pid: Optional[int]):
        """
        Called by GameDetector when a new game is found.
        Emit a signal to safely show the lockscreen on the main (Qt) thread.
        """
        logger.info("Game detected: %s (PID %d)", game_exe, game_pid)
        self._signals.game_detected.emit(game_exe, game_pid, launcher_exe, launcher_pid)

    @pyqtSlot(str, int, bool)
    def _show_sleep_lockscreen(self, game_exe: str, game_pid: int, is_soft: bool = False):
        """Create and show the strict sleep lockscreen."""
        # Check if already showing
        self._active_lockscreens = [w for w in self._active_lockscreens if w.isVisible()]
        for w in self._active_lockscreens:
            if type(w).__name__ == "LockScreen" and getattr(w, "_is_sleep_lock", False):
                return
            if type(w).__name__ == "QuitPopup" and getattr(w, "_game_exe", "").lower() == game_exe.lower():
                return
                
        lockscreen = self._LockScreen(
            game_exe=game_exe,
            game_pid=game_pid,
            on_play=self._on_user_play,
            on_quit=self._on_user_quit,
            is_sleep_lock=True,
            is_soft_sleep_lock=is_soft
        )
        self._active_lockscreens.append(lockscreen)
        lockscreen.show()

    def _show_lockscreen(self, game_exe: str, game_pid: int,
                         launcher_exe: Optional[str], launcher_pid: Optional[int]):
        """Create and show the lockscreen (runs on Qt main thread)."""
        # Clean up any closed windows to avoid memory leak
        self._active_lockscreens = [w for w in self._active_lockscreens if w.isVisible()]

        # Prevent duplicate lockscreens if one is already showing
        logger.info("_active_lockscreens: %s", [type(w).__name__ for w in self._active_lockscreens])
        for w in self._active_lockscreens:
            if type(w).__name__ == "LockScreen":
                logger.info("Lockscreen already visible. Skipping duplicate spawn for %s (PID %d)", game_exe, game_pid)
                # Remove this PID from active so it can be detected again when current lockscreen finishes
                self._detector.remove_active_pid(game_pid)
                return
            if type(w).__name__ == "QuitPopup" and getattr(w, "_game_exe", "").lower() == game_exe.lower():
                # Quit popup is already telling them to quit this game
                self._detector.remove_active_pid(game_pid)
                return

        config = load_config()
        from core.night_guard import is_night_time
        
        # Check night block before showing lockscreen
        if is_night_time():
            mode = config.get("mode", 2)
            is_hardcore = mode >= 3
            if mode == 5:
                is_hardcore = config.get("custom_mode", {}).get("sleep_lock") == "lock"

            if is_hardcore:
                # Instead of killing, we just show the lockscreen and log violation
                logger.info("HARDCORE: Overlaying new launch %s during night hours", game_exe)
                from core import report_logger
                from core.i18n import t
                    
                # Log violation
                session_index = report_logger.start_session(game_exe, config.get("night_start", "23:00"))
                report_logger.mark_force_killed(session_index)
                report_logger.mark_notified(session_index)
                
                # Show popup
                from datetime import datetime
                now_str = datetime.now().strftime("%H:%M")
                self._show_toast(t("toast_title"), t("toast_hardcore_kill", time=now_str))
                self._show_sleep_lockscreen(game_exe, game_pid, is_soft=False)
                return
            else:
                logger.info("SOFT SLEEP LOCK: Game launched at night in reminder mode. Spawning soft sleep lockscreen.")
                self._show_sleep_lockscreen(game_exe, game_pid, is_soft=True)
                return

        # Normal lockscreen behavior
        lockscreen = self._LockScreen(
            game_exe=game_exe,
            game_pid=game_pid,
            launcher_exe=launcher_exe,
            launcher_pid=launcher_pid,
            on_play=self._on_user_play,
            on_quit=self._on_user_quit,
        )
        self._active_lockscreens.append(lockscreen)
        lockscreen.show()

    def _on_user_play(self, game_exe: str, game_pid: int):
        """User chose to continue playing — whitelist this game."""
        self._detector.whitelist_game(game_exe)
        self._detector.remove_active_pid(game_pid)
        logger.info("User chose PLAY for %s — whitelisted", game_exe)

    def _on_user_quit(self, game_exe: str, game_pid: int):
        """User chose to quit — wait for game to be closed via QuitPopup."""
        logger.info("User chose QUIT for %s, spawning QuitPopup", game_exe)
        from ui.quit_popup import QuitPopup
        
        # Spawn popup and keep a reference so it isn't garbage collected
        popup = QuitPopup(game_exe, game_pid, self._on_quit_popup_closed)
        self._active_lockscreens.append(popup)
        popup.show()

    def _on_quit_popup_closed(self, game_exe: str, game_pid: int):
        """Called when the QuitPopup confirms the game PID is dead."""
        self._detector.remove_active_pid(game_pid)
        logger.info("Game %s finally closed by user", game_exe)

    # ─── Night Guard Callbacks ───────────────────────────────────────

    def _on_whitelist_reset(self):
        """Called at 05:00 to reset the whitelist."""
        self._detector.reset_whitelist()
        logger.info("Daily whitelist reset")

    def _show_toast(self, title: str, message: str):
        """Show a toast notification via the tray icon."""
        try:
            # Try winotify first for persistent notifications
            from winotify import Notification
            toast = Notification(
                app_id="Mindfun",
                title=title,
                msg=message,
                duration="long",
            )
            toast.show()
        except Exception:
            # Fallback to QSystemTrayIcon notification
            self._tray.show_toast(title, message)

    # ─── UI Actions ──────────────────────────────────────────────────

    def _open_settings(self):
        """Open or show the settings window."""
        if self._settings is None:
            from ui.settings_window import SettingsWindow
            from PyQt5.QtGui import QIcon
            self._settings = SettingsWindow(
                on_config_changed=self._on_config_changed,
                on_language_changed=self._on_language_changed,
            )
            icon_path = self._find_icon()
            if icon_path:
                self._settings.setWindowIcon(QIcon(icon_path))
        self._settings.show()
        self._settings.raise_()
        self._settings.activateWindow()

    def _view_log(self):
        """Open settings to the log tab."""
        if self._settings is None:
            from ui.settings_window import SettingsWindow
            from PyQt5.QtGui import QIcon
            self._settings = SettingsWindow(
                on_config_changed=self._on_config_changed,
                on_language_changed=self._on_language_changed,
            )
            icon_path = self._find_icon()
            if icon_path:
                self._settings.setWindowIcon(QIcon(icon_path))
        self._settings.show_log_tab()

    def _on_config_changed(self):
        """Called when config is modified via settings."""
        self._tray.refresh_menu()
        logger.info("Config changed — menu refreshed")
        
        # Removed anti-cheat toggle check

    def _on_language_changed(self):
        """Called when the language is changed."""
        config = load_config()
        set_language(config.get("language", "vi"))
        self._tray.refresh_menu()

    def _pause_today(self):
        """Pause game detection for today."""
        self._detector.pause()
        self._tray.set_paused(True)
        logger.info("Mindfun paused for today")

    def _resume(self):
        """Resume game detection."""
        self._detector.resume()
        self._tray.set_paused(False)
        logger.info("Mindfun resumed")

    def _quit(self):
        """Clean quit."""
        logger.info("User requested quit")
        self._detector.stop()
        self._night_guard.stop()


# ─── Entry Point ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Mindfun — Behavioral Friction for Gaming")
    parser.add_argument("--settings", action="store_true", help="Show settings window on startup")
    args = parser.parse_args()

    app = MindfunApp(show_settings=args.settings)
    sys.exit(app.run())


if __name__ == "__main__":
    main()
