"""
Mindfun — Internationalization (i18n) Module

Provides Vietnamese/English language switching for all UI strings.
"""

# All translatable strings keyed by language code
STRINGS = {
    "vi": {
        # Lockscreen
        "game_paused": "Paused: {game}",
        "seconds_remaining": "Wait {seconds}s",
        "unfinished_tasks_prompt": "Pending Tasks:",
        "unfinished_tasks_ask": "Bạn vẫn còn công việc chưa xong. Bạn có tiếp tục chơi không?",
        "sleep_lock_warning": "Đã quá giờ đi ngủ. Hãy tắt {game} để bảo vệ sức khỏe!",
        "soft_sleep_lock_warning": "Đã đến giờ đi ngủ. Bạn có chắc chắn muốn tiếp tục chơi {game}?",
        "btn_quit": "THOÁT",
        "btn_play": "CHƠI TIẾP",
        "btn_next": "Tiếp tục",
        "btn_finish_tasks": "HOÀN THÀNH NHIỆM VỤ ĐỂ CHƠI",
        "waiting_prompt": "Hãy chậm lại và hít thở",

        # Tray
        "tray_tooltip": "Mindfun đang bảo vệ bạn",
        "tray_title": "Mindfun v1.0.0",
        "tray_status_active": "Trạng thái: Đang hoạt động ✓",
        "tray_status_paused": "Trạng thái: Tạm dừng ⏸",
        "tray_current_mode": "Mode hiện tại: {mode}",
        "tray_open_settings": "Mở Cài Đặt...",
        "tray_view_log": "Xem Nhật Ký...",
        "tray_pause_today": "Tạm dừng hôm nay",
        "tray_resume": "Bật lại Bảo Vệ",
        "tray_quit": "Thoát Mindfun",
        "tray_reset_whitelist": "Xóa lịch sử cho phép",
        "tray_about": "Giới thiệu",

        # Settings tabs
        "settings_title": "Mindfun — Cài Đặt",
        "tab_commitment": "Mức Độ Cam Kết",
        "tab_games": "Danh Sách Game",
        "tab_questions": "Câu Hỏi Thức Tỉnh",
        "tab_log": "Nhật Ký ",
        "tab_settings": "Cài đặt chung",

        # Settings — General
        "label_anti_cheat": "Chặn thoát nhanh (Anti-Cheat)",
        "anti_cheat_desc": "Khi bật, nút Thoát và Tạm dừng ở khay hệ thống sẽ bị vô hiệu hóa. Người dùng cần vào Task Manager để tắt ứng dụng.",
        "label_dev_mode": "Chế độ Nhà phát triển (Test Mode)",
        "dev_mode_desc": "Bỏ qua đếm ngược và hiển thị nút Reset trên khay hệ thống.",
        "label_sleep_lock": "Giờ đi ngủ (Sleep Lock)",
        "label_night_start": "Bắt đầu khóa lúc:",
        "label_day_start": "Mở khóa lúc:",

        # Mode descriptions
        "mode_1_name": "Nhắc nhở (15 giây)",
        "mode_1_desc": "<b>Cấu hình:</b><ul style='margin-top: 4px; margin-bottom: 0px;'><li>⏳ <b>Thời gian chờ:</b> 15s</li><li>🌙 <b>Khóa giờ ngủ (Sleep lock):</b> Nhắc nhở</li><li>📋 <b>Công việc chưa xong:</b> Nhắc nhở</li></ul>",
        "mode_2_name": "Kỷ luật (1 phút)",
        "mode_2_desc": "<b>Cấu hình:</b><ul style='margin-top: 4px; margin-bottom: 0px;'><li>⏳ <b>Thời gian chờ:</b> 1m</li><li>🌙 <b>Khóa giờ ngủ (Sleep lock):</b> Nhắc nhở</li><li>📋 <b>Công việc chưa xong:</b> Nhắc nhở</li></ul>",
        "mode_3_name": "Cai nghiện (3 phút)",
        "mode_3_desc": "<b>Cấu hình:</b><ul style='margin-top: 4px; margin-bottom: 0px;'><li>⏳ <b>Thời gian chờ:</b> 3m</li><li>🌙 <b>Khóa giờ ngủ (Sleep lock):</b> <span style='color:#ed8796;font-weight:bold;'>Khóa màn hình (Overlay)</span></li><li>📋 <b>Công việc chưa xong:</b> Nhắc nhở</li></ul>",
        "mode_4_name": "Thiết quân luật (5 phút)",
        "mode_4_desc": "<b>Cấu hình:</b><ul style='margin-top: 4px; margin-bottom: 0px;'><li>⏳ <b>Thời gian chờ:</b> 5m</li><li>🌙 <b>Khóa giờ ngủ (Sleep lock):</b> <span style='color:#ed8796;font-weight:bold;'>Khóa màn hình (Overlay)</span></li><li>📋 <b>Công việc chưa xong:</b> <span style='color:#ed8796;font-weight:bold;'>Khóa màn hình (Overlay)</span></li></ul>",
        "mode_5_name": "Tùy chỉnh (Custom)",
        "mode_5_desc": "<b>Cấu hình:</b><br>Bạn có thể tự cấu hình thời gian đếm ngược và chọn chế độ Nhắc nhở/Khóa màn hình một cách độc lập.",
        
        "label_custom_duration": "Thời gian chờ (giây):",
        "label_custom_sleep": "Khóa giờ ngủ (Sleep Lock):",
        "label_custom_task": "Công việc chưa xong (Task Lock):",
        "opt_remind": "Nhắc nhở",
        "opt_lock": "Khóa màn hình",

        # Settings — Games tab
        "add_game_placeholder": "TenGame.exe",
        "btn_add": "+ Thêm",
        "btn_delete": "Xóa",
        "btn_save": "Lưu thay đổi",
        "btn_save_list": "Lưu danh sách",
        "msg_saved": "Đã lưu cài đặt thành công!",
        "btn_manage_games": "Quản lý Danh sách Game",
        "placeholder_search_game": "Tìm kiếm game...",
        "title_game_manager": "Quản lý Game",
        "placeholder_custom_name": "Tên Game (VD: Minecraft)",
        "placeholder_custom_exe": "Tên file (VD: javaw.exe)",

        # Settings — Questions tab
        "btn_edit": "Sửa",
        "btn_add_question": "+ Thêm câu hỏi mới",
        "btn_cancel": "Hủy",
        "question_dialog_title": "Thêm/Sửa câu hỏi",
        "question_note": "Nhóm có chế độ 'Checklist' sẽ yêu cầu bạn tích hoàn thành. Nhóm khác sẽ lấy ngẫu nhiên 1 câu hỏi.",
        "btn_add_group": "+ Thêm Nhóm",
        "btn_edit_group": "Sửa Nhóm",
        "group_dialog_title": "Tên Nhóm",
        "cb_group_enabled": "Bật nhóm này",
        "cb_group_checklist": "Dùng làm Checklist (Thay vì lấy ngẫu nhiên 1 câu)",

        # Settings — Log tab
        "log_col_date": "Ngày",
        "log_col_game": "Game",
        "log_col_start": "Giờ bắt đầu",
        "log_col_minutes": "Số phút quá giờ",
        "btn_clear_log": "Xóa toàn bộ nhật ký",
        "log_minutes_suffix": "phút",

        # Settings — Language
        "label_language": "Ngôn ngữ ",
        
        "group_preset_games": "Game hệ thống (Preset)",
        "group_custom_games": "Game tùy chỉnh (Custom)",
        "btn_move_up": "▲ Lên",
        "btn_move_down": "▼ Xuống",
        "log_chart_title": "Thống kê thời gian chơi:",
        "log_range_7": "7 Ngày",
        "log_range_14": "14 Ngày",
        "log_range_30": "30 Ngày",
        "log_legend_valid": "Giờ chơi hợp lệ",
        "log_legend_viol": "Giờ chơi đêm (Vi phạm)",
        "lang_vietnamese": "Tiếng Việt",
        "lang_english": "English",


        # Night guard toasts
        "toast_night_report": "Báo cáo: Vừa rồi bạn đã thức muộn chơi {game} khoảng {minutes} phút. Hãy chú ý giữ gìn sức khỏe nhé!",
        "toast_night_remind": "Bạn đang chơi game trong giờ đi ngủ. Hệ thống sẽ ghi lại vi phạm này để nhắc nhở!",
        "toast_hardcore_kill": "⚠️ Mindfun đã khóa màn hình game của bạn. Đã qua {time}.\nHãy tắt máy và đi ngủ.",
        "toast_title": "Mindfun",

        # About
        "about_title": "Giới thiệu Mindfun",
        "about_text": (
            "Mindfun v1.0.0\n\n"
            "Không cấm đoán — chỉ tạo khoảng dừng tỉnh thức.\n\n"
            "Triết lý: Behavioral Friction — tạo ma sát đủ để\n"
            "lý trí thức tỉnh trước khi xung động chiến thắng.\n\n"
            "Local-only. Không gửi dữ liệu qua mạng.\n"
            "Open Source."
        ),

        # Confirm dialogs
        "confirm_clear_log": "Bạn có chắc muốn xóa toàn bộ nhật ký?",
        "confirm_yes": "Có",
        "confirm_no": "Không",
        "confirm_title": "Xác nhận",
        "confirm_pause": "Tạm dừng Mindfun trong ngày hôm nay?\nMindfun sẽ tự bật lại vào 05:00 sáng mai.",
        "confirm_disable_ac_title": "Cảnh báo",
        "confirm_disable_ac_text": "Bạn có chắc chắn muốn tắt chế độ Anti-Cheat không?\n\nViệc này sẽ gỡ bỏ lớp bảo vệ của Mindfun, khiến bạn dễ dàng bị khuất phục bởi xung động nhất thời và có thể sẽ phải hối hận vì mất kiểm soát.\n\nBạn vẫn muốn tắt chứ?",
    },
    "en": {
        # Lockscreen
        "game_paused": "Paused: {game}",
        "seconds_remaining": "Wait {seconds}s",
        "unfinished_tasks_prompt": "Pending Tasks:",
        "unfinished_tasks_ask": "You have unfinished tasks. Do you still want to play?",
        "sleep_lock_warning": "It's past your bedtime. Please close {game} and go to sleep!",
        "soft_sleep_lock_warning": "It's past your bedtime. Are you sure you want to continue playing {game}?",
        "btn_quit": "QUIT",
        "btn_play": "PLAY",
        "btn_next": "Next",
        "btn_finish_tasks": "FINISH TASKS TO PLAY",
        "waiting_prompt": "Take a moment to slow down.",

        # Tray
        "tray_tooltip": "Mindfun is protecting you",
        "tray_title": "Mindfun v1.0.0",
        "tray_status_active": "Status: Active ✓",
        "tray_status_paused": "Status: Paused ⏸",
        "tray_current_mode": "Current mode: {mode}",
        "tray_open_settings": "Open Settings...",
        "tray_view_log": "View Log...",
        "tray_pause_today": "Pause for Today",
        "tray_resume": "Resume Protection",
        "tray_quit": "Quit Mindfun",
        "tray_reset_whitelist": "Lock Game (Clear history)",
        "tray_about": "About",

        # Settings tabs
        "settings_title": "Mindfun — Settings",
        "tab_commitment": "Commitment Level",
        "tab_games": "Game List",
        "tab_questions": "Mindful Questions",
        "tab_log": "Log",
        "tab_settings": "General Settings",

        # Settings — General
        "label_anti_cheat": "Friction Lock (Anti-Cheat)",
        "anti_cheat_desc": "When enabled, the Quit and Pause buttons in the system tray are disabled. To close the app, you must use Task Manager — creating a small but intentional friction.",
        "label_dev_mode": "Developer Mode",
        "dev_mode_desc": "Bypasses countdown and shows Reset button in tray.",
        "label_sleep_lock": "Sleep Time (Sleep Lock)",
        "label_night_start": "Start lock at:",
        "label_day_start": "End lock at:",

        # Mode descriptions
        "mode_1_name": "Reminder (15 seconds)",
        "mode_1_desc": "<b>Configuration:</b><ul style='margin-top: 4px; margin-bottom: 0px;'><li>⏳ <b>Delay Time:</b> 15s</li><li>🌙 <b>Sleep Lock:</b> Reminder</li><li>📋 <b>Unfinished Task:</b> Reminder</li></ul>",
        "mode_2_name": "Discipline (1 minute)",
        "mode_2_desc": "<b>Configuration:</b><ul style='margin-top: 4px; margin-bottom: 0px;'><li>⏳ <b>Delay Time:</b> 1m</li><li>🌙 <b>Sleep Lock:</b> Reminder</li><li>📋 <b>Unfinished Task:</b> Reminder</li></ul>",
        "mode_3_name": "Rehab (3 mins)",
        "mode_3_desc": "<b>Config:</b><ul style='margin-top: 4px; margin-bottom: 0px;'><li>⏳ <b>Wait time:</b> 3m</li><li>🌙 <b>Sleep lock:</b> <span style='color:#ed8796;font-weight:bold;'>Lockscreen Overlay</span></li><li>📋 <b>Incomplete tasks:</b> Remind</li></ul>",
        "mode_4_name": "Martial Law (5 mins)",
        "mode_4_desc": "<b>Config:</b><ul style='margin-top: 4px; margin-bottom: 0px;'><li>⏳ <b>Wait time:</b> 5m</li><li>🌙 <b>Sleep lock:</b> <span style='color:#ed8796;font-weight:bold;'>Lockscreen Overlay</span></li><li>📋 <b>Incomplete tasks:</b> <span style='color:#ed8796;font-weight:bold;'>Lockscreen Overlay</span></li></ul>",
        "mode_5_name": "Custom Mode",
        "mode_5_desc": "<b>Config:</b><br>Freely adjust the wait time (seconds) and choose lockscreen behaviors independently.",

        "label_custom_duration": "Wait time (seconds):",
        "label_custom_sleep": "Sleep Lock:",
        "label_custom_task": "Incomplete Tasks (Task Lock):",
        "opt_remind": "Remind Only",
        "opt_lock": "Lockscreen",

        # Settings — Games tab
        "add_game_placeholder": "GameName.exe",
        "btn_add": "+ Add",
        "btn_delete": "Delete",
        "btn_save": "Save changes",
        "btn_save_list": "Save list",
        "msg_saved": "Settings saved successfully!",
        "btn_manage_games": "Manage Game List",
        "placeholder_search_game": "Search games...",
        "title_game_manager": "Game Manager",
        "placeholder_custom_name": "Game Name (e.g. Minecraft)",
        "placeholder_custom_exe": "Executable (e.g. javaw.exe)",

        # Settings — Questions tab
        "btn_edit": "Edit",
        "btn_add_question": "+ Add new question",
        "btn_cancel": "Cancel",
        "question_dialog_title": "Add/Edit Question",
        "question_note": "Groups with 'Checklist' enabled will ask you to check off items. Others will pick a random question.",
        "btn_add_group": "+ Add Group",
        "btn_edit_group": "Edit Group",
        "group_dialog_title": "Group Name",
        "cb_group_enabled": "Enable this group",
        "cb_group_checklist": "Use as Checklist (instead of random questions)",

        # Settings — Log tab
        "log_col_date": "Date",
        "log_col_game": "Game",
        "log_col_start": "Start Time",
        "log_col_minutes": "Minutes Over",
        "btn_clear_log": "Clear All Logs",
        "log_minutes_suffix": "min",

        # Settings — Language
        "label_language": "Language",
        

        "group_preset_games": "Preset Games",
        "group_custom_games": "Custom Games",
        "btn_move_up": "▲ Up",
        "btn_move_down": "▼ Down",
        "log_chart_title": "Playtime Statistics:",
        "log_range_7": "7 Days",
        "log_range_14": "14 Days",
        "log_range_30": "30 Days",
        "log_legend_valid": "Valid Playtime",
        "log_legend_viol": "Night Playtime (Violation)",
        "lang_vietnamese": "Tiếng Việt",
        "lang_english": "English",
        "lang_english": "English",


        # Night guard toasts
        "toast_night_report": "Report: Last night you played {game} for ~{minutes} minutes. Take care of your health!",
        "toast_night_remind": "You are playing games during sleep hours. This violation will be recorded!",
        "toast_hardcore_kill": "⚠️ Mindfun locked your screen. It's past {time}.\nPlease turn off your PC and sleep.",
        "toast_title": "Mindfun",

        # About
        "about_title": "About Mindfun",
        "about_text": (
            "Mindfun v1.0.0\n\n"
            "No bans — just a mindful pause.\n\n"
            "Philosophy: Behavioral Friction — creating just enough\n"
            "resistance for reason to awaken before impulse wins.\n\n"
            "Local-only. No data sent over the network.\n"
            "Open Source."
        ),

        # Confirm dialogs
        "confirm_clear_log": "Are you sure you want to clear all logs?",
        "confirm_yes": "Yes",
        "confirm_no": "No",
        "confirm_title": "Confirm",
        "confirm_pause": "Pause Mindfun for today?\nMindfun will resume at 05:00 AM tomorrow.",
        "confirm_disable_ac_title": "Warning",
        "confirm_disable_ac_text": "Are you sure you want to disable Anti-Cheat mode?\n\nThis will remove Mindfun's protection layer, making it easy for you to give in to temporary impulses and potentially regret losing self-control.\n\nDo you still want to disable it?",
    },
}

# Mode duration mapping (mode number → seconds)
MODE_DURATIONS = {
    1: 15,
    2: 60,
    3: 180,
    4: 300,
}

# Current language (module-level state, set at startup)
_current_lang = "vi"


def set_language(lang_code: str):
    """Set the current language ('vi' or 'en')."""
    global _current_lang
    if lang_code in STRINGS:
        _current_lang = lang_code



def t(key: str, **kwargs) -> str:
    """
    Translate a string key to the current language.

    Usage:
        t("game_paused", game="League of Legends")
        t("btn_quit")
    """
    lang = "en" if key.startswith("toast_") else _current_lang
    text = STRINGS.get(lang, STRINGS["vi"]).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text


def get_mode_name(mode: int) -> str:
    """Get the localized display name for a mode number."""
    return t(f"mode_{mode}_name")


def get_mode_duration(mode: int) -> int:
    """Get the countdown duration in seconds for a mode number."""
    if mode == 5:
        from core.config_manager import load_config
        return load_config().get("custom_mode", {}).get("duration", 60)
    return MODE_DURATIONS.get(mode, 60)
