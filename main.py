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
    play_time_tick = pyqtSignal(int)

# ─── Application Class ──────────────────────────────────────────────

class MindfunApp(QObject):
    """Main application controller."""

    def __init__(self, show_settings=False, test_onboarding=False):
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

        self._icon_path = self._find_icon()
        self._show_settings_on_start = show_settings

        # Signals for cross-thread UI updates
        self._signals = AppSignals()
        self._signals.game_detected.connect(self._show_lockscreen)
        self._signals.play_time_tick.connect(self._show_play_time_bubble)

        self._settings: Optional[SettingsWindow] = None
        self._detector = None
        self._overlay_bubble = None
        self._tray = None
        self._night_guard = None

        config = load_config()
        if test_onboarding or not config.get("onboarding_completed", False):
            from ui.onboarding_window import OnboardingWindow
            self._onboarding = OnboardingWindow()
            self._onboarding.on_finished.connect(self._start_services)
            self._onboarding.show()
        else:
            self._start_services()

    def _start_services(self):
        """Start all background components and main UI (called after onboarding or immediately)."""
        # Game detector
        self._detector = GameDetector(
            on_game_detected=self._on_game_detected,
            on_play_time_tick=self._on_play_time_tick_callback
        )
        
        # Tray icon
        from ui.tray_icon import TrayIcon
        self._tray = TrayIcon(
            icon_path=self._icon_path,
            on_open_settings=self._open_settings,
            on_view_log=self._view_log,
            on_pause_today=self._pause_today,
            on_resume=self._resume,
            on_quit=self._quit,
            on_reset_whitelist=self._detector.reset_whitelist,
            on_toggle_chat_head=self._toggle_chat_head,
        )

        # Chat head (Overlay Bubble)
        from ui.overlay_bubble import OverlayBubble
        self._overlay_bubble = OverlayBubble(icon_path=self._icon_path)
        self._overlay_bubble.on_double_click.connect(self._open_settings)
        self._overlay_bubble.on_right_click.connect(self._show_bubble_menu)
        self._overlay_bubble.on_single_click.connect(self._show_play_time_now)
        self._overlay_bubble.show()

        # Night guard
        self._night_guard = NightGuard(
            on_whitelist_reset=self._on_whitelist_reset,
            on_toast=self._show_toast,
            on_night_lockdown=lambda exe, pid, is_soft: QMetaObject.invokeMethod(
                self, "_show_sleep_lockscreen", Qt.QueuedConnection,
                Q_ARG(str, exe), Q_ARG(int, pid), Q_ARG(bool, is_soft)
            ),
        )

        if self._show_settings_on_start:
            # We must use a timer to show it after event loop starts
            QTimer.singleShot(500, self._open_settings)
            
        self._detector.start()
        self._night_guard.start()
        self._tray.show()

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

        # Components are started in _start_services()
        logger.info("All components started (or waiting for onboarding), entering event loop")
        exit_code = self._app.exec_()

        # Cleanup
        if self._detector:
            self._detector.stop()
        if self._night_guard:
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

    def _on_play_time_tick_callback(self, mins: int):
        from core.i18n import t
        if self._overlay_bubble:
            msg = t("bubble_play_time", mins=mins)
            self._overlay_bubble.show_message(msg, 5000)

    @pyqtSlot(int)
    def _show_play_time_bubble(self, minutes: int):
        """Show the overlay bubble (runs on Qt main thread)."""
        msg = t("bubble_play_time_alert", minutes=minutes)
        logger.info(f"Showing play time bubble: {minutes} mins")
        self._overlay_bubble.show_message(msg, 15000)

    def _show_bubble_menu(self, global_pos):
        from PyQt5.QtWidgets import QMenu
        from core.i18n import t
        from core.config_manager import load_config
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu { background: #2c2c2c; color: white; border: 1px solid #444; border-radius: 6px; padding: 4px; font-family: 'Segoe UI'; font-size: 13px; }
            QMenu::item { padding: 6px 24px; border-radius: 4px; }
            QMenu::item:selected { background: #3c3c3c; }
        """)
        
        act_settings = menu.addAction(t("tray_open_settings"))
        
        # Pause / Resume logic based on game detector
        is_paused = self._detector.is_paused()
        act_pause = None
        act_resume = None
        if is_paused:
            act_resume = menu.addAction(t("tray_resume"))
        else:
            act_pause = menu.addAction(t("tray_pause_today"))
            
        act_hide = menu.addAction(t("bubble_hide"))
        menu.addSeparator()
        act_quit = menu.addAction(t("tray_quit"))
        
        action = menu.exec_(global_pos)
        
        if action == act_settings:
            self._open_settings()
        elif action == act_pause:
            self._pause_today()
        elif action == act_resume:
            self._resume()
        elif action == act_hide:
            self._overlay_bubble.hide()
        elif action == act_quit:
            self._quit()
            
    def _toggle_chat_head(self):
        if self._overlay_bubble.isHidden():
            self._overlay_bubble.show()
        else:
            self._overlay_bubble.hide()
            
    @pyqtSlot()
    def _show_play_time_now(self):
        from core.report_logger import get_daily_stats
        from core.i18n import t
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        stats = get_daily_stats()
        seconds = stats.get(today, {}).get("total_seconds", 0)
        mins = seconds // 60
        msg = t("bubble_play_time", mins=mins)
        self._overlay_bubble.show_message(msg, 5000)

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
        config = load_config()
        sound_cfg = config.get("sound", {})
        if sound_cfg.get("play_notification", True):
            sound_path = sound_cfg.get("notification_sound", "")
            if sound_path:
                try:
                    import winsound
                    winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                except Exception as e:
                    logger.error("Failed to play sound: %s", e)
                    
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
        from core.config_manager import load_config
        from core.i18n import t
        from PyQt5.QtWidgets import QMessageBox
        
        is_anti_cheat = load_config().get("anti_cheat", True)
        if is_anti_cheat:
            QMessageBox.warning(None, t("anti_cheat_title"), t("anti_cheat_pause_warning"))
            return
            
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
        from core.config_manager import load_config
        from core.i18n import t
        from PyQt5.QtWidgets import QMessageBox
        
        is_anti_cheat = load_config().get("anti_cheat", True)
        if is_anti_cheat:
            QMessageBox.warning(None, t("anti_cheat_title"), t("anti_cheat_warning"))
            return
            
        logger.info("User requested quit")
        self._detector.stop()
        self._night_guard.stop()
        self._app.quit()


# ─── Entry Point ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Mindfun — Behavioral Friction for Gaming")
    parser.add_argument("--settings", action="store_true", help="Show settings window on startup")
    parser.add_argument("--test-onboarding", action="store_true", help="Force show the onboarding window for testing")
    args = parser.parse_args()

    app = MindfunApp(show_settings=args.settings, test_onboarding=args.test_onboarding)
    sys.exit(app.run())


if __name__ == "__main__":
    main()
