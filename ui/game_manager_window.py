"""
Mindfun — Game Manager Window

A separate window to manage the list of tracked games (presets and customs).
Includes a search bar to easily find and toggle tracking for specific games.
"""

import logging
from typing import Callable, Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox,
    QLineEdit, QPushButton, QMessageBox, QScrollArea, QWidget, QLabel,
    QShortcut, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence, QColor

from core.config_manager import load_config, save_config, load_game_presets
from core.i18n import t

logger = logging.getLogger("mindfun.game_manager")


class GameManagerWindow(QDialog):
    def __init__(self, on_config_changed: Optional[Callable[[], None]] = None, parent=None):
        super().__init__(parent)
        self._on_config_changed = on_config_changed
        self.setWindowTitle(t("title_game_manager"))
        self.setMinimumSize(500, 650)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)

        self._fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        self._fullscreen_shortcut.activated.connect(self._toggle_fullscreen)

        self._build_ui()

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        config = load_config()
        game_list_lower = {g.lower() for g in config.get("game_list", [])}
        presets = load_game_presets().get("presets", [])
        preset_exes = {p["exe"].lower() for p in presets}

        # Migrate old custom games from game_list into config["custom_games"]
        custom_games = config.get("custom_games", [])
        custom_exes = {c["exe"].lower() for c in custom_games}
        for g in config.get("game_list", []):
            g_lower = g.lower()
            if g_lower not in preset_exes and g_lower not in custom_exes:
                custom_games.append({"name": g, "exe": g})
                custom_exes.add(g_lower)
        config["custom_games"] = custom_games

        # Search Bar
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(t("placeholder_search_game"))
        self._search_input.textChanged.connect(self._on_search_changed)
        layout.addWidget(self._search_input)

        # Preset games with checkboxes (Scrollable)
        group_preset = QGroupBox(t("group_preset_games"))
        preset_layout = QVBoxLayout(group_preset)
        
        # Add Select All / Deselect All buttons
        btn_layout = QHBoxLayout()
        btn_select_all = QPushButton("Chọn tất cả")
        btn_select_all.clicked.connect(self._select_all_presets)
        btn_deselect_all = QPushButton("Bỏ chọn tất cả")
        btn_deselect_all.clicked.connect(self._deselect_all_presets)
        btn_layout.addWidget(btn_select_all)
        btn_layout.addWidget(btn_deselect_all)
        preset_layout.addLayout(btn_layout)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self._preset_scroll_layout = QVBoxLayout(scroll_content)
        
        self._preset_checks: list[tuple[QCheckBox, str, QWidget]] = []

        for preset in presets:
            cb = QCheckBox(f'{preset["name"]}  ({preset["exe"]})')
            cb.setChecked(preset["exe"].lower() in game_list_lower)
            self._preset_checks.append((cb, preset["exe"], cb))
            self._preset_scroll_layout.addWidget(cb)

        self._preset_scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        preset_layout.addWidget(scroll)
        layout.addWidget(group_preset, stretch=2)

        # Custom games
        group_custom = QGroupBox(t("group_custom_games"))
        self._custom_layout = QVBoxLayout(group_custom)

        # Add custom game inputs
        add_layout = QHBoxLayout()
        self._custom_name_input = QLineEdit()
        self._custom_name_input.setPlaceholderText(t("placeholder_custom_name"))
        
        self._custom_exe_input = QLineEdit()
        self._custom_exe_input.setPlaceholderText(t("placeholder_custom_exe"))
        
        btn_add = QPushButton(t("btn_add"))
        btn_add.clicked.connect(self._add_custom_game)
        
        add_layout.addWidget(self._custom_name_input)
        add_layout.addWidget(self._custom_exe_input)
        add_layout.addWidget(btn_add)
        self._custom_layout.addLayout(add_layout)

        # List of custom games (checkboxes)
        self._custom_scroll = QScrollArea()
        self._custom_scroll.setWidgetResizable(True)
        self._custom_scroll_content = QWidget()
        self._custom_scroll_layout = QVBoxLayout(self._custom_scroll_content)
        
        self._custom_checks: list[tuple[QCheckBox, str, str, QWidget]] = [] # cb, name, exe, container
        
        for cgame in custom_games:
            self._create_custom_game_row(cgame["name"], cgame["exe"], cgame["exe"].lower() in game_list_lower)

        self._custom_scroll_layout.addStretch()
        self._custom_scroll.setWidget(self._custom_scroll_content)
        self._custom_layout.addWidget(self._custom_scroll)

        layout.addWidget(group_custom, stretch=1)

        # Save button
        btn_save = QPushButton(t("btn_save_list"))
        btn_save.setObjectName("btn_save_primary")
        btn_save.setMinimumHeight(40)
        btn_save.clicked.connect(self._save_game_list)
        layout.addWidget(btn_save)

    def _create_custom_game_row(self, name: str, exe: str, checked: bool):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        
        cb = QCheckBox(f'{name}  ({exe})')
        cb.setChecked(checked)
        row_layout.addWidget(cb)
        
        btn_del = QPushButton(t("btn_delete"))
        btn_del.setObjectName("btn_danger")
        btn_del.setFixedWidth(60)
        btn_del.clicked.connect(lambda _, w=row_widget, c=cb: self._delete_custom_game(w, c))
        row_layout.addWidget(btn_del)
        
        self._custom_scroll_layout.insertWidget(self._custom_scroll_layout.count() - 1, row_widget)
        self._custom_checks.append((cb, name, exe, row_widget))

    def _on_search_changed(self, text: str):
        search_text = text.lower()
        
        # Filter presets
        for cb, _, container in self._preset_checks:
            if search_text in cb.text().lower():
                container.setVisible(True)
            else:
                container.setVisible(False)
                
        # Filter customs
        for cb, _, _, container in self._custom_checks:
            if search_text in cb.text().lower():
                container.setVisible(True)
            else:
                container.setVisible(False)

    def _add_custom_game(self):
        """Add a custom game to the list."""
        name = self._custom_name_input.text().strip()
        exe = self._custom_exe_input.text().strip()
        
        if not exe:
            return
            
        if not name:
            name = exe
            
        if not exe.lower().endswith(".exe"):
            exe += ".exe"
            
        # Check if already exists in custom games to prevent duplicates
        for _, _, existing_exe, _ in self._custom_checks:
            if existing_exe.lower() == exe.lower():
                QMessageBox.warning(self, t("title_game_manager"), "Game này đã có trong danh sách Custom Games!")
                return
                
        self._create_custom_game_row(name, exe, True)
        
        self._custom_name_input.clear()
        self._custom_exe_input.clear()
        self._on_search_changed(self._search_input.text())

    def _select_all_presets(self):
        """Check all visible preset checkboxes."""
        for cb, _, container in self._preset_checks:
            if container.isVisible():
                cb.setChecked(True)

    def _deselect_all_presets(self):
        """Uncheck all visible preset checkboxes."""
        for cb, _, container in self._preset_checks:
            if container.isVisible():
                cb.setChecked(False)

    def _delete_custom_game(self, row_widget: QWidget, cb: QCheckBox):
        """Delete the selected custom game."""
        # Remove from UI
        row_widget.setParent(None)
        row_widget.deleteLater()
        
        # Remove from tracking list
        self._custom_checks = [c for c in self._custom_checks if c[0] != cb]

    def _save_game_list(self):
        """Save the combined preset + custom game list to config."""
        config = load_config()
        game_list = []
        custom_games_to_save = []

        # Save checked presets
        for cb, exe, _ in self._preset_checks:
            if cb.isChecked():
                game_list.append(exe)

        # Save custom games definitions and active ones
        for cb, name, exe, _ in self._custom_checks:
            custom_games_to_save.append({"name": name, "exe": exe})
            if cb.isChecked():
                game_list.append(exe)

        config["game_list"] = game_list
        config["custom_games"] = custom_games_to_save
        save_config(config)
        logger.info("Game list saved: %s, custom definitions: %s", game_list, len(custom_games_to_save))
        
        if self._on_config_changed:
            self._on_config_changed()
            
        self._show_toast(t("msg_saved"))

    def _show_toast(self, message: str):
        toast = QLabel(message, self)
        is_dark = load_config().get("dark_mode", True)
        if is_dark:
            toast.setStyleSheet("background-color: #b6f36d; color: #111111; padding: 12px 24px; border-radius: 8px; font-weight: bold; font-size: 14px;")
        else:
            toast.setStyleSheet("background-color: #b6f36d; color: #111111; padding: 12px 24px; border-radius: 8px; font-weight: bold; font-size: 14px;")
        toast.setAlignment(Qt.AlignCenter)
        toast.adjustSize()
        toast.move((self.width() - toast.width()) // 2, self.height() - toast.height() - 40)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 80))
        toast.setGraphicsEffect(shadow)
        
        toast.show()
        toast.raise_()
        QTimer.singleShot(2000, toast.deleteLater)
