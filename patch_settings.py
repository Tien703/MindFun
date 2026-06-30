import re

with open('ui/settings_window.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove UI setup
ui_setup_pattern = r'        # Primary Color Picker.*?\n        theme_layout\.addLayout\(color_layout\)\n'
content = re.sub(ui_setup_pattern, '', content, flags=re.DOTALL)

# 2. Remove _pick_primary_color method
method_pattern = r'    def _pick_primary_color\(self\):\n(?:        .*?\n)+\n'
content = re.sub(method_pattern, '\n', content, flags=re.DOTALL)

# 3. Remove save logic
save_str = """        if theme_cfg.get("primary_accent") != self._current_primary_color:
            theme_cfg["primary_accent"] = self._current_primary_color
            needs_restart = True
            
"""
content = content.replace(save_str, '')

with open('ui/settings_window.py', 'w', encoding='utf-8') as f:
    f.write(content)
