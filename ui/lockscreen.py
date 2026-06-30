import ui.theme as theme
"""
Mindfun — LockScreen UI

Fullscreen overlay that appears when a game is detected.
Shows a countdown timer with a mindfulness checklist, then lets the user
choose to continue playing or quit.

Anti-bypass features:
- Always-on-top overlay window (Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
- HWND_TOPMOST re-assertion every 500ms via QTimer
- Buttons disabled during countdown
- Alt+F4 intercepted via nativeEvent (WM_SYSCOMMAND)
- Overlay Mode Only: Does not suspend or kill the game to bypass Anti-Cheats.
"""

import logging
from typing import Optional

# pyrefly: ignore [missing-import]
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QApplication, QCheckBox,
    QStackedWidget, QSizeGrip, QScrollArea, QFrame
)
from ui.circular_progress import CircularProgress
import winsound
# pyrefly: ignore [missing-import]
from PyQt5.QtCore import Qt, QTimer, QByteArray
# pyrefly: ignore [missing-import]
from PyQt5.QtGui import QColor, QLinearGradient, QPainter

from core.i18n import t, get_mode_duration
from core.config_manager import load_config, load_questions, save_questions
from ui.progress_character import ProgressCharacter

logger = logging.getLogger("mindfun.lockscreen")

# Windows constants for nativeEvent
WM_SYSCOMMAND = 0x0112
SC_CLOSE = 0xF060

# For SetWindowPos HWND_TOPMOST
try:
    import ctypes
    _user32 = ctypes.windll.user32
    HWND_TOPMOST = -1
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    SWP_NOACTIVATE = 0x0010
    
    # Constants for window minimization
    SW_MINIMIZE = 6
    SW_RESTORE = 9
    
    EnumWindows = _user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    GetWindowThreadProcessId = _user32.GetWindowThreadProcessId
    IsWindowVisible = _user32.IsWindowVisible
    IsIconic = _user32.IsIconic
    ShowWindow = _user32.ShowWindow
    SetForegroundWindow = _user32.SetForegroundWindow
    
    _WIN_API = True
except (OSError, AttributeError):
    _WIN_API = False


