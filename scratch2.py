import re

with open("ui/lockscreen.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add _furthest_group_index in __init__
content = content.replace("self._global_elapsed_seconds = 0", "self._global_elapsed_seconds = 0\n        self._furthest_group_index = 0")

# 2. Add _handle_prev method
handle_prev_code = """    def _handle_prev(self):
        \"\"\"Go to the previous group.\"\"\"
        if self._current_group_index > 0:
            self._current_group_index -= 1
            if self._checklist_groups:
                self._stacked_checklists.setCurrentIndex(self._current_group_index)
            
            if self._current_group_index == 0:
                self._btn_prev.hide()
                
            self._btn_next.show()
            self._btn_next.setEnabled(True)
            self._btn_next.setText(t("btn_next") if t("btn_next") != "btn_next" else "Sau")
            
            self._btn_play.hide()
            self._update_play_button()
"""

# Inject before _handle_next
content = content.replace("    def _handle_next(self):", handle_prev_code + "\n    def _handle_next(self):")

# 3. Update _handle_next logic
handle_next_code = """    def _handle_next(self):
        \"\"\"Go to the next group.\"\"\"
        self._current_group_index += 1
        self._furthest_group_index = max(self._furthest_group_index, self._current_group_index)
        n = len(self._checklist_groups)
        
        # Update UI
        if self._checklist_groups:
            self._stacked_checklists.setCurrentIndex(self._current_group_index)
            
        self._btn_prev.show()
        self._btn_prev.setEnabled(True)
        
        if self._current_group_index == self._furthest_group_index:
            self._remaining = self._group_times[self._current_group_index]
            self._countdown_active = (self._remaining > 0)
        else:
            self._remaining = 0
            self._countdown_active = False
            
        self._progress.setValue(self._total_seconds - self._global_elapsed_seconds)
        
        self._btn_quit.setEnabled(True)
        self._btn_next.setEnabled(not self._countdown_active)
        self._btn_play.setEnabled(not self._countdown_active)
        
        if self._current_group_index == n - 1:
            self._btn_next.hide()
            self._btn_play.show()
            self._update_play_button()
        else:
            self._btn_next.setText(t("btn_next") if t("btn_next") != "btn_next" else "Sau")
            
        # Update bubble text
        total_left = max(0, self._total_seconds - self._global_elapsed_seconds)
        self._countdown_label.setText(f"{total_left}s\\n\\n{t('waiting_prompt')}")"""

# Replace the whole _handle_next
start_idx = content.find("    def _handle_next(self):")
end_idx = content.find("    def _handle_play(self):")
content = content[:start_idx] + handle_next_code + "\n\n" + content[end_idx:]

# 4. Connect btn_prev
content = content.replace("self._btn_prev.hide() # Initially hidden", "self._btn_prev.hide()\n        self._btn_prev.clicked.connect(self._handle_prev)")

# 5. Update _tick() to show total in bubble and remaining in btn_next
tick_code = """    def _tick(self):
        \"\"\"Update countdown and check state.\"\"\"
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
                    self._btn_next.setText(t("btn_next") if t("btn_next") != "btn_next" else "Sau")
                else:
                    self._update_play_button()
                    
                self._countdown_label.setText(f"{total_left}s\\n\\n{t('waiting_prompt')}")
                import logging
                logging.getLogger(__name__).info("Countdown finished for current group — buttons enabled")
            else:
                self._countdown_label.setText(f"{total_left}s\\n\\n{t('waiting_prompt')}")
                
                # Update button text with remaining group time
                n = len(self._checklist_groups)
                if n > 1 and self._current_group_index < n - 1:
                    btn_text = t("btn_next") if t("btn_next") != "btn_next" else "Sau"
                    self._btn_next.setText(f"{btn_text} ({self._remaining}s)")
                else:
                    self._btn_play.setText(f"{t('btn_play')} ({self._remaining}s)")
            
            self._progress.setValue(self._total_seconds - self._global_elapsed_seconds)
"""

start_idx = content.find("    def _tick(self):")
end_idx = content.find("    def _get_game_hwnds(self) -> list:")

content = content[:start_idx] + tick_code + "\n" + content[end_idx:]

with open("ui/lockscreen.py", "w", encoding="utf-8") as f:
    f.write(content)
