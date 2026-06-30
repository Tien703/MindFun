import re

with open("ui/lockscreen.py", "r", encoding="utf-8") as f:
    content = f.read()

start_idx = content.find("    def _setup_ui(self):")
end_idx = content.find("    def resizeEvent(self, event):")

new_setup = """    def _setup_ui(self):
        \"\"\"Build the lockscreen UI layout.\"\"\"
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
        self._bubble_frame.setStyleSheet(\"\"\"
            QFrame {
                background-color: #e2d6b5;
                border: 4px solid #66461a;
                border-radius: 10px;
            }
        \"\"\")
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
        self._countdown_label.setText(f"{self._remaining}s\\n\\n{t('waiting_prompt')}")
        
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
        self._board_frame.setStyleSheet(\"\"\"
            QFrame#board_frame {
                background-color: #fce3b8;
                border: 8px solid #c98835;
                border-radius: 5px;
            }
        \"\"\")
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
        
        self._btn_prev = QPushButton("Trước")
        self._btn_prev.setObjectName("btn_prev")
        self._btn_prev.setEnabled(False)
        self._btn_prev.setCursor(Qt.PointingHandCursor)
        self._btn_prev.hide() # Initially hidden
        # TODO: Implement _handle_prev if you want to go back
        
        self._btn_next = QPushButton(t("btn_next") if t("btn_next") != "btn_next" else "Sau")
        self._btn_next.setObjectName("btn_next") 
        self._btn_next.setEnabled(not self._countdown_active)
        self._btn_next.setCursor(Qt.PointingHandCursor)
        self._btn_next.clicked.connect(self._handle_next)
        
        wooden_btn_style = \"\"\"
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
        \"\"\"
        self._btn_prev.setStyleSheet(wooden_btn_style)
        self._btn_next.setStyleSheet(wooden_btn_style)
        
        board_btn_layout.addStretch()
        board_btn_layout.addWidget(self._btn_prev)
        board_btn_layout.addWidget(self._btn_next)
        board_btn_layout.addStretch()
        
        board_layout.addLayout(board_btn_layout)
        right_pane.addWidget(self._board_frame)
        
        # Warning label
        self._warning_label = QLabel(t("unfinished_tasks_ask"))
        self._warning_label.setAlignment(Qt.AlignCenter)
        self._warning_label.setStyleSheet("color: #ed8796; font-size: 16px; font-weight: bold; font-style: italic;")
        self._warning_label.hide()
        right_pane.addWidget(self._warning_label)
        
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
        
        self._btn_quit.setStyleSheet(wooden_btn_style)
        self._btn_play.setStyleSheet(wooden_btn_style)

        n = len(self._checklist_groups)
        if n > 1 and self._current_group_index < n - 1:
            self._btn_play.hide()
        else:
            self._btn_next.hide()
            
        if self._is_sleep_lock:
            if not self._is_soft_sleep_lock:
                self._btn_play.hide()
                self._btn_next.hide()
                self._warning_label.hide()

        main_btn_layout.addStretch()
        main_btn_layout.addWidget(self._btn_quit)
        main_btn_layout.addWidget(self._btn_play)
        main_btn_layout.addStretch()
        
        right_pane.addLayout(main_btn_layout)
        
        layout.addWidget(right_frame, 6)
        
        self.size_grip = QSizeGrip(self)
        self._apply_styles()

"""

new_content = content[:start_idx] + new_setup + content[end_idx:]
with open("ui/lockscreen.py", "w", encoding="utf-8") as f:
    f.write(new_content)
