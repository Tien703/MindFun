import re

with open("ui/lockscreen.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add _was_red
content = content.replace("self._furthest_group_index = 0", "self._furthest_group_index = 0\n        self._was_red = False")

# 2. Remove _warning_label from _setup_ui
content = re.sub(r'# Warning label\s*self\._warning_label.*?\s*right_pane\.addWidget\(self\._warning_label\)', '', content, flags=re.DOTALL)

# Also remove from _update_play_button
content = re.sub(r'if has_unfinished and can_play_time and not is_blocked:.*?self\._warning_label\.hide\(\)', '', content, flags=re.DOTALL)
content = content.replace("self._warning_label.hide()", "") # Catch any stragglers in setup_ui

# 3. Insert _update_character_state
new_method = """    def _update_character_state(self):
        total_left = max(0, self._total_seconds - self._global_elapsed_seconds)
        
        is_red = False
        bubble_message = t("waiting_prompt")
        
        on_last_screen = (self._current_group_index == len(self._checklist_groups) - 1) if self._checklist_groups else True
        
        if self._is_sleep_lock:
            is_red = True
            if self._is_soft_sleep_lock:
                bubble_message = t("soft_sleep_lock_warning") if t("soft_sleep_lock_warning") != "soft_sleep_lock_warning" else "Đã muộn rồi, bạn nên đi ngủ sớm!"
            else:
                bubble_message = t("sleep_lock_warning") if t("sleep_lock_warning") != "sleep_lock_warning" else "Đã quá giờ đi ngủ! Hãy tắt máy và nghỉ ngơi."
        else:
            if on_last_screen and self._has_unfinished_tasks():
                is_red = True
                if self._check_strict_block():
                    bubble_message = "Bạn còn công việc BẮT BUỘC chưa xong!"
                else:
                    bubble_message = "Bạn còn công việc chưa xong"
            else:
                bubble_message = t("waiting_prompt") if t("waiting_prompt") != "waiting_prompt" else "Hãy chậm lại và hít thở"
                
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
            time_text = f"Thời gian tĩnh tâm: {total_left}s\\n\\n"
        else:
            time_text = ""
            
        self._countdown_label.setText(f"{time_text}{bubble_message}")
"""
content = content.replace("    def _tick(self):", new_method + "\n    def _tick(self):")

# 4. Modify _tick to use the new method
tick_pattern = r'self\._countdown_label\.setText\(f"\{total_left\}s\\n\\n\{t\(\'waiting_prompt\'\)\}"\)'
content = re.sub(tick_pattern, 'self._update_character_state()', content)

# 5. Call _update_character_state in _on_task_checked
content = content.replace("self._update_play_button()", "self._update_play_button()\n        self._update_character_state()")

# 6. Call _update_character_state in _setup_ui initially
content = content.replace("self._apply_styles()", "self._update_character_state()\n        self._apply_styles()")

# Remove old bubble text setting in _setup_ui
content = content.replace('self._countdown_label.setText(f"{self._remaining}s\\n\\n{t(\'waiting_prompt\')}")', '')

with open("ui/lockscreen.py", "w", encoding="utf-8") as f:
    f.write(content)