class LockScreen(QWidget):
    """
    Fullscreen lockscreen overlay with countdown timer and mindfulness question.
    """

    def __init__(
        self,
        game_exe: str,
        game_pid: int,
        launcher_exe: Optional[str] = None,
        launcher_pid: Optional[int] = None,
        on_play: Optional[callable] = None,
        on_quit: Optional[callable] = None,
        is_sleep_lock: bool = False,
        is_soft_sleep_lock: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self._game_exe = game_exe
        self._game_pid = game_pid
        self._on_play = on_play
        self._on_quit = on_quit
        self._is_sleep_lock = is_sleep_lock
        self._is_soft_sleep_lock = is_soft_sleep_lock

        # Load mode duration
        config = load_config()
        self._mode = config.get("mode", 2)
        self._total_seconds = get_mode_duration(self._mode)
        self._remaining = self._total_seconds
        self._countdown_active = True
        self._is_closing = False
        self._drag_pos = None
        self._global_elapsed_seconds = 0
        self._furthest_group_index = 0
        self._was_red = False

        # Load tasks grouped by category
        _, self._checklist_groups = self._load_questions_and_tasks(config)

            
        self._current_group_index = 0
        
        n = len(self._checklist_groups)
        if n == 0:
            self._group_times = [self._total_seconds]
        else:
            base = self._total_seconds // n
            rem = self._total_seconds % n
            self._group_times = [base] * n
            for i in range(rem):
                self._group_times[i] += 1
                
        self._remaining = self._group_times[self._current_group_index]
        self._countdown_active = (self._remaining > 0)
        
        if self._is_sleep_lock and not self._is_soft_sleep_lock:
            self._remaining = 0
            self._countdown_active = False

        # Setup window
        self._minimize_counter = 1
        self._setup_window()
        self._setup_ui()
        self._setup_timers()

        # Overlay without suspending
        logger.info("LockScreen: overlying %s (PID %d), _WIN_API: %s", game_exe, game_pid, _WIN_API)

    def _load_questions_and_tasks(self, config: dict) -> tuple[str, list]:
        """Load all tasks from enabled checklist groups (no random questions)."""
        questions_data = load_questions()
        
        groups = questions_data.get("task_groups", [])
            
        all_tasks = []
        
        for group in groups:
            if not group.get("enabled", True):
                continue
            
            items = group.get("items", [])
            if not items:
                continue
                
            if group.get("is_checklist", False):
                all_tasks.append({
                    "id": group["id"],
                    "name": group.get("name", "Tasks"),
                    "type": "checklist",
                    "items": [(group["id"], item["id"], item["text"], item.get("done", False)) for item in items]
                })
            else:
                import random
                question = random.choice(items).get("text", "")
                all_tasks.append({
                    "id": group["id"],
                    "name": group.get("name", "Question"),
                    "type": "question",
                    "question": question
                })
                    
        return "", all_tasks

    def _setup_window(self):
        """Configure window flags and properties."""
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFocusPolicy(Qt.StrongFocus)

        WIDTH, HEIGHT = 900, 550
        screen = QApplication.primaryScreen()
        if screen:
            screen_geo = screen.geometry()
            x = (screen_geo.width() - WIDTH) // 2
            y = (screen_geo.height() - HEIGHT) // 2
            self.setGeometry(x, y, WIDTH, HEIGHT) 
            
        try:
            from BlurWindow.blurWindow import blur
            blur(self.winId(), Acrylic=True)
        except Exception as e:
            logger.error("Failed to apply blur: %s", e)
            
        self.show()

    def _setup_ui(self):
        """Build the lockscreen UI layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── LEFT FRAME (Beige background) ──
        left_frame = QFrame()
        left_frame.setStyleSheet("background-color: #c5cec0;")
        left_pane = QVBoxLayout(left_frame)
        left_pane.setContentsMargins(40, 40, 40, 40)
        left_pane.setSpacing(20)

        # Game name label
        from core.config_manager import get_game_name
        friendly_name = get_game_name(self._game_exe)
        
        if self._is_sleep_lock:
            if self._is_soft_sleep_lock:
                self._game_label = QLabel(t("soft_sleep_lock_warning", game=friendly_name))
            else:
                self._game_label = QLabel(t("sleep_lock_warning", game=friendly_name))
            self._game_label.setStyleSheet("color: #ed8796; font-size: 24px; font-weight: bold; background: transparent; border: none;")
        else:
            self._game_label = QLabel(t("game_paused", game=friendly_name))
            self._game_label.setStyleSheet("color: #000000; font-size: 20px; font-weight: bold; background: transparent; border: none;")
            
        self._game_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self._game_label.setObjectName("game_label")
        left_pane.addWidget(self._game_label)
        
        left_pane.addStretch()
        
        # Countdown label inside Speech Bubble
        self._bubble_frame = QFrame()
        self._bubble_frame.setStyleSheet("""
            QFrame {
                background-color: #e2d6b5;
                border: 4px solid #66461a;
                border-radius: 10px;
            }
        """)
        bubble_layout = QVBoxLayout(self._bubble_frame)
        bubble_layout.setContentsMargins(15, 15, 15, 15)
        
        self._countdown_label = QLabel()
        self._countdown_label.setAlignment(Qt.AlignCenter)
        self._countdown_label.setStyleSheet("color: #000000; font-size: 16px; font-weight: bold; border: none; background: transparent;")
        bubble_layout.addWidget(self._countdown_label)
        
        # Progress character
        self._progress = ProgressCharacter()
        self._progress.setMaxValue(self._total_seconds)
        self._progress.setValue(self._total_seconds - self._global_elapsed_seconds)
        
        
        if self._is_sleep_lock and not self._is_soft_sleep_lock:
            self._progress.hide()
            self._bubble_frame.hide()
            
        # Center the bubble and character
        char_layout = QVBoxLayout()
        char_layout.setAlignment(Qt.AlignCenter)
        char_layout.addWidget(self._bubble_frame, 0, Qt.AlignCenter)
        char_layout.addSpacing(10)
        char_layout.addWidget(self._progress, 0, Qt.AlignCenter)
        
        left_pane.addLayout(char_layout)
        left_pane.addStretch()
        layout.addWidget(left_frame, 4)

        # ── RIGHT FRAME (Dark Green background) ──
        right_frame = QFrame()
        right_frame.setStyleSheet("background-color: #436762;")
        right_pane = QVBoxLayout(right_frame)
        right_pane.setContentsMargins(40, 40, 40, 40)
        right_pane.setSpacing(20)
        
        # Checklist/Board Frame
        self._board_frame = QFrame()
        self._board_frame.setStyleSheet("""
            QFrame#board_frame {
                background-color: #fce3b8;
                border: 8px solid #c98835;
                border-radius: 5px;
            }
        """)
        self._board_frame.setObjectName("board_frame")
        board_layout = QVBoxLayout(self._board_frame)
        board_layout.setContentsMargins(20, 20, 20, 20)
        
        if self._checklist_groups:
            self._stacked_checklists = QStackedWidget()
            
            for group_data in self._checklist_groups:
                page = QWidget()
                page_layout = QVBoxLayout(page)
                page_layout.setSpacing(16)
                page_layout.setContentsMargins(0, 0, 0, 0)
                
                title = QLabel(f"[{group_data['name']}]")
                title.setStyleSheet("color: #000000; font-size: 20px; font-weight: bold; margin-bottom: 8px; background: transparent; border: none;")
                page_layout.addWidget(title)
                
                if group_data["type"] == "checklist":
                    for group_id, item_id, text, is_done in group_data["items"]:
                        item_container = QWidget()
                        item_layout = QHBoxLayout(item_container)
                        item_layout.setContentsMargins(0, 0, 0, 0)
                        item_layout.setSpacing(12)
                        
                        cb = QCheckBox()
                        cb.setObjectName("task_checkbox")
                        cb.setChecked(is_done)
                        
                        lbl = QLabel(text)
                        lbl.setWordWrap(True)
                        lbl.setCursor(Qt.PointingHandCursor)
                        
                        if is_done:
                            f = lbl.font()
                            f.setStrikeOut(True)
                            lbl.setFont(f)
                            lbl.setStyleSheet("color: #888888; font-size: 22px; background: transparent; border: none;")
                        else:
                            lbl.setStyleSheet("color: #000000; font-size: 22px; background: transparent; border: none;")
                            
                        lbl.mousePressEvent = lambda event, cb_ref=cb, g_id=group_id, i_id=item_id, lbl_ref=lbl: cb_ref.setChecked(not cb_ref.isChecked()) or self._on_task_checked(g_id, i_id, cb_ref, lbl_ref)
                        cb.clicked.connect(lambda checked, g_id=group_id, i_id=item_id, cb_ref=cb, lbl_ref=lbl: self._on_task_checked(g_id, i_id, cb_ref, lbl_ref))
                        
                        item_layout.addWidget(cb)
                        item_layout.addWidget(lbl, 1)
                        
                        page_layout.addWidget(item_container)
                else:
                    lbl = QLabel(f'"{group_data["question"]}"')
                    lbl.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    lbl.setWordWrap(True)
                    lbl.setStyleSheet("color: #000000; font-size: 20px; background: transparent; border: none;")
                    page_layout.addWidget(lbl)
                    
                page_layout.addStretch()
                self._stacked_checklists.addWidget(page)
                
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setFrameShape(QFrame.NoFrame)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll_area.setStyleSheet("background: transparent; border: none;")
            scroll_area.setWidget(self._stacked_checklists)
            
            if self._is_sleep_lock and not self._is_soft_sleep_lock:
                scroll_area.hide()
            
            board_layout.addWidget(scroll_area)
        else:
            lbl = QLabel(t("waiting_prompt"))
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #000000; font-size: 20px; background: transparent; border: none;")
            if self._is_sleep_lock and not self._is_soft_sleep_lock:
                lbl.hide()
            board_layout.addWidget(lbl)
            
        # Board Buttons (Prev/Next)
        board_btn_layout = QHBoxLayout()
        board_btn_layout.setSpacing(20)
        
        self._btn_prev = QPushButton(t("btn_prev"))
        self._btn_prev.setObjectName("btn_prev")
        self._btn_prev.setEnabled(False)
        self._btn_prev.setCursor(Qt.PointingHandCursor)
        self._btn_prev.hide()
        self._btn_prev.clicked.connect(self._handle_prev)
        # TODO: Implement _handle_prev if you want to go back
        
        self._btn_next = QPushButton(t("btn_next") if t("btn_next") != "btn_next" else "Sau")
        self._btn_next.setObjectName("btn_next") 
        self._btn_next.setEnabled(not self._countdown_active)
        self._btn_next.setCursor(Qt.PointingHandCursor)
        self._btn_next.clicked.connect(self._handle_next)
        
        self._wooden_btn_style = """
            QPushButton {
                background-color: #e2d6b5;
                border: 2px solid #fce3b8;
                border-bottom: 4px solid #c98835;
                border-right: 4px solid #c98835;
                color: #000000;
                padding: 10px;
                font-weight: bold;
                border-radius: 0px;
            }
            QPushButton:pressed {
                border: 2px solid #c98835;
                border-bottom: 2px solid #fce3b8;
                border-right: 2px solid #fce3b8;
            }
            QPushButton:disabled {
                background-color: #d9d9d9;
                color: #888888;
                border: 2px solid #eeeeee;
                border-bottom: 4px solid #aaaaaa;
                border-right: 4px solid #aaaaaa;
            }
        """
        self._btn_prev.setStyleSheet(self._wooden_btn_style)
        self._btn_next.setStyleSheet(self._wooden_btn_style)
        
        board_btn_layout.addStretch()
        board_btn_layout.addWidget(self._btn_prev)
        board_btn_layout.addWidget(self._btn_next)
        board_btn_layout.addStretch()
        
        board_layout.addLayout(board_btn_layout)
        right_pane.addWidget(self._board_frame)
        
        
        
        # Main Action Buttons (Play/Quit)
        main_btn_layout = QHBoxLayout()
        main_btn_layout.setSpacing(30)
        
        self._btn_quit = QPushButton(t("btn_quit"))
        self._btn_quit.setObjectName("btn_quit")
        self._btn_quit.setEnabled(True)
        self._btn_quit.setCursor(Qt.PointingHandCursor)
        self._btn_quit.clicked.connect(self._handle_quit)
        self._btn_quit.setMinimumHeight(50)
        
        self._btn_play = QPushButton(t("btn_play"))
        self._btn_play.setObjectName("btn_play")
        self._btn_play.setEnabled(not self._countdown_active)
        self._btn_play.setCursor(Qt.PointingHandCursor)
        self._btn_play.clicked.connect(self._handle_play)
        self._btn_play.setMinimumHeight(50)
        
        self._btn_quit.setStyleSheet(self._wooden_btn_style)
        self._btn_play.setStyleSheet(self._wooden_btn_style)

        n = len(self._checklist_groups)
        if n > 1 and self._current_group_index < n - 1:
            self._btn_play.hide()
        else:
            self._btn_next.hide()
            
        if self._is_sleep_lock:
            if not self._is_soft_sleep_lock:
                self._btn_play.hide()
                self._btn_next.hide()
                

        main_btn_layout.addStretch()
        main_btn_layout.addWidget(self._btn_quit)
        main_btn_layout.addWidget(self._btn_play)
        main_btn_layout.addStretch()
        
        right_pane.addLayout(main_btn_layout)
        
        layout.addWidget(right_frame, 6)
        
        self.size_grip = QSizeGrip(self)
        self._update_character_state()
        self._apply_styles()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'size_grip'):
            self.size_grip.move(self.width() - self.size_grip.width() - 5, self.height() - self.size_grip.height() - 5)
            self.size_grip.raise_()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = None
            event.accept()

    def _apply_styles(self):
        """Apply dark theme styling."""
        from core.config_manager import load_config
        import ui.theme as theme
        is_dark = load_config().get("dark_mode", True)
        self.setStyleSheet(theme.get_lockscreen_style(is_dark))

    def _on_task_checked(self, group_id: str, item_id: str, checkbox: QCheckBox, label: QLabel = None):
        """Handle task checkbox click. Save 'done' state to config."""
        is_done = checkbox.isChecked()
        
        target = label if label else checkbox
        is_dark = load_config().get("dark_mode", True)
        desc_col = theme.get_settings_palette(is_dark)["desc_color"]
        text_col = theme.get_settings_palette(is_dark)["text_color"]
        
        if is_done:
            f = target.font()
            f.setStrikeOut(True)
            target.setFont(f)
            target.setStyleSheet(f"color: {desc_col}; font-size: 22px;")
            
            # Play sound
            config = load_config()
            sound_cfg = config.get("sound", {})
            if sound_cfg.get("play_checklist", True):
                sound_path = sound_cfg.get("checklist_sound", "")
                if sound_path:
                    try:
                        winsound.PlaySound(sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                    except Exception as e:
                        logger.error(f"Failed to play sound: {e}")
        else:
            f = target.font()
            f.setStrikeOut(False)
            target.setFont(f)
            target.setStyleSheet(f"color: {text_col}; font-size: 22px;")

        # Update JSON
        questions_data = load_questions()
        groups = questions_data.get("task_groups", [])
        for g in groups:
            if g.get("id") == group_id:
                for item in g.get("items", []):
                    if item.get("id") == item_id:
                        item["done"] = is_done
                        save_questions(questions_data)
                        break
                        
        # Update internal state and check strict block
        for group in self._checklist_groups:
            if group["id"] == group_id and group["type"] == "checklist":
                for i, (g_id, i_id, txt, _) in enumerate(group["items"]):
                    if i_id == item_id:
                        group["items"][i] = (g_id, i_id, txt, is_done)
                        break
                        
        self._update_play_button()
        self._update_character_state()

    def _has_unfinished_tasks(self) -> bool:
        """Check if any checklist items are not done."""
        for group in self._checklist_groups:
            if group["type"] == "checklist":
                for _, _, _, is_done in group["items"]:
                    if not is_done:
                        return True
        return False

    def _check_strict_block(self) -> bool:
        """Check if playing should be blocked based on mode 4/5 and unfinished tasks."""
        is_strict = False
        if self._mode == 4:
            is_strict = True
        elif self._mode == 5:
            config = load_config()
            is_strict = config.get("custom_mode", {}).get("task_lock") == "lock"
            
        if not is_strict:
            return False
            
        for group in self._checklist_groups:
            if group["type"] == "checklist":
                for _, _, _, is_done in group["items"]:
                    if not is_done:
                        return True
        return False
        
    def _update_play_button(self):
        """Update play button state based on strict block."""
        is_blocked = self._check_strict_block()
        has_unfinished = self._has_unfinished_tasks()
        
        n = len(self._checklist_groups)
        on_last_screen = (self._current_group_index == n - 1) if n > 0 else True
        can_play_time = on_last_screen and not self._countdown_active
        
        
            
        if is_blocked:
            self._btn_play.setEnabled(False)
            self._btn_play.setText(t("btn_finish_tasks"))
            self._btn_play.setStyleSheet("""
                QPushButton {
                    color: #ed8796; 
                    border: 2px solid #ed8796; 
                    background-color: transparent;
                    border-radius: 12px;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 16px;
                }
            """)
        else:
            self._btn_play.setText(t("btn_play"))
            self._btn_play.setStyleSheet(self._wooden_btn_style) # Revert to wooden style
            
            if can_play_time:
                self._btn_play.setEnabled(True)
            else:
                self._btn_play.setEnabled(False)

    def _setup_timers(self):
        """Set up QTimers for countdown and window topmost enforcement."""
        # Countdown timer: fires every 1 second
        self._countdown_timer = QTimer(self)
        self._countdown_timer.timeout.connect(self._tick)
        self._countdown_timer.start(1000)

        # Topmost enforcement timer: fires every 500ms
        self._topmost_timer = QTimer(self)
        self._topmost_timer.timeout.connect(self._enforce_topmost)
        self._topmost_timer.start(500)

        # Process monitor timer: fires every 2000ms
        self._process_timer = QTimer(self)
        self._process_timer.timeout.connect(self._check_process_alive)
        self._process_timer.start(2000)

    def _check_process_alive(self):
        """Check if any game process matching _game_exe is still running; close if it died."""
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
                logger.info("No processes found for %s. Closing LockScreen.", self._game_exe)
                self._countdown_timer.stop()
                self._topmost_timer.stop()
                self._process_timer.stop()
                self._is_closing = True
                
                # Let the detector know this PID is gone, just in case
                # Let the detector know this PID is gone, just in case
                self.close()
        except Exception as e:
            logger.error("Error checking process alive: %s", e)

    def _update_character_state(self):
        total_left = max(0, self._total_seconds - self._global_elapsed_seconds)
        
        is_red = False
        bubble_message = t("waiting_prompt")
        
        on_last_screen = (self._current_group_index == len(self._checklist_groups) - 1) if self._checklist_groups else True
        
        if self._is_sleep_lock:
            is_red = True
            if self._is_soft_sleep_lock:
                bubble_message = t("soft_sleep_lock_warning")
            else:
                bubble_message = t("sleep_lock_warning")
        else:
            if on_last_screen and self._has_unfinished_tasks():
                is_red = True
                if self._check_strict_block():
                    bubble_message = t("strict_task_block")
                else:
                    bubble_message = t("soft_task_block")
            else:
                bubble_message = t("waiting_prompt")
                
        # Update character color
        self._progress.set_red_mode(is_red)
        
        # Play sound on color change to red
        if is_red and not self._was_red:
            try:
                import winsound
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
            except:
                pass
        self._was_red = is_red
        
        # Update bubble text
        if total_left > 0:
            time_text = t("time_meditation", total_left=total_left)
        else:
            time_text = ""
            
        self._countdown_label.setText(f"{time_text}{bubble_message}")

    def _tick(self):
        """Update countdown and check state."""
        self.raise_()
        self.activateWindow()

        if self._countdown_active:
            self._remaining -= 1
            self._global_elapsed_seconds += 1
            
            total_left = max(0, self._total_seconds - self._global_elapsed_seconds)

            if self._remaining <= 0:
                self._remaining = 0
                self._countdown_active = False
                self._btn_quit.setEnabled(True)
                
                n = len(self._checklist_groups)
                if n > 1 and self._current_group_index < n - 1:
                    self._btn_next.setEnabled(True)
                    self._btn_next.setText(t("btn_next"))
                else:
                    self._update_play_button()
                    
                self._update_character_state()
                import logging
                logging.getLogger(__name__).info("Countdown finished for current group — buttons enabled")
            else:
                self._update_character_state()
                
                # Update button text with remaining group time
                n = len(self._checklist_groups)
                if n > 1 and self._current_group_index < n - 1:
                    btn_text = t("btn_next")
                    self._btn_next.setText(f"{btn_text} ({self._remaining}s)")
                else:
                    self._btn_play.setText(f"{t('btn_play')} ({self._remaining}s)")
            
            self._progress.setValue(self._total_seconds - self._global_elapsed_seconds)

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
        """Minimize the game window during countdown to prevent fullscreen bypass."""
        if not _WIN_API:
            return
        try:
            hwnds = self._get_game_hwnds()
            for hwnd in hwnds:
                ShowWindow(hwnd, SW_MINIMIZE)
        except Exception as e:
            logger.error("Error minimizing game windows: %s", e)

    def _restore_game_windows(self):
        """Restore the game window and focus it."""
        if not _WIN_API:
            return
        try:
            hwnds = self._get_game_hwnds()
            for hwnd in hwnds:
                ShowWindow(hwnd, SW_RESTORE)
                SetForegroundWindow(hwnd)
        except Exception as e:
            logger.error("Error restoring game windows: %s", e)

    def _enforce_topmost(self):
        """Re-assert HWND_TOPMOST position to prevent Alt+Tab escaping."""
        if _WIN_API:
            hwnd = int(self.winId())
            _user32.SetWindowPos(
                hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE,
            )
            
            # Minimize game window continuously to prevent fullscreen bypass
            self._minimize_game_windows()

    def _handle_prev(self):
        """Go to the previous group."""
        if self._current_group_index > 0:
            self._current_group_index -= 1
            if self._checklist_groups:
                self._stacked_checklists.setCurrentIndex(self._current_group_index)
            
            if self._current_group_index == 0:
                self._btn_prev.hide()
                
            self._btn_next.show()
            self._btn_next.setEnabled(True)
            self._btn_next.setText(t("btn_next"))
            
            self._btn_play.hide()
            self._update_play_button()

    def _handle_next(self):
        """Go to the next group."""
        self._current_group_index += 1
        is_first_time = (self._current_group_index > self._furthest_group_index)
        self._furthest_group_index = max(self._furthest_group_index, self._current_group_index)
        n = len(self._checklist_groups)
        
        # Update UI
        if self._checklist_groups:
            self._stacked_checklists.setCurrentIndex(self._current_group_index)
            
        self._btn_prev.show()
        self._btn_prev.setEnabled(True)
        
        if is_first_time:
            self._remaining = self._group_times[self._current_group_index]
            self._countdown_active = (self._remaining > 0)
            
        self._progress.setValue(self._total_seconds - self._global_elapsed_seconds)
        
        self._btn_quit.setEnabled(True)
        self._btn_next.setEnabled(not self._countdown_active)
        self._btn_play.setEnabled(not self._countdown_active)
        
        if self._current_group_index == n - 1:
            self._btn_next.hide()
            self._btn_play.show()
            self._update_play_button()
        else:
            self._btn_next.setText(t("btn_next"))
            
        # Update bubble text
        total_left = max(0, self._total_seconds - self._global_elapsed_seconds)
        self._update_character_state()

    def _handle_play(self):
        """User chose 'I still want to play' — resume game and close."""
        logger.info("User chose PLAY for %s", self._game_exe)
        self._countdown_timer.stop()
        self._topmost_timer.stop()

        # Restore the game window so the user can play
        self._restore_game_windows()

        if self._on_play:
            self._on_play(self._game_exe, self._game_pid)

        self._is_closing = True
        self.close()

    def _handle_quit(self):
        """User chose 'Quit & do something else' — kill game and close."""
        logger.info("User chose QUIT for %s", self._game_exe)
        self._countdown_timer.stop()
        self._topmost_timer.stop()

        # Restore the game window so they can exit it
        self._restore_game_windows()

        if self._on_quit:
            self._on_quit(self._game_exe, self._game_pid)

        self._is_closing = True
        self.close()

    # ─── Anti-bypass overrides ───────────────────────────────────────

    def closeEvent(self, event):
        """
        Override close event: closing the window = killing the game.
        This prevents Alt+F4 bypass — the user can't escape without a choice.
        """
        if self._is_closing:
            event.accept()
            return

        if self._countdown_active:
            # During countdown, block closing entirely
            event.ignore()
            return

        # After countdown, closing = quitting the game
        self._handle_quit()
        event.accept()

    def keyPressEvent(self, event):
        """Block keyboard shortcuts during countdown."""
        if self._countdown_active:
            event.ignore()
            return
        super().keyPressEvent(event)

    def nativeEvent(self, event_type, message):
        """
        Intercept Windows native events to block Alt+F4 (WM_SYSCOMMAND SC_CLOSE).
        """
        try:
            if event_type == QByteArray(b"windows_generic_MSG"):
                import ctypes.wintypes
                msg = ctypes.wintypes.MSG.from_address(int(message))
                if msg.message == WM_SYSCOMMAND and (msg.wParam & 0xFFF0) == SC_CLOSE:
                    if self._countdown_active:
                        return True, 0  # Block during countdown
                    else:
                        self._handle_quit()
                        return True, 0
        except Exception:
            pass
        return super().nativeEvent(event_type, message)

    def paintEvent(self, event):
        """Custom paint for the background overlay."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        from core.config_manager import load_config
        is_dark = load_config().get("dark_mode", True)
        
        if is_dark:
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0.0, QColor(20, 20, 20, 240))  # Semi-transparent dark
            gradient.setColorAt(1.0, QColor(10, 10, 10, 240))
        else:
            gradient = QLinearGradient(0, 0, self.width(), self.height())
            gradient.setColorAt(0.0, QColor(240, 240, 240, 240))  # Semi-transparent light
            gradient.setColorAt(1.0, QColor(220, 220, 220, 240))
            
        painter.setBrush(gradient)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 16, 16)
        super().paintEvent(event)
        
