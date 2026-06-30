"""
Mindfun — Theme Manager

Centralizes CSS for Light and Dark themes, using a modern Windows 11 style.
Accent colors: 
- Primary/Active: #f2b42c (Yellow-Orange)
- Danger/Quit: #fe413c (Red)
- Success/Save: #b6f36d (Lime Green)
"""

def get_settings_style(is_dark: bool) -> str:
    from core.config_manager import load_config
    theme_cfg = load_config().get("theme", {})
    
    if is_dark:
        # Dark Mode
        bg_window = theme_cfg.get("bg_dark", "#202020")
        bg_card = theme_cfg.get("card_dark", "#2D2D2D")
        border_color = "#3E3E3E"
        text_primary = "#FFFFFF"
        text_secondary = "#A0A0A0"
        accent_primary = theme_cfg.get("primary_accent", "#f2b42c")
        accent_success = theme_cfg.get("success_accent", "#b6f36d")
        accent_danger = theme_cfg.get("danger_accent", "#fe413c")
        bg_hover = "#3E3E3E"
    else:
        # Light Mode
        bg_window = theme_cfg.get("bg_light", "#F3F3F3")
        bg_card = theme_cfg.get("card_light", "#FFFFFF")
        border_color = "#E5E5E5"
        text_primary = "#111111"
        text_secondary = "#5F5F5F"
        accent_primary = theme_cfg.get("primary_accent", "#f2b42c")
        accent_success = theme_cfg.get("success_accent", "#b6f36d")
        accent_danger = theme_cfg.get("danger_accent", "#fe413c")
        bg_hover = "#F6F6F6"
        
    accent_success_hover = accent_success # simplify


    return f"""
        QWidget {{ background-color: {bg_window}; color: {text_primary}; font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 14px; }}
        
        QTabWidget::pane {{ border: 1px solid {border_color}; background-color: {bg_card}; border-radius: 8px; padding: 16px; }}
        QTabBar::tab {{ background: {bg_window}; color: {text_secondary}; padding: 8px 20px; border: 1px solid transparent; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 4px; font-weight: bold; min-height: 24px; }}
        QTabBar::tab:selected {{ background: {bg_card}; color: {text_primary}; border: 1px solid {border_color}; border-bottom-color: {bg_card}; font-weight: bold; }}
        QTabBar::tab:hover:!selected {{ background: {bg_hover}; color: {text_primary}; }}
        
        QPushButton {{ background-color: {bg_card}; color: {text_primary}; border: 1px solid {border_color}; border-radius: 6px; padding: 8px 24px; font-weight: 600; }}
        QPushButton:hover {{ background-color: {bg_hover}; }}
        QPushButton:pressed {{ background-color: {border_color}; }}
        
        QPushButton#btn_save_primary {{ background-color: {accent_success}; border: none; color: #111111; }}
        QPushButton#btn_save_primary:hover {{ background-color: {accent_success_hover}; }}
        
        QPushButton#btn_danger {{ background-color: {accent_danger}; border: none; color: #FFFFFF; }}
        QPushButton#btn_danger:hover {{ background-color: #e63935; }}
        
        QRadioButton {{ color: {text_primary}; spacing: 8px; font-size: 14px; min-height: 32px; padding: 2px 0; }}
        QRadioButton::indicator {{ width: 18px; height: 18px; }}
        QCheckBox {{ color: {text_primary}; spacing: 8px; font-size: 14px; min-height: 32px; padding: 2px 0; }}
        QCheckBox::indicator {{ width: 18px; height: 18px; }}
        
        QSpinBox {{ background-color: {bg_card}; color: {text_primary}; border: 1px solid {border_color}; border-radius: 6px; padding: 4px 12px; min-height: 32px; }}
        QLineEdit {{ background-color: {bg_card}; color: {text_primary}; border: 1px solid {border_color}; border-radius: 6px; padding: 4px 12px; min-height: 32px; }}
        QLineEdit:focus {{ border: 2px solid {accent_primary}; padding: 7px 11px; }}
        
        QListWidget {{ background-color: {bg_card}; color: {text_primary}; border: 1px solid {border_color}; border-radius: 6px; padding: 4px; outline: none; }}
        QListWidget::item {{ padding: 8px 12px; border-radius: 4px; margin-bottom: 2px; }}
        QListWidget::item:selected {{ background-color: {accent_primary}; color: #111111; font-weight: bold; }}
        QListWidget::item:hover:!selected {{ background-color: {bg_hover}; }}
        
        QTableWidget {{ background-color: {bg_card}; color: {text_primary}; border: 1px solid {border_color}; border-radius: 6px; gridline-color: {border_color}; outline: none; }}
        QTableWidget::item {{ padding: 6px; }}
        QHeaderView::section {{ background-color: {bg_window}; color: {text_secondary}; padding: 8px; border: none; border-bottom: 1px solid {border_color}; font-weight: 600; text-align: left; }}
        
        QComboBox {{ background-color: {bg_card}; color: {text_primary}; border: 1px solid {border_color}; border-radius: 6px; padding: 4px 12px; min-height: 32px; }}
        QComboBox::drop-down {{ border: none; width: 24px; }}
        QComboBox QAbstractItemView {{ background-color: {bg_card}; color: {text_primary}; border: 1px solid {border_color}; border-radius: 6px; selection-background-color: {bg_hover}; selection-color: {text_primary}; outline: none; }}
        
        QGroupBox {{ color: {text_primary}; border: 1px solid {border_color}; border-radius: 8px; margin-top: 28px; padding-top: 16px; font-weight: 600; font-size: 14px; }}
        QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; left: 16px; top: 0px; padding: 0px; background-color: transparent; }}
        
        QScrollArea {{ background-color: transparent; border: none; }}
        QScrollArea > QWidget > QWidget {{ background-color: transparent; }}
        
        QScrollBar:vertical {{ border: none; background: transparent; width: 8px; margin: 0px; }}
        QScrollBar::handle:vertical {{ background: {border_color}; min-height: 20px; border-radius: 4px; }}
        QScrollBar::handle:vertical:hover {{ background: {text_secondary}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ border: none; background: none; height: 0px; }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
        
        QScrollBar:horizontal {{ border: none; background: transparent; height: 8px; margin: 0px; }}
        QScrollBar::handle:horizontal {{ background: {border_color}; min-width: 20px; border-radius: 4px; }}
        QScrollBar::handle:horizontal:hover {{ background: {text_secondary}; }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ border: none; background: none; width: 0px; }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}
        
        QFrame#separator {{ background-color: {border_color}; max-height: 1px; }}
    """

