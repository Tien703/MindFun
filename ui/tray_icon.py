"""
Mindfun — System Tray Icon

Uses PyQt5's QSystemTrayIcon to provide a system tray presence with
status info, quick settings access, and pause/resume controls.
"""

import logging
from typing import Optional, Callable

from PyQt5.QtWidgets import (
    QSystemTrayIcon, QMenu, QAction, QMessageBox,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication

from core.i18n import t, get_mode_name
from core.config_manager import load_config

logger = logging.getLogger("mindfun.tray_icon")


class TrayIcon(QSystemTrayIcon):
    """
    System tray icon with context menu for Mindfun.
    """

    def __init__(
        self,
        icon_path: str,
        on_open_settings: Optional[Callable] = None,
        on_view_log: Optional[Callable] = None,
        on_pause_today: Optional[Callable] = None,
        on_resume: Optional[Callable] = None,
        on_quit: Optional[Callable] = None,
        on_reset_whitelist: Optional[Callable] = None,
        parent=None,
    ):
        icon = QIcon(icon_path) if icon_path else QIcon()
        super().__init__(icon, parent)

        self._on_open_settings = on_open_settings
        self._on_view_log = on_view_log
        self._on_pause_today = on_pause_today
        self._on_resume = on_resume
        self._on_quit = on_quit
        self._on_reset_whitelist = on_reset_whitelist
        self._is_paused = False

        self.setToolTip(t("tray_tooltip"))
        self._build_menu()

        # Double-click opens settings
        self.activated.connect(self._on_activated)

    def _build_menu(self):
        """Build the right-click context menu."""
        menu = QMenu()
        menu.setStyleSheet(self._menu_style())

        config = load_config()
        mode = config.get("mode", 2)

        # ── Header section ──
        title_action = QAction(t("tray_title"), menu)
        title_action.setEnabled(False)
        menu.addAction(title_action)

        if self._is_paused:
            status_action = QAction(t("tray_status_paused"), menu)
        else:
            status_action = QAction(t("tray_status_active"), menu)
        status_action.setEnabled(False)
        menu.addAction(status_action)

        mode_action = QAction(t("tray_current_mode", mode=get_mode_name(mode)), menu)
        mode_action.setEnabled(False)
        menu.addAction(mode_action)

        menu.addSeparator()

        # ── Actions ──
        settings_action = QAction(t("tray_open_settings"), menu)
        settings_action.triggered.connect(self._open_settings)
        menu.addAction(settings_action)

        log_action = QAction(t("tray_view_log"), menu)
        log_action.triggered.connect(self._view_log)
        menu.addAction(log_action)

        menu.addSeparator()

        reset_action = QAction(t("tray_reset_whitelist"), menu)
        reset_action.triggered.connect(self._on_reset_whitelist)
        menu.addAction(reset_action)

        menu.addSeparator()


        is_anti_cheat = config.get("anti_cheat", True)

        # ── Pause/Resume ──
        if self._is_paused:
            resume_action = QAction(t("tray_resume"), menu)
            resume_action.triggered.connect(self._resume)
            menu.addAction(resume_action)
        else:
            pause_action = QAction(t("tray_pause_today"), menu)
            pause_action.triggered.connect(self._pause_today)
            if is_anti_cheat:
                pause_action.setEnabled(False)
            menu.addAction(pause_action)

        menu.addSeparator()

        # ── About & Quit ──
        about_action = QAction(t("tray_about"), menu)
        about_action.triggered.connect(self._show_about)
        menu.addAction(about_action)

        quit_action = QAction(t("tray_quit"), menu)
        quit_action.triggered.connect(self._quit)
        if is_anti_cheat:
            quit_action.setEnabled(False)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

    def _menu_style(self) -> str:
        """Dark theme style for the tray context menu."""
        from core.config_manager import load_config
        import ui.theme as theme
        is_dark = load_config().get("dark_mode", True)
        return theme.get_tray_style(is_dark)

    def refresh_menu(self):
        """Rebuild the menu to reflect current state."""
        self._build_menu()

    def set_paused(self, paused: bool):
        """Update the paused state and refresh menu."""
        self._is_paused = paused
        self.refresh_menu()

    def show_toast(self, title: str, message: str):
        """Show a system tray notification (balloon/toast)."""
        self.showMessage(title, message, QSystemTrayIcon.Information, 10000)

    # ─── Callbacks ───────────────────────────────────────────────────

    def _on_activated(self, reason):
        """Handle tray icon activation (double-click opens settings)."""
        if reason == QSystemTrayIcon.DoubleClick:
            self._open_settings()

    def _open_settings(self):
        if self._on_open_settings:
            self._on_open_settings()

    def _view_log(self):
        if self._on_view_log:
            self._on_view_log()

    def _pause_today(self):
        """Show confirmation dialog, then pause if confirmed."""
        reply = QMessageBox.question(
            None,
            t("confirm_title"),
            t("confirm_pause"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._is_paused = True
            self.refresh_menu()
            if self._on_pause_today:
                self._on_pause_today()

    def _resume(self):
        self._is_paused = False
        self.refresh_menu()
        if self._on_resume:
            self._on_resume()



    def _show_about(self):
        """Show the About dialog."""
        QMessageBox.information(
            None,
            t("about_title"),
            t("about_text"),
        )

    def _quit(self):
        """Quit the application (tray companion only, not the watchdog)."""
        if self._on_quit:
            self._on_quit()
        QCoreApplication.quit()
