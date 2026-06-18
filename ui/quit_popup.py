"""
Quit Popup Window

A small, non-obtrusive popup that stays on top of the screen to remind the user
to manually close the game. It polls the game's PID and automatically closes itself
when the game is successfully terminated.
"""

import logging
from typing import Callable
import psutil

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt5.QtCore import Qt, QTimer

from core.config_manager import load_config
import ui.theme as theme

logger = logging.getLogger("mindfun.quit_popup")

class QuitPopup(QWidget):
    def __init__(self, game_exe: str, game_pid: int, on_closed: Callable[[str, int], None], parent=None):
        super().__init__(parent)
        self._game_exe = game_exe
        self._game_pid = game_pid
        self._on_closed = on_closed
        self._is_closing = False

        self._setup_window()
        self._setup_ui()
        
        # Timer to check if PID is still alive
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check_pid)
        self._timer.start(1000)  # Check every 1 second
        
        logger.info("QuitPopup opened for %s (PID %d)", game_exe, game_pid)

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # Position at top center
        screen = QApplication.primaryScreen()
        if screen:
            geo = screen.geometry()
            self.setFixedWidth(400)
            self.setFixedHeight(60)
            x = (geo.width() - self.width()) // 2
            y = 20  # 20px from top
            self.move(x, y)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        from core.config_manager import load_config, get_game_name
        layout.setContentsMargins(0, 0, 0, 0)
        
        pal = theme.get_settings_palette(load_config().get("dark_mode", True))
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #fe413c;
                border: 2px solid #8B0000;
                border-radius: 8px;
            }}
        """)
        
        # Add English string for consistency with new lockscreen
        friendly_name = get_game_name(self._game_exe)
        text = f"Close {friendly_name} to exit."
        lang = load_config().get("language", "vi")
        if lang == "vi":
            text = f"Vui lòng tắt {friendly_name} để hoàn tất."
            
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"""
            QLabel {{
                color: #FFFFFF;
                font-size: 16px;
                font-weight: bold;
                border: none;
            }}
        """)
        layout.addWidget(label)

    def _check_pid(self):
        """Check if the game process is still running."""
        try:
            if not psutil.pid_exists(self._game_pid):
                logger.info("Process %d no longer exists. Closing popup.", self._game_pid)
                self._finish_and_close()
        except Exception as e:
            logger.error("Error checking PID %d: %s", self._game_pid, e)
            self._finish_and_close()
            
    def _finish_and_close(self):
        if self._is_closing:
            return
        self._is_closing = True
        self._timer.stop()
        if self._on_closed:
            self._on_closed(self._game_exe, self._game_pid)
        self.close()

    def mousePressEvent(self, event):
        """Allow dragging the popup if it gets in the way."""
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()