def get_lockscreen_style(is_dark: bool) -> str:
    from core.config_manager import load_config
    theme_cfg = load_config().get("theme", {})
    
    accent_primary = theme_cfg.get("primary_accent", "#f2b42c")
    accent_success = theme_cfg.get("success_accent", "#b6f36d")
    
    if is_dark:
        bg_card = theme_cfg.get("card_dark", "#2D2D2D")
        border_color = "#3E3E3E"
        text_primary = "#FFFFFF"
        text_secondary = "#A0A0A0"
        bg_hover = "#2D2D2D"
    else:
        bg_card = theme_cfg.get("card_light", "#FFFFFF")
        border_color = "#E5E5E5"
        text_primary = "#111111"
        text_secondary = "#5F5F5F"
        bg_hover = "#F6F6F6"

    return f"""
        #lockscreen_content {{
            background-color: {bg_card};
            border-radius: 12px;
            border: 1px solid {border_color};
        }}
        #game_label {{
            color: {text_primary};
            font-size: 36px;
            font-weight: bold;
            font-family: 'Segoe UI', 'Inter', sans-serif;
            padding: 24px;
        }}
        #countdown_progress {{
            background-color: {border_color};
            border: none;
            border-radius: 4px;
        }}
        #countdown_progress::chunk {{
            background-color: {accent_primary};
            border-radius: 4px;
        }}
        #countdown_label {{
            color: {text_secondary};
            font-size: 20px;
            font-family: 'Segoe UI', 'Inter', sans-serif;
            font-weight: 600;
        }}
        #question_label {{
            color: {text_primary};
            font-size: 26px;
            font-family: 'Segoe UI', 'Inter', sans-serif;
            padding: 10px 60px;
            line-height: 1.5;
        }}
        #task_checkbox {{
            color: {text_primary};
            font-size: 22px;
            font-family: 'Segoe UI', 'Inter', sans-serif;
        }}
        #task_checkbox::indicator {{
            width: 32px;
            height: 32px;
            border-radius: 8px;
            border: 2px solid {border_color};
            background-color: {bg_card};
        }}
        #task_checkbox::indicator:checked {{
            background-color: {accent_success};
            border-color: {accent_success};
            image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%23111111" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>');
        }}
        #task_checkbox:disabled {{
            color: {text_secondary};
        }}
        #btn_quit {{
            background-color: {bg_card};
            color: {accent_success};
            font-size: 18px;
            font-weight: bold;
            font-family: 'Segoe UI', 'Inter', sans-serif;
            border: 2px solid {accent_success};
            border-radius: 8px;
            padding: 16px 36px;
        }}
        #btn_quit:hover {{
            background-color: {accent_success};
            color: #111111;
        }}
        #btn_quit:disabled {{
            background-color: {bg_card};
            color: {text_secondary};
            border-color: {border_color};
        }}
        #btn_play {{
            background-color: {accent_primary};
            color: #111111;
            font-size: 18px;
            font-weight: bold;
            font-family: 'Segoe UI', 'Inter', sans-serif;
            border: none;
            border-radius: 8px;
            padding: 18px 38px;
        }}
        #btn_play:hover {{
            background-color: #d99a1c;
        }}
        #btn_play:disabled {{
            background-color: {bg_hover};
            color: {text_secondary};
        }}
        
        QScrollArea {{ background-color: transparent; border: none; }}
        QScrollArea > QWidget > QWidget {{ background-color: transparent; }}
        
        QScrollBar:vertical {{ border: none; background: transparent; width: 8px; margin: 0px; }}
        QScrollBar::handle:vertical {{ background: {border_color}; min-height: 20px; border-radius: 4px; }}
        QScrollBar::handle:vertical:hover {{ background: {text_secondary}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ border: none; background: none; height: 0px; }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
        
        QScrollBar:horizontal {{ border: none; background: transparent; height: 8px; margin: 0px; }}
        QScrollBar::handle:horizontal {{ background: {border_color}; min-width: 20px; border-radius: 4px; }}
        QScrollBar::handle:horizontal:hover {{ background: {text_secondary}; }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ border: none; background: none; width: 0px; }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: none; }}
    """

