"""
Quit Popup Window

A small, non-obtrusive popup that stays on top of the screen to remind the user
to manually close the game. It polls the game's PID and automatically closes itself
when the game is successfully terminated.
"""

import logging
from typing import Callable

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt5.QtCore import Qt, QTimer
import ui.theme as theme

# For SetWindowPos HWND_TOPMOST
try:
    import ctypes
    _user32 = ctypes.windll.user32
    
    # Constants for window minimization
    SW_MINIMIZE = 6
    SW_RESTORE = 9
    
    EnumWindows = _user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    GetWindowThreadProcessId = _user32.GetWindowThreadProcessId
    IsWindowVisible = _user32.IsWindowVisible
    ShowWindow = _user32.ShowWindow
    
    _WIN_API = True
except (OSError, AttributeError):
    _WIN_API = False

logger = logging.getLogger("mindfun.quit_popup")

class QuitPopup(QWidget):
    def __init__(self, game_exe: str, game_pid: int, on_closed: Callable[[str, int], None], parent=None):
        super().__init__(parent)
        self._game_exe = game_exe
        self._game_pid = game_pid
        self._on_closed = on_closed
        self._is_closing = False
        self._minimize_counter = 1

        self._setup_window()
        self._setup_ui()
        
        # Timer to check if PID is still alive (runs every 1s)
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
        """Check if any game process matching _game_exe is still running."""
        try:
            import psutil
            any_alive = False
            for p in psutil.process_iter(['name', 'pid']):
                try:
                    if p.info['name'] and p.info['name'].lower() == self._game_exe.lower():
                        any_alive = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                    
            if not any_alive:
                logger.info("No processes found for %s. Closing popup.", self._game_exe)
                self._finish_and_close()
            else:
                # Minimize game every 10 seconds (0s, 10s, 20s...)
                if self._minimize_counter % 10 == 0:
                    self._minimize_game_windows()
                self._minimize_counter += 1
        except Exception as e:
            logger.error("Error checking PID %d: %s", self._game_pid, e)
            self._finish_and_close()
            
    def _get_game_hwnds(self) -> list:
        """Find all visible window handles for all processes matching game_exe."""
        hwnds = []
        if not _WIN_API:
            return hwnds
        try:
            import psutil
            target_pids = set()
            for p in psutil.process_iter(['name', 'pid']):
                try:
                    if p.info['name'] and p.info['name'].lower() == self._game_exe.lower():
                        target_pids.add(p.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                    
            def callback(hwnd, _):
                window_pid = ctypes.c_ulong()
                GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
                if window_pid.value in target_pids and IsWindowVisible(hwnd):
                    hwnds.append(hwnd)
                return True
            
            # Store cb_func reference to avoid garbage collection crash
            self._cb_func = EnumWindowsProc(callback)
            EnumWindows(self._cb_func, 0)
        except Exception as e:
            logger.error("Error enumerating windows: %s", e)
        return hwnds

    def _minimize_game_windows(self):
        """Minimize the game window to force the user to quit."""
        if not _WIN_API:
            return
        try:
            hwnds = self._get_game_hwnds()
            for hwnd in hwnds:
                ShowWindow(hwnd, SW_MINIMIZE)
        except Exception as e:
            logger.error("Error minimizing game windows: %s", e)

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
