"""
Mindfun — Settings Window

PyQt5 dark-themed settings window with 4 tabs:
1. Commitment Level (mode selection)
2. Game List (preset + custom games)
3. Mindful Questions (add/edit/delete)
4. Violation Log (report table + clear)

Includes language switcher (Vietnamese/English).
"""

import logging
from typing import Optional, Callable

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QPushButton, QRadioButton, QButtonGroup, QCheckBox,
    QLineEdit, QListWidget, QListWidgetItem, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QMessageBox,
    QInputDialog, QSpacerItem, QSizePolicy, QFrame,
    QGroupBox, QScrollArea, QTimeEdit,
)
from PyQt5.QtCore import Qt, QTime, QTimer
from PyQt5.QtGui import QFont, QIcon

from core.i18n import t, set_language, get_language
from core.config_manager import (
    load_config, save_config,
    load_questions, save_questions,
    load_game_presets,
)
from core import report_logger
from ui.game_manager_window import GameManagerWindow

logger = logging.getLogger("mindfun.settings_window")

# ─── Shared Styles ───────────────────────────────────────────────────

import ui.theme as theme


class SettingsWindow(QWidget):
    """
    Settings window with 4 tabs + language switcher.
    """

    def __init__(
        self,
        on_config_changed: Optional[Callable] = None,
        on_language_changed: Optional[Callable] = None,
        parent=None,
    ):
        super().__init__(parent)
        self._on_config_changed = on_config_changed
        self._on_language_changed = on_language_changed

        self.setWindowTitle(t("settings_title"))
        self.setMinimumSize(700, 550)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.setStyleSheet(theme.get_settings_style(load_config().get("dark_mode", True)))

        self._build_ui()
        self._apply_dynamic_colors(load_config().get("dark_mode", True))

    def _build_ui(self):
        """Build the complete settings UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ── Tab widget ──
        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_settings_tab(), f"  {t('tab_settings')}  ")
        self._tabs.addTab(self._build_questions_tab(), f"  {t('tab_questions')}  ")
        self._tabs.addTab(self._build_log_tab(), f"  {t('tab_log')}  ")
        layout.addWidget(self._tabs)

    # ─── Tab 0: General Settings ─────────────────────────────────────

    def _build_settings_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(24)
        config = load_config()

        # Commitment Level (Mode)
        group_mode = QGroupBox(t("tab_commitment"))
        mode_layout = QHBoxLayout(group_mode)
        
        radio_layout = QVBoxLayout()
        desc_layout = QVBoxLayout()
        
        self._mode_desc_label = QLabel("")
        self._mode_desc_label.setStyleSheet("color: #fcd7ae; font-size: 14px; font-style: italic; background-color: #988180; padding: 12px; border-radius: 8px;")
        self._mode_desc_label.setWordWrap(True)
        self._mode_desc_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        desc_layout.addWidget(self._mode_desc_label)
        
        current_mode = config.get("mode", 2)
        self._mode_group = QButtonGroup(self)
        self._modes_data = {
            1: (t("mode_1_name"), t("mode_1_desc")),
            2: (t("mode_2_name"), t("mode_2_desc")),
            3: (t("mode_3_name"), t("mode_3_desc")),
            4: (t("mode_4_name"), t("mode_4_desc")),
        }

        for mode_num, (name, desc) in self._modes_data.items():
            radio = QRadioButton(f"{name}")
            radio.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 8px;")
            if mode_num == current_mode:
                radio.setChecked(True)
                self._mode_desc_label.setText(desc)
            self._mode_group.addButton(radio, mode_num)
            radio_layout.addWidget(radio)

        self._mode_group.idClicked.connect(self._on_mode_changed)

        mode_layout.addLayout(radio_layout, 1)
        mode_layout.addLayout(desc_layout, 1)
            
        layout.addWidget(group_mode)

        # Sleep Lock
        group_sleep = QGroupBox(t("label_sleep_lock"))
        sleep_layout = QHBoxLayout(group_sleep)
        
        lbl_start = QLabel(t("label_night_start"))
        self._time_night_start = QTimeEdit()
        self._time_night_start.setDisplayFormat("HH:mm")
        
        lbl_end = QLabel(t("label_day_start"))
        self._time_day_start = QTimeEdit()
        self._time_day_start.setDisplayFormat("HH:mm")
        
        ns_str = config.get("night_start", "23:00")
        ds_str = config.get("day_start", "05:00")
        self._time_night_start.setTime(QTime.fromString(ns_str, "HH:mm"))
        self._time_day_start.setTime(QTime.fromString(ds_str, "HH:mm"))
        
        sleep_layout.addWidget(lbl_start)
        sleep_layout.addWidget(self._time_night_start)
        sleep_layout.addSpacing(20)
        sleep_layout.addWidget(lbl_end)
        sleep_layout.addWidget(self._time_day_start)
        sleep_layout.addStretch()
        
        layout.addWidget(group_sleep)

        # Anti-cheat (Friction Mode)
        group_ac = QGroupBox(t("label_anti_cheat"))
        ac_layout = QVBoxLayout(group_ac)
        
        self._anti_cheat_cb = QCheckBox(t("label_anti_cheat"))
        self._anti_cheat_cb.setChecked(config.get("anti_cheat", True))
        self._anti_cheat_cb.toggled.connect(self._on_ac_toggled)
        
        self._ac_desc = QLabel(f"    {t('anti_cheat_desc')}")
        self._ac_desc.setStyleSheet("color: #c6a9a3; font-size: 13px; margin-bottom: 8px;")
        self._ac_desc.setWordWrap(True)

        ac_layout.addWidget(self._anti_cheat_cb)
        ac_layout.addWidget(self._ac_desc)
        
        layout.addWidget(group_ac)

        # Language
        group_lang = QGroupBox(t("label_language"))
        lang_layout = QVBoxLayout(group_lang)
        self._lang_combo = QComboBox()
        self._lang_combo.addItem(t("lang_vietnamese"), "vi")
        self._lang_combo.addItem(t("lang_english"), "en")

        current_lang = config.get("language", "vi")
        idx = 0 if current_lang == "vi" else 1
        self._lang_combo.setCurrentIndex(idx)
        self._lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        lang_layout.addWidget(self._lang_combo)
        layout.addWidget(group_lang)

        # Dark Mode Toggle
        self._dark_mode_cb = QCheckBox("Dark Mode")
        self._dark_mode_cb.setChecked(config.get("dark_mode", True))
        layout.addWidget(self._dark_mode_cb)

        # Game Manager Button
        btn_game_manager = QPushButton(t("btn_manage_games"))
        btn_game_manager.setMinimumHeight(40)
        btn_game_manager.clicked.connect(self._open_game_manager)
        layout.addWidget(btn_game_manager)


        layout.addStretch()

        # Save Button
        btn_save = QPushButton(t("btn_save"))
        btn_save.setObjectName("btn_save_primary")
        btn_save.setMinimumHeight(40)
        btn_save.clicked.connect(self._save_general_settings)
        layout.addWidget(btn_save)

        return widget

    def _open_game_manager(self):
        """Open the external Game Manager window."""
        dialog = GameManagerWindow(on_config_changed=self._on_config_changed, parent=self)
        dialog.exec_()

    def _on_mode_changed(self, mode_id: int):
        """Update description label when mode changes."""
        if mode_id in self._modes_data:
            self._mode_desc_label.setText(self._modes_data[mode_id][1])

    def _on_ac_toggled(self, checked: bool):
        if not checked:
            box = QMessageBox(self)
            box.setIcon(QMessageBox.Warning)
            box.setWindowTitle(t("confirm_disable_ac_title"))
            box.setText(t("confirm_disable_ac_text"))
            
            yes_btn = box.addButton(t("confirm_yes"), QMessageBox.YesRole)
            no_btn = box.addButton(t("confirm_no"), QMessageBox.NoRole)
            box.setDefaultButton(no_btn)
            
            # Setup 5s delay
            yes_btn.setEnabled(False)
            original_yes_text = t("confirm_yes")
            self._ac_countdown = 5
            yes_btn.setText(f"{original_yes_text} ({self._ac_countdown}s)")
            
            timer = QTimer(box)
            def update_timer():
                self._ac_countdown -= 1
                if self._ac_countdown > 0:
                    yes_btn.setText(f"{original_yes_text} ({self._ac_countdown}s)")
                else:
                    yes_btn.setText(original_yes_text)
                    yes_btn.setEnabled(True)
                    timer.stop()
                    
            timer.timeout.connect(update_timer)
            timer.start(1000)
            
            box.exec_()
            
            if box.clickedButton() == no_btn or box.clickedButton() is None:
                self._anti_cheat_cb.blockSignals(True)
                self._anti_cheat_cb.setChecked(True)
                self._anti_cheat_cb.blockSignals(False)

    def _save_general_settings(self):
        """Save general settings to config."""
        config = load_config()
        ac_checked = self._anti_cheat_cb.isChecked()
        selected_mode = self._mode_group.checkedId()
        
        ns_str = self._time_night_start.time().toString("HH:mm")
        ds_str = self._time_day_start.time().toString("HH:mm")
        
        dark_checked = self._dark_mode_cb.isChecked()
        
        changed = False
        if config.get("dark_mode") != dark_checked:
            config["dark_mode"] = dark_checked
            logger.info("Dark mode changed to %s", dark_checked)
            self.setStyleSheet(theme.get_settings_style(dark_checked))
            self._apply_dynamic_colors(dark_checked)
            changed = True
            
        if selected_mode > 0 and config.get("mode") != selected_mode:
            config["mode"] = selected_mode
            logger.info("Mode changed to %d", selected_mode)
            changed = True
            
        if config.get("anti_cheat") != ac_checked:
            config["anti_cheat"] = ac_checked
            logger.info("Anti-cheat mode changed to %s", ac_checked)
            changed = True
            
        if config.get("night_start") != ns_str:
            config["night_start"] = ns_str
            changed = True
            
        if config.get("day_start") != ds_str:
            config["day_start"] = ds_str
            changed = True
            
        if changed:
            save_config(config)
            if self._on_config_changed:
                self._on_config_changed()
                
        QMessageBox.information(self, t("settings_title"), t("msg_saved"))

    # ─── Tab 2: Game List ────────────────────────────────────────────



    # ─── Tab 3: Tasks & Groups ───────────────────────────────────────

    def _build_questions_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        note = QLabel(t("question_note"))
        note.setStyleSheet("color: #6c7086; font-style: italic;")
        layout.addWidget(note)

        # Splitter layout (Groups on left, Tasks on right)
        split_layout = QHBoxLayout()
        split_layout.setSpacing(16)

        # ── Left Pane: Groups ──
        group_pane = QVBoxLayout()
        self._group_list = QListWidget()
        self._group_list.currentRowChanged.connect(self._on_group_selected)
        group_pane.addWidget(self._group_list)

        # Group actions
        group_btn_layout = QHBoxLayout()
        btn_add_group = QPushButton(t("btn_add_group"))
        btn_add_group.clicked.connect(self._add_group)
        group_btn_layout.addWidget(btn_add_group)

        btn_edit_group = QPushButton(t("btn_edit_group"))
        btn_edit_group.clicked.connect(self._edit_group)
        group_btn_layout.addWidget(btn_edit_group)

        btn_delete_group = QPushButton("X")
        btn_delete_group.setObjectName("btn_danger")
        btn_delete_group.setFixedWidth(40)
        btn_delete_group.clicked.connect(self._delete_group)
        group_btn_layout.addWidget(btn_delete_group)

        group_pane.addLayout(group_btn_layout)
        
        # Group Settings (Enabled & Checklist toggles)
        self._cb_group_enabled = QCheckBox(t("cb_group_enabled"))
        self._cb_group_enabled.clicked.connect(self._toggle_group_settings)
        self._cb_group_enabled.setEnabled(False)
        group_pane.addWidget(self._cb_group_enabled)

        self._cb_group_checklist = QCheckBox(t("cb_group_checklist"))
        self._cb_group_checklist.clicked.connect(self._toggle_group_settings)
        self._cb_group_checklist.setEnabled(False)
        group_pane.addWidget(self._cb_group_checklist)

        # Group Reorder Buttons
        group_reorder_layout = QHBoxLayout()
        btn_move_up = QPushButton(t("btn_move_up"))
        btn_move_up.clicked.connect(self._move_group_up)
        group_reorder_layout.addWidget(btn_move_up)

        btn_move_down = QPushButton(t("btn_move_down"))
        btn_move_down.clicked.connect(self._move_group_down)
        group_reorder_layout.addWidget(btn_move_down)
        
        group_pane.addLayout(group_reorder_layout)

        # ── Right Pane: Tasks ──
        task_pane = QVBoxLayout()
        self._task_list = QListWidget()
        self._task_list.itemDoubleClicked.connect(self._toggle_task_done)
        task_pane.addWidget(self._task_list)

        # Task actions
        task_btn_layout = QHBoxLayout()
        btn_add_task = QPushButton(t("btn_add_question"))
        btn_add_task.clicked.connect(self._add_task)
        task_btn_layout.addWidget(btn_add_task)

        btn_edit_task = QPushButton(t("btn_edit"))
        btn_edit_task.clicked.connect(self._edit_task)
        task_btn_layout.addWidget(btn_edit_task)

        btn_delete_task = QPushButton(t("btn_delete"))
        btn_delete_task.setObjectName("btn_danger")
        btn_delete_task.clicked.connect(self._delete_task)
        task_btn_layout.addWidget(btn_delete_task)

        task_pane.addLayout(task_btn_layout)

        # Add panes to split layout
        split_layout.addLayout(group_pane, 1)  # Ratio 1
        split_layout.addLayout(task_pane, 2)   # Ratio 2

        layout.addLayout(split_layout)

        # Initial load
        self._refresh_groups()

        return widget

    def _get_current_lang_groups(self):
        config = load_config()
        lang = config.get("language", "vi")
        questions_data = load_questions()
        return questions_data, lang, questions_data.get("task_groups", {}).setdefault(lang, [])

    def _refresh_groups(self):
        """Refresh the groups list."""
        self._group_list.clear()
        _, _, groups = self._get_current_lang_groups()
        for g in groups:
            self._group_list.addItem(g.get("name", "Unnamed"))
        
        # Reset right pane
        self._task_list.clear()
        self._cb_group_enabled.setEnabled(False)
        self._cb_group_enabled.setChecked(False)
        self._cb_group_checklist.setEnabled(False)
        self._cb_group_checklist.setChecked(False)

    def _on_group_selected(self, row: int):
        """Load tasks and settings for the selected group."""
        if row < 0:
            return
            
        _, _, groups = self._get_current_lang_groups()
        if row < len(groups):
            group = groups[row]
            
            # Update toggles
            self._cb_group_enabled.setEnabled(True)
            self._cb_group_enabled.setChecked(group.get("enabled", True))
            
            self._cb_group_checklist.setEnabled(True)
            self._cb_group_checklist.setChecked(group.get("is_checklist", False))
            
            # Update task list
            self._refresh_tasks(group)

    def _refresh_tasks(self, group: dict):
        self._task_list.clear()
        for item in group.get("items", []):
            text = item.get("text", "")
            if group.get("is_checklist", False):
                status = "[x] " if item.get("done", False) else "[ ] "
                text = status + text
            self._task_list.addItem(text)

    def _toggle_group_settings(self):
        row = self._group_list.currentRow()
        if row < 0:
            return
            
        q_data, lang, groups = self._get_current_lang_groups()
        if row < len(groups):
            groups[row]["enabled"] = self._cb_group_enabled.isChecked()
            groups[row]["is_checklist"] = self._cb_group_checklist.isChecked()
            save_questions(q_data)
            self._refresh_tasks(groups[row]) # Refresh to show/hide [ ]

    def _add_group(self):
        text, ok = QInputDialog.getText(self, t("group_dialog_title"), "")
        if ok and text.strip():
            import uuid
            q_data, lang, groups = self._get_current_lang_groups()
            groups.append({
                "id": uuid.uuid4().hex,
                "name": text.strip(),
                "enabled": True,
                "is_checklist": True,
                "items": []
            })
            save_questions(q_data)
            self._refresh_groups()

    def _edit_group(self):
        row = self._group_list.currentRow()
        if row < 0: return
        
        q_data, lang, groups = self._get_current_lang_groups()
        old_name = groups[row].get("name", "")
        text, ok = QInputDialog.getText(self, t("group_dialog_title"), "", text=old_name)
        if ok and text.strip():
            groups[row]["name"] = text.strip()
            save_questions(q_data)
            self._refresh_groups()
            self._group_list.setCurrentRow(row)

    def _delete_group(self):
        """Delete selected group."""
        row = self._group_list.currentRow()
        if row < 0:
            return

        questions_data, lang, groups = self._get_current_lang_groups()
        if row < len(groups):
            del groups[row]
            save_questions(questions_data)
            self._refresh_groups()

    def _move_group_up(self):
        """Move selected group up."""
        row = self._group_list.currentRow()
        if row > 0:
            questions_data, lang, groups = self._get_current_lang_groups()
            groups[row - 1], groups[row] = groups[row], groups[row - 1]
            save_questions(questions_data)
            self._refresh_groups()
            self._group_list.setCurrentRow(row - 1)

    def _move_group_down(self):
        """Move selected group down."""
        row = self._group_list.currentRow()
        questions_data, lang, groups = self._get_current_lang_groups()
        if 0 <= row < len(groups) - 1:
            groups[row + 1], groups[row] = groups[row], groups[row + 1]
            save_questions(questions_data)
            self._refresh_groups()
            self._group_list.setCurrentRow(row + 1)

    def _toggle_group_settings(self):
        row = self._group_list.currentRow()
        if row < 0: return
        
        q_data, lang, groups = self._get_current_lang_groups()
        groups[row]["enabled"] = self._cb_group_enabled.isChecked()
        groups[row]["is_checklist"] = self._cb_group_checklist.isChecked()
        save_questions(q_data)

    def _add_task(self):
        group_row = self._group_list.currentRow()
        if group_row < 0: return
        
        text, ok = QInputDialog.getText(self, t("question_dialog_title"), "")
        if ok and text.strip():
            import uuid
            q_data, lang, groups = self._get_current_lang_groups()
            groups[group_row].setdefault("items", []).append({
                "id": uuid.uuid4().hex,
                "text": text.strip(),
                "done": False
            })
            save_questions(q_data)
            self._refresh_tasks(groups[group_row])

    def _edit_task(self):
        group_row = self._group_list.currentRow()
        task_row = self._task_list.currentRow()
        if group_row < 0 or task_row < 0: return
        
        q_data, lang, groups = self._get_current_lang_groups()
        items = groups[group_row].get("items", [])
        if task_row < len(items):
            old_text = items[task_row].get("text", "")
            text, ok = QInputDialog.getText(self, t("question_dialog_title"), "", text=old_text)
            if ok and text.strip():
                items[task_row]["text"] = text.strip()
                save_questions(q_data)
                self._refresh_tasks(groups[group_row])
                self._task_list.setCurrentRow(task_row)

    def _delete_task(self):
        group_row = self._group_list.currentRow()
        task_row = self._task_list.currentRow()
        if group_row < 0 or task_row < 0: return
        
        q_data, lang, groups = self._get_current_lang_groups()
        items = groups[group_row].get("items", [])
        if task_row < len(items):
            items.pop(task_row)
            save_questions(q_data)
            self._refresh_tasks(groups[group_row])

    def _toggle_task_done(self, item):
        group_row = self._group_list.currentRow()
        task_row = self._task_list.row(item)
        if group_row < 0 or task_row < 0: return

        q_data, lang, groups = self._get_current_lang_groups()
        if not groups[group_row].get("is_checklist", False):
            return # Only checklist items have 'done' state
            
        items = groups[group_row].get("items", [])
        if task_row < len(items):
            # Toggle boolean
            items[task_row]["done"] = not items[task_row].get("done", False)
            save_questions(q_data)
            self._refresh_tasks(groups[group_row])
            self._task_list.setCurrentRow(task_row)

    # ─── Tab 4: Violation Log ────────────────────────────────────────

    def _build_log_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        # Header controls (Range selection)
        header_layout = QHBoxLayout()
        header_label = QLabel(t("log_chart_title"))
        header_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        self._range_combo = QComboBox()
        self._range_combo.addItems([t("log_range_7"), t("log_range_14"), t("log_range_30")])
        self._range_combo.currentIndexChanged.connect(self._refresh_log_chart)
        header_layout.addWidget(self._range_combo)
        layout.addLayout(header_layout)

        # Bar Chart
        from ui.bar_chart import PlayTimeBarChart
        self._bar_chart = PlayTimeBarChart()
        layout.addWidget(self._bar_chart, 1)

        # Legend
        legend_layout = QHBoxLayout()
        legend_layout.addStretch()
        
        self._valid_color = QWidget()
        self._valid_color.setFixedSize(12, 12)
        self._valid_color.setStyleSheet("background-color: #c6a9a3; border-radius: 2px;")
        legend_layout.addWidget(self._valid_color)
        legend_layout.addWidget(QLabel(t("log_legend_valid")))
        
        legend_layout.addSpacing(20)
        
        self._viol_color = QWidget()
        self._viol_color.setFixedSize(12, 12)
        self._viol_color.setStyleSheet("background-color: #8b3a3a; border-radius: 2px;")
        legend_layout.addWidget(self._viol_color)
        legend_layout.addWidget(QLabel(t("log_legend_viol")))
        
        legend_layout.addStretch()
        layout.addLayout(legend_layout)

        self._refresh_log_chart()

        return widget

    def _refresh_log_chart(self):
        """Refresh the violation log chart."""
        from core.report_logger import get_daily_stats
        stats = get_daily_stats()
        
        idx = self._range_combo.currentIndex()
        days = 7
        if idx == 1: days = 14
        elif idx == 2: days = 30
            
        self._bar_chart.set_data(stats, days)

    # ─── Language switcher ───────────────────────────────────────────

    def _on_lang_changed(self, index):
        """Handle language change."""
        lang = self._lang_combo.itemData(index)
        if lang:
            config = load_config()
            config["language"] = lang
            save_config(config)
            set_language(lang)
            logger.info("Language changed to %s", lang)

            # Notify parent to rebuild menus etc.
            if self._on_language_changed:
                self._on_language_changed()

            # Rebuild this window
            QMessageBox.information(
                self,
                "Language Changed",
                "Please close and reopen Settings for the language change to take full effect."
            )

    # ─── Public methods ──────────────────────────────────────────────

    def refresh_all(self):
        """Refresh all tabs (call after config changes)."""
        self._refresh_groups()
        self._refresh_log_chart()

    def show_log_tab(self):
        """Switch to the log tab and refresh data."""
        self._tabs.setCurrentIndex(3)
        self._refresh_log_chart()
        self.show()
        self.raise_()
        self.activateWindow()

    def _apply_dynamic_colors(self, is_dark: bool):
        pal = theme.get_settings_palette(is_dark)
        self._mode_desc_label.setStyleSheet(f"color: {pal['text_color']}; font-size: 14px; font-style: italic; background-color: {pal['desc_bg']}; padding: 12px; border-radius: 8px;")
        self._ac_desc.setStyleSheet(f"color: {pal['desc_color']}; font-size: 13px; font-style: italic;")
        
        chart_colors = theme.get_chart_colors(is_dark)
        if hasattr(self, '_valid_color'):
            self._valid_color.setStyleSheet(f"background-color: {chart_colors['valid']}; border-radius: 2px;")
            self._viol_color.setStyleSheet(f"background-color: {chart_colors['violation']}; border-radius: 2px;")
        
        if hasattr(self, '_bar_chart'):
            self._bar_chart.set_dark_mode(is_dark)
            self._bar_chart.update()

        theme.apply_window_titlebar_color(self.winId(), is_dark)