def get_tray_style(is_dark: bool) -> str:
    from core.config_manager import load_config
    theme_cfg = load_config().get("theme", {})
    
    if is_dark:
        bg_menu = theme_cfg.get("card_dark", "#2D2D2D")
        return f"""
            QMenu {{
                background-color: {bg_menu};
                color: #FFFFFF;
                border: 1px solid #3E3E3E;
                border-radius: 8px;
                padding: 6px 0;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 14px;
            }}
            QMenu::item {{ padding: 8px 32px 8px 24px; }}
            QMenu::item:selected {{ background-color: #3E3E3E; }}
            QMenu::item:disabled {{ color: #A0A0A0; }}
            QMenu::separator {{ height: 1px; background-color: #3E3E3E; margin: 4px 12px; }}
        """
    else:
        bg_menu = theme_cfg.get("card_light", "#FFFFFF")
        return f"""
            QMenu {{
                background-color: {bg_menu};
                color: #111111;
                border: 1px solid #E5E5E5;
                border-radius: 8px;
                padding: 6px 0;
                font-family: 'Segoe UI', 'Inter', sans-serif;
                font-size: 14px;
            }}
            QMenu::item {{ padding: 8px 32px 8px 24px; }}
            QMenu::item:selected {{ background-color: #F6F6F6; }}
            QMenu::item:disabled {{ color: #5F5F5F; }}
            QMenu::separator {{ height: 1px; background-color: #E5E5E5; margin: 4px 12px; }}
        """

def get_chart_colors(is_dark: bool) -> dict:
    from core.config_manager import load_config
    theme_cfg = load_config().get("theme", {})
    
    accent_danger = theme_cfg.get("danger_accent", "#fe413c")
    accent_success = theme_cfg.get("success_accent", "#b6f36d")
    
    if is_dark:
        return {
            "axes": "#A0A0A0",
            "text": "#FFFFFF",
            "grid": "#3E3E3E",
            "valid": accent_success,
            "violation": accent_danger,
        }
    else:
        return {
            "axes": "#5F5F5F",
            "text": "#111111",
            "grid": "#E5E5E5",
            "valid": accent_success,
            "violation": accent_danger,
        }

def get_settings_palette(is_dark: bool) -> dict:
    from core.config_manager import load_config
    theme_cfg = load_config().get("theme", {})
    
    if is_dark:
        return {
            "desc_color": "#A0A0A0",
            "desc_bg": theme_cfg.get("card_dark", "#2D2D2D"),
            "text_color": "#FFFFFF"
        }
    else:
        return {
            "desc_color": "#5F5F5F",
            "desc_bg": theme_cfg.get("card_light", "#FFFFFF"),
            "text_color": "#111111"
        }

def apply_window_titlebar_color(hwnd, is_dark: bool):
    try:
        import ctypes
        DWMWA_CAPTION_COLOR = 35
        # COLORREF format is 0x00bbggrr
        if is_dark:
            color = 0x00202020
        else:
            color = 0x00F3F3F3
            
        value = ctypes.c_int(color)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            int(hwnd), DWMWA_CAPTION_COLOR, ctypes.byref(value), ctypes.sizeof(value)
        )
        
        # Text color (Immersive dark mode toggle)
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        dark_mode_val = ctypes.c_int(1 if is_dark else 0)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            int(hwnd), DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(dark_mode_val), ctypes.sizeof(dark_mode_val)
        )
    except Exception:
        pass
