"""
Mindfun — Internationalization (i18n) Module

Provides Vietnamese/English language switching for all UI strings.
"""

# All translatable strings keyed by language code
STRINGS = {
    "vi": {
        # Lockscreen
        "game_paused": "Tạm dừng: {game}",
        "seconds_remaining": "Chờ {seconds}s",
        "unfinished_tasks_prompt": "Nhiệm vụ chưa hoàn thành:",
        "unfinished_tasks_ask": "Bạn vẫn còn công việc chưa xong. Bạn có tiếp tục chơi không?",
        "sleep_lock_warning": "Đã quá giờ đi ngủ! Hãy tắt máy và nghỉ ngơi.",
        "soft_sleep_lock_warning": "Đã muộn rồi, bạn nên đi ngủ sớm!",

        "btn_prev": "Trước",
        "btn_select_all": "Chọn tất cả",
        "btn_deselect_all": "Bỏ chọn tất cả",
        "btn_scan_games": "🔍 Quét Game",
        "lbl_selected_zero": "Đã chọn: 0 game",
        "lbl_selected_count": "Đã chọn: {count} / {total} game",
        "msg_game_exists": "Game này đã có trong danh sách Custom Games!",
        "msg_scan_no_games": "Không tìm thấy game nào trong các thư mục mặc định (Steam, Riot, Epic).",
        "msg_scan_added": "Đã quét và thêm {added} game mới vào danh sách Custom.",
        "title_auto_scan": "Quét Tự Động",
        "msg_please_close_game": "Vui lòng tắt {friendly_name} để hoàn tất.",
        "time_meditation": "Thời gian tĩnh tâm: {total_left}s\n\n",
        "strict_task_block": "Bạn còn công việc BẮT BUỘC chưa xong!",
        "soft_task_block": "Bạn còn công việc chưa xong",
        "btn_quit": "THOÁT",
        "btn_play": "CHƠI TIẾP",
        "btn_next": "Sau",
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
        "tray_toggle_bubble": "Bật / Tắt Bong Bóng",

        # Bubble / Chat head
        "bubble_hide": "Ẩn bong bóng (Chat Head)",
        "bubble_play_time": "Hôm nay bạn đã chơi game tổng cộng {mins} phút.",
        "bubble_play_time_alert": "Bạn đã chơi game được {minutes} phút rồi, hãy nghỉ ngơi một chút nhé!",

        # Anti-cheat
        "anti_cheat_title": "Anti-Cheat",
        "anti_cheat_warning": "Chế độ Chặn thoát nhanh (Anti-Cheat) đang bật.\nBạn không thể thoát MindFun. Hãy vào Cài Đặt để tắt chế độ này nếu bạn thực sự muốn thoát!",
        "anti_cheat_pause_warning": "Chế độ Chặn thoát nhanh (Anti-Cheat) đang bật.\nBạn không thể tạm dừng MindFun. Hãy vào Cài Đặt để tắt chế độ này nếu cần.",

        # Chart tooltips
        "chart_total": "Tổng: {total_h:.1f}h",
        "chart_valid": "Hợp lệ: {valid_h:.1f}h",
        "chart_viol": "Quá giờ: {viol_h:.1f}h",

        # Settings tabs
        "settings_title": "Mindfun — Cài Đặt",
        "tab_commitment": "Mức Độ Cam Kết",
        "tab_games": "Danh Sách Game",
        "tab_questions": "Câu Hỏi Thức Tỉnh",
        "tab_log": "Nhật Ký",
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
        "mode_1_desc": "<b>Cấu hình:</b><ul style='margin-top: 4px; margin-bottom: 0px;'><li>⏳ <b>Thời gian chờ:</b> 15s</li><li>🌙 <b>Khóa giờ ngủ:</b> Nhắc nhở</li><li>📋 <b>Công việc chưa xong:</b> Nhắc nhở</li></ul>",
        "mode_2_name": "Kỷ luật (1 phút)",
        "mode_2_desc": "<b>Cấu hình:</b><ul style='margin-top: 4px; margin-bottom: 0px;'><li>⏳ <b>Thời gian chờ:</b> 1m</li><li>🌙 <b>Khóa giờ ngủ:</b> Nhắc nhở</li><li>📋 <b>Công việc chưa xong:</b> Nhắc nhở</li></ul>",
        "mode_3_name": "Cai nghiện (3 phút)",
        "mode_3_desc": "<b>Cấu hình:</b><ul style='margin-top: 4px; margin-bottom: 0px;'><li>⏳ <b>Thời gian chờ:</b> 3m</li><li>🌙 <b>Khóa giờ ngủ:</b> <span style='color:#ed8796;font-weight:bold;'>Khóa màn hình</span></li><li>📋 <b>Công việc chưa xong:</b> Nhắc nhở</li></ul>",
        "mode_4_name": "Thiết quân luật (5 phút)",
        "mode_4_desc": "<b>Cấu hình:</b><ul style='margin-top: 4px; margin-bottom: 0px;'><li>⏳ <b>Thời gian chờ:</b> 5m</li><li>🌙 <b>Khóa giờ ngủ:</b> <span style='color:#ed8796;font-weight:bold;'>Khóa màn hình</span></li><li>📋 <b>Công việc chưa xong:</b> <span style='color:#ed8796;font-weight:bold;'>Khóa màn hình</span></li></ul>",
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
        "label_language": "Ngôn ngữ",

        # Settings - Theme & Sound
        "label_theme": "Giao diện (Theme)",
        "label_primary_color": "Màu chủ đạo (Primary Accent):",
        "btn_pick_color": "Chọn màu",
        "label_sound": "Âm thanh",
        "label_checklist_sound": "Âm thanh hoàn thành Checklist:",
        "label_notif_sound": "Âm thanh Thông báo:",
        "opt_custom_sound": "Tùy chọn khác (Custom)...",
        "btn_browse": "Duyệt...",

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

        # Onboarding
        "onb_lang_title": "Chọn ngôn ngữ",
        "onb_lang_desc": "Bạn muốn sử dụng ngôn ngữ nào cho MindFun?",
        "onb_title": "Chào mừng đến với MindFun",
        "onb_desc": "Đây là lần đầu tiên bạn mở ứng dụng.\nBạn có muốn chạy Trình hướng dẫn thiết lập không?",
        "onb_yes": "Có, hãy hướng dẫn tôi",
        "onb_no": "Không, để tôi tự khám phá",
        "onb_step1": "Bước 1: Chọn mức độ cam kết",
        "onb_step1_desc": "Mức độ cam kết quyết định độ khó của hệ thống và thời gian tự ý thức.",
        "onb_step2": "Bước 2: Thêm Game cần quản lý",
        "onb_step2_desc": "MindFun sẽ chặn và yêu cầu bạn rèn luyện não trước khi mở những game này.",
        "onb_add_game": "Chọn File Game",
        "onb_finish_title": "Hoàn tất thiết lập!",
        "onb_finish_desc": "MindFun đã sẵn sàng bảo vệ thời gian của bạn.\nHãy bấm Bắt đầu để trải nghiệm!",
        "onb_btn_next": "Tiếp theo",
        "onb_btn_back": "Quay lại",
        "onb_btn_start": "Bắt đầu",
        "onb_btn_skip": "Bỏ qua",
        "onb_btn_browse": "Duyệt tìm File (.exe)",
        "onb_mode1_desc": "Vài giây ngắn đủ để bạn tự ý thức.",
        "onb_mode2_desc": "Thời gian dài hơn, ý thức tốt hơn.",
        "onb_mode3_desc": "Hệ thống sẽ khó hơn, bạn sẽ tự ý thức được.",
        "onb_mode4_desc": "Không dành cho người không muốn bỏ game!",
    },

    "en": {
        # Lockscreen
        "game_paused": "Paused: {game}",
        "seconds_remaining": "Wait {seconds}s",
        "unfinished_tasks_prompt": "Pending Tasks:",
        "unfinished_tasks_ask": "You have unfinished tasks. Do you still want to play?",
        "sleep_lock_warning": "It's past your bedtime! Please shut down and rest.",
        "soft_sleep_lock_warning": "It's getting late, you should sleep early!",

        "btn_prev": "Prev",
        "btn_select_all": "Select All",
        "btn_deselect_all": "Deselect All",
        "btn_scan_games": "🔍 Scan Games",
        "lbl_selected_zero": "Selected: 0 games",
        "lbl_selected_count": "Selected: {count} / {total} games",
        "msg_game_exists": "This game is already in the Custom Games list!",
        "msg_scan_no_games": "No games found in default directories (Steam, Riot, Epic).",
        "msg_scan_added": "Scanned and added {added} new games to the Custom list.",
        "title_auto_scan": "Auto Scan",
        "msg_please_close_game": "Please close {friendly_name} to complete.",
        "time_meditation": "Mindfulness time: {total_left}s\n\n",
        "strict_task_block": "You have MANDATORY tasks unfinished!",
        "soft_task_block": "You have unfinished tasks",
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
        "tray_toggle_bubble": "Toggle Chat Bubble",

        # Bubble / Chat head
        "bubble_hide": "Hide Chat Head",
        "bubble_play_time": "You have played for {mins} minutes today.",
        "bubble_play_time_alert": "You have been playing for {minutes} minutes. Take a break!",

        # Anti-cheat
        "anti_cheat_title": "Anti-Cheat",
        "anti_cheat_warning": "Anti-Cheat (Friction Lock) is enabled.\nYou cannot quit MindFun. Please disable this mode in Settings if you really want to quit!",
        "anti_cheat_pause_warning": "Anti-Cheat (Friction Lock) is enabled.\nYou cannot pause MindFun. Please disable this mode in Settings if needed.",

        # Chart tooltips
        "chart_total": "Total: {total_h:.1f}h",
        "chart_valid": "Valid: {valid_h:.1f}h",
        "chart_viol": "Over: {viol_h:.1f}h",

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

        "label_custom_duration": "Wait Time (seconds):",
        "label_custom_sleep": "Sleep Lock:",
        "label_custom_task": "Unfinished Task Lock:",
        "opt_remind": "Remind",
        "opt_lock": "Lockscreen",

        # Settings — Games tab
        "add_game_placeholder": "GameName.exe",
        "btn_add": "+ Add",
        "btn_delete": "Delete",
        "btn_save": "Save Changes",
        "btn_save_list": "Save List",
        "msg_saved": "Settings saved successfully!",
        "btn_manage_games": "Manage Game List",
        "placeholder_search_game": "Search game...",
        "title_game_manager": "Game Manager",
        "placeholder_custom_name": "Game Name (e.g. Minecraft)",
        "placeholder_custom_exe": "File name (e.g. javaw.exe)",

        # Settings — Questions tab
        "btn_edit": "Edit",
        "btn_add_question": "+ Add New Question",
        "btn_cancel": "Cancel",
        "question_dialog_title": "Add/Edit Question",
        "question_note": "Groups in 'Checklist' mode require you to tick off items. Other groups pick one question at random.",
        "btn_add_group": "+ Add Group",
        "btn_edit_group": "Edit Group",
        "group_dialog_title": "Group Name",
        "cb_group_enabled": "Enable this group",
        "cb_group_checklist": "Use as Checklist (Instead of random pick)",

        # Settings — Log tab
        "log_col_date": "Date",
        "log_col_game": "Game",
        "log_col_start": "Start Time",
        "log_col_minutes": "Minutes Over",
        "btn_clear_log": "Clear All Logs",
        "log_minutes_suffix": "mins",

        # Settings — Language
        "label_language": "Language",

        # Settings - Theme & Sound
        "label_theme": "Theme",
        "label_primary_color": "Primary Accent Color:",
        "btn_pick_color": "Pick Color",
        "label_sound": "Sound",
        "label_checklist_sound": "Checklist Complete Sound:",
        "label_notif_sound": "Notification Sound:",
        "opt_custom_sound": "Custom...",
        "btn_browse": "Browse...",

        "group_preset_games": "System Games (Preset)",
        "group_custom_games": "Custom Games",
        "btn_move_up": "▲ Up",
        "btn_move_down": "▼ Down",
        "log_chart_title": "Play Time Statistics:",
        "log_range_7": "7 Days",
        "log_range_14": "14 Days",
        "log_range_30": "30 Days",
        "log_legend_valid": "Valid Play Time",
        "log_legend_viol": "Late Night Play (Violation)",
        "lang_vietnamese": "Tiếng Việt",
        "lang_english": "English",

        # Night guard toasts
        "toast_night_report": "Report: You stayed up late playing {game} for about {minutes} minutes. Please take care of your health!",
        "toast_night_remind": "You are playing games during your sleep hours. The system will record this violation.",
        "toast_hardcore_kill": "⚠️ Mindfun has locked your game screen. It's past {time}.\nPlease shut down and go to sleep.",
        "toast_title": "Mindfun",

        # About
        "about_title": "About Mindfun",
        "about_text": (
            "Mindfun v1.0.0\n\n"
            "No bans — just mindful pauses.\n\n"
            "Philosophy: Behavioral Friction — creating just enough\n"
            "friction for reason to awaken before impulse wins.\n\n"
            "Local-only. No data sent over the network.\n"
            "Open Source."
        ),

        # Confirm dialogs
        "confirm_clear_log": "Are you sure you want to clear all logs?",
        "confirm_yes": "Yes",
        "confirm_no": "No",
        "confirm_title": "Confirm",
        "confirm_pause": "Pause Mindfun for today?\nMindfun will automatically resume at 5:00 AM tomorrow.",
        "confirm_disable_ac_title": "Warning",
        "confirm_disable_ac_text": "Are you sure you want to disable Anti-Cheat?\n\nThis removes Mindfun's protection layer, making it easy to give in to impulsive urges.\n\nDo you still want to disable it?",

        # Onboarding
        "onb_lang_title": "Choose Language",
        "onb_lang_desc": "Which language would you like to use for MindFun?",
        "onb_title": "Welcome to MindFun",
        "onb_desc": "This is your first time opening the app.\nWould you like to run the Setup Wizard?",
        "onb_yes": "Yes, guide me",
        "onb_no": "No, let me explore",
        "onb_step1": "Step 1: Choose Commitment Level",
        "onb_step1_desc": "The commitment level determines the system's strictness and your mindfulness time.",
        "onb_step2": "Step 2: Add Games to Manage",
        "onb_step2_desc": "MindFun will block and require a brain workout before launching these games.",
        "onb_add_game": "Select Game File",
        "onb_finish_title": "Setup Complete!",
        "onb_finish_desc": "MindFun is ready to protect your time.\nClick Start to experience it!",
        "onb_btn_next": "Next",
        "onb_btn_back": "Back",
        "onb_btn_start": "Start",
        "onb_btn_skip": "Skip",
        "onb_btn_browse": "Browse (.exe)",
        "onb_mode1_desc": "A few seconds for self-awareness.",
        "onb_mode2_desc": "Longer delay for better mindfulness.",
        "onb_mode3_desc": "Stricter system to enforce self-awareness.",
        "onb_mode4_desc": "Not for those who don't want to quit!",
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
    lang = _current_lang
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
