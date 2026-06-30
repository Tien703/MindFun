import re

with open("core/i18n.py", "r", encoding="utf-8") as f:
    content = f.read()

# Update VI dictionary
vi_additions = """
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
        "time_meditation": "Thời gian tĩnh tâm: {total_left}s\\n\\n",
        "strict_task_block": "Bạn còn công việc BẮT BUỘC chưa xong!",
        "soft_task_block": "Bạn còn công việc chưa xong",
"""
content = content.replace('        "btn_quit": "THOÁT",', vi_additions + '        "btn_quit": "THOÁT",')
content = content.replace('"btn_next": "Tiếp tục",', '"btn_next": "Sau",')
content = content.replace('"sleep_lock_warning": "Đã quá giờ đi ngủ. Hãy tắt {game} để bảo vệ sức khỏe!",', '"sleep_lock_warning": "Đã quá giờ đi ngủ! Hãy tắt máy và nghỉ ngơi.",')
content = content.replace('"soft_sleep_lock_warning": "Đã đến giờ đi ngủ. Bạn có chắc chắn muốn tiếp tục chơi {game}?",', '"soft_sleep_lock_warning": "Đã muộn rồi, bạn nên đi ngủ sớm!",')

# Update EN dictionary
en_additions = """
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
        "time_meditation": "Mindfulness time: {total_left}s\\n\\n",
        "strict_task_block": "You have MANDATORY tasks unfinished!",
        "soft_task_block": "You have unfinished tasks",
"""
content = content.replace('        "btn_quit": "QUIT",', en_additions + '        "btn_quit": "QUIT",')
content = content.replace('"sleep_lock_warning": "It\'s past your bedtime. Please close {game} and go to sleep!",', '"sleep_lock_warning": "It\'s past your bedtime! Please shut down and rest.",')
content = content.replace('"soft_sleep_lock_warning": "It\'s past your bedtime. Are you sure you want to continue playing {game}?",', '"soft_sleep_lock_warning": "It\'s getting late, you should sleep early!",')

with open("core/i18n.py", "w", encoding="utf-8") as f:
    f.write(content)

# Update lockscreen.py
with open("ui/lockscreen.py", "r", encoding="utf-8") as f:
    l_content = f.read()

l_content = l_content.replace('self._btn_prev = QPushButton("Trước")', 'self._btn_prev = QPushButton(t("btn_prev"))')
l_content = l_content.replace('self._btn_next.setText(t("btn_next") if t("btn_next") != "btn_next" else "Sau")', 'self._btn_next.setText(t("btn_next"))')
l_content = l_content.replace('btn_text = t("btn_next") if t("btn_next") != "btn_next" else "Sau"', 'btn_text = t("btn_next")')

l_content = l_content.replace('bubble_message = t("soft_sleep_lock_warning") if t("soft_sleep_lock_warning") != "soft_sleep_lock_warning" else "Đã muộn rồi, bạn nên đi ngủ sớm!"', 'bubble_message = t("soft_sleep_lock_warning")')
l_content = l_content.replace('bubble_message = t("sleep_lock_warning") if t("sleep_lock_warning") != "sleep_lock_warning" else "Đã quá giờ đi ngủ! Hãy tắt máy và nghỉ ngơi."', 'bubble_message = t("sleep_lock_warning")')
l_content = l_content.replace('bubble_message = "Bạn còn công việc BẮT BUỘC chưa xong!"', 'bubble_message = t("strict_task_block")')
l_content = l_content.replace('bubble_message = "Bạn còn công việc chưa xong"', 'bubble_message = t("soft_task_block")')
l_content = l_content.replace('bubble_message = t("waiting_prompt") if t("waiting_prompt") != "waiting_prompt" else "Hãy chậm lại và hít thở"', 'bubble_message = t("waiting_prompt")')
l_content = l_content.replace('time_text = f"Thời gian tĩnh tâm: {total_left}s\\n\\n"', 'time_text = t("time_meditation", total_left=total_left)')

with open("ui/lockscreen.py", "w", encoding="utf-8") as f:
    f.write(l_content)

# Update game_manager_window.py
with open("ui/game_manager_window.py", "r", encoding="utf-8") as f:
    g_content = f.read()

g_content = g_content.replace('QPushButton("Chọn tất cả")', 'QPushButton(t("btn_select_all"))')
g_content = g_content.replace('QPushButton("Bỏ chọn tất cả")', 'QPushButton(t("btn_deselect_all"))')
g_content = g_content.replace('QPushButton("🔍 Quét Game")', 'QPushButton(t("btn_scan_games"))')
g_content = g_content.replace('QLabel("Đã chọn: 0 game")', 'QLabel(t("lbl_selected_zero"))')
g_content = g_content.replace('QMessageBox.warning(self, t("title_game_manager"), "Game này đã có trong danh sách Custom Games!")', 'QMessageBox.warning(self, t("title_game_manager"), t("msg_game_exists"))')
g_content = g_content.replace('self._lbl_counter.setText(f"Đã chọn: {count} / {total} game")', 'self._lbl_counter.setText(t("lbl_selected_count", count=count, total=total))')
g_content = g_content.replace('QMessageBox.information(self, "Auto Scan", "Không tìm thấy game nào trong các thư mục mặc định (Steam, Riot, Epic).")', 'QMessageBox.information(self, t("title_auto_scan"), t("msg_scan_no_games"))')
g_content = g_content.replace('QMessageBox.information(self, "Auto Scan", f"Đã quét và thêm {added} game mới vào danh sách Custom.")', 'QMessageBox.information(self, t("title_auto_scan"), t("msg_scan_added", added=added))')

with open("ui/game_manager_window.py", "w", encoding="utf-8") as f:
    f.write(g_content)

# Update onboarding_window.py
with open("ui/onboarding_window.py", "r", encoding="utf-8") as f:
    o_content = f.read()

o_content = o_content.replace('btn_vi = QPushButton("Tiếng Việt")', 'btn_vi = QPushButton(t("lang_vietnamese"))')

with open("ui/onboarding_window.py", "w", encoding="utf-8") as f:
    f.write(o_content)

# Update quit_popup.py
with open("ui/quit_popup.py", "r", encoding="utf-8") as f:
    q_content = f.read()

q_content = q_content.replace('text = f"Vui lòng tắt {friendly_name} để hoàn tất."', 'text = t("msg_please_close_game", friendly_name=friendly_name)')

with open("ui/quit_popup.py", "w", encoding="utf-8") as f:
    f.write(q_content)
