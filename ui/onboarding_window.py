from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QStackedWidget, QSpacerItem, QSizePolicy, QGraphicsDropShadowEffect,
    QRadioButton, QButtonGroup, QFileDialog, QListWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor

from core.config_manager import load_config, save_config
from core.i18n import t, set_language

class LanguageSlide(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        
        lbl_title = QLabel(t("onb_lang_title"))
        lbl_title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        lbl_title.setStyleSheet("color: #f2b42c;")
        lbl_title.setAlignment(Qt.AlignCenter)
        
        is_dark = window.config.get("dark_mode", True)
        text_color = "#E0E0E0" if is_dark else "#333333"

        lbl_desc = QLabel(t("onb_lang_desc"))
        lbl_desc.setFont(QFont("Segoe UI", 14))
        lbl_desc.setAlignment(Qt.AlignCenter)
        lbl_desc.setStyleSheet(f"color: {text_color};")
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        btn_vi = QPushButton("Tiếng Việt")
        btn_vi.setFixedSize(200, 45)
        btn_vi.setStyleSheet("""
            QPushButton { background: #f2b42c; color: #111; font-size: 14px; font-weight: bold; border-radius: 8px; }
            QPushButton:hover { background: #ffd257; }
        """)
        btn_vi.clicked.connect(lambda: self._set_language("vi"))
        
        btn_en = QPushButton("English")
        btn_en.setFixedSize(200, 45)
        btn_en.setStyleSheet("""
            QPushButton { background: #444; color: #FFF; font-size: 14px; font-weight: bold; border-radius: 8px; }
            QPushButton:hover { background: #555; }
        """)
        btn_en.clicked.connect(lambda: self._set_language("en"))
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_vi)
        btn_layout.addWidget(btn_en)
        btn_layout.addStretch()
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_desc)
        layout.addLayout(btn_layout)
        
    def _set_language(self, lang):
        self.window.config["language"] = lang
        save_config(self.window.config)
        set_language(lang)
        self.window._setup_remaining_slides()
        self.window._next_slide()

class PromptSlide(QWidget):
    def __init__(self, window):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        
        lbl_title = QLabel(t("onb_title"))
        lbl_title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        lbl_title.setStyleSheet("color: #f2b42c;")
        lbl_title.setAlignment(Qt.AlignCenter)
        
        is_dark = window.config.get("dark_mode", True)
        text_color = "#E0E0E0" if is_dark else "#333333"

        lbl_desc = QLabel(t("onb_desc"))
        lbl_desc.setFont(QFont("Segoe UI", 14))
        lbl_desc.setAlignment(Qt.AlignCenter)
        lbl_desc.setStyleSheet(f"color: {text_color};")
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        btn_yes = QPushButton(t("onb_yes"))
        btn_yes.setFixedSize(200, 45)
        btn_yes.setStyleSheet("""
            QPushButton { background: #f2b42c; color: #111; font-size: 14px; font-weight: bold; border-radius: 8px; }
            QPushButton:hover { background: #ffd257; }
        """)
        btn_yes.clicked.connect(window._next_slide)
        
        btn_no = QPushButton(t("onb_no"))
        btn_no.setFixedSize(200, 45)
        btn_no.setStyleSheet("""
            QPushButton { background: #444; color: #FFF; font-size: 14px; font-weight: bold; border-radius: 8px; }
            QPushButton:hover { background: #555; }
        """)
        btn_no.clicked.connect(window._finish)
        
        btn_layout.addStretch()
        btn_layout.addWidget(btn_yes)
        btn_layout.addWidget(btn_no)
        btn_layout.addStretch()
        
        layout.addStretch()
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_desc)
        layout.addLayout(btn_layout)
        layout.addStretch()

class ModeSelectionSlide(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        lbl_title = QLabel(t("onb_step1"))
        lbl_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        lbl_title.setStyleSheet("color: #f2b42c;")
        lbl_title.setWordWrap(True)
        
        is_dark = window.config.get("dark_mode", True)
        text_color = "#E0E0E0" if is_dark else "#333333"

        lbl_desc = QLabel(t("onb_step1_desc"))
        lbl_desc.setFont(QFont("Segoe UI", 12))
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet(f"color: {text_color};")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_desc)
        layout.addSpacing(20)
        
        self.btn_group = QButtonGroup(self)
        modes = [
            (1, t("mode_1_name").split(" (")[0], t("onb_mode1_desc")),
            (2, t("mode_2_name").split(" (")[0], t("onb_mode2_desc")),
            (3, t("mode_3_name").split(" (")[0], t("onb_mode3_desc")),
            (4, t("mode_4_name").split(" (")[0], t("onb_mode4_desc")),
        ]
        
        for val, name, desc in modes:
            rb = QRadioButton(f"{name} - {desc}")
            rb.setFont(QFont("Segoe UI", 12))
            rb.setStyleSheet(f"color: {text_color};")
            self.btn_group.addButton(rb, val)
            layout.addWidget(rb)
            if val == self.window.config.get("mode", 2):
                rb.setChecked(True)
                
        self.btn_group.buttonClicked.connect(self._on_mode_changed)
        layout.addStretch()
        
    def _on_mode_changed(self, btn):
        self.window.config["mode"] = self.btn_group.id(btn)

class AddGameSlide(QWidget):
    def __init__(self, window):
        super().__init__()
        self.window = window
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        lbl_title = QLabel(t("onb_step2"))
        lbl_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        lbl_title.setWordWrap(True)
        is_dark = window.config.get("dark_mode", True)
        text_color = "#E0E0E0" if is_dark else "#333333"

        lbl_title.setStyleSheet("color: #f2b42c;")
        
        lbl_desc = QLabel(t("onb_step2_desc"))
        lbl_desc.setFont(QFont("Segoe UI", 12))
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet(f"color: {text_color};")
        
        self.list_widget = QListWidget()
        self._refresh_list()
        
        btn_add = QPushButton(t("onb_btn_browse"))
        btn_add.setFixedSize(200, 40)
        btn_add.setStyleSheet("background: #f2b42c; color: #111; font-weight: bold; border-radius: 8px;")
        btn_add.clicked.connect(self._add_game)
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_desc)
        layout.addWidget(self.list_widget)
        layout.addWidget(btn_add, alignment=Qt.AlignCenter)
        
    def _refresh_list(self):
        self.list_widget.clear()
        for game in self.window.config.get("game_list", []):
            if isinstance(game, str):
                self.list_widget.addItem(game)
            elif isinstance(game, dict):
                self.list_widget.addItem(game.get("name", "Unknown Game"))
            
    def _add_game(self):
        file_path, _ = QFileDialog.getOpenFileName(self, t("onb_add_game"), "", "Executables (*.exe)")
        if file_path:
            name = os.path.basename(file_path)
            if "game_list" not in self.window.config:
                self.window.config["game_list"] = []
            self.window.config["game_list"].append({"name": name, "path": file_path})
            self._refresh_list()

        
class OnboardingWindow(QWidget):
    on_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.setWindowTitle("MindFun Setup")
        self.setFixedSize(650, 550)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self._setup_ui()
        self._current_index = 0
        self._update_ui()
        
        # Center on screen
        self._center_on_screen()
        
    def _center_on_screen(self):
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
    def _setup_ui(self):
        # Main container for rounded corners and styling
        self.container = QWidget(self)
        self.container.setGeometry(10, 10, self.width()-20, self.height()-20)
        self.container.setStyleSheet("""
            QWidget#MainContainer {
                background-color: #1e1e1e;
                border: 1px solid #333333;
                border-radius: 16px;
            }
        """)
        self.container.setObjectName("MainContainer")
        
        # Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 150))
        self.container.setGraphicsEffect(shadow)
        
        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(30, 40, 30, 30)
        
        # Stacked Widget for slides
        self.stack = QStackedWidget()
        
        self.slide_lang = LanguageSlide(self)
        self.stack.addWidget(self.slide_lang)
        
        # Bottom controls
        bottom_layout = QHBoxLayout()
        
        self.btn_back = QPushButton(t("onb_btn_back"))
        self.btn_back.setCursor(Qt.PointingHandCursor)
        self.btn_back.setFixedSize(100, 40)
        self.btn_back.setStyleSheet("""
            QPushButton { background: transparent; color: #888; border: none; font-size: 14px; font-weight: bold; }
            QPushButton:hover { color: #FFF; }
        """)
        self.btn_back.clicked.connect(self._prev_slide)
        self.btn_back.hide()
        
        self.btn_skip = QPushButton(t("onb_btn_skip"))
        self.btn_skip.setCursor(Qt.PointingHandCursor)
        self.btn_skip.setFixedSize(100, 40)
        self.btn_skip.setStyleSheet("""
            QPushButton { background: transparent; color: #888; font-size: 14px; font-weight: bold; border: none; }
            QPushButton:hover { color: #BBB; }
        """)
        self.btn_skip.clicked.connect(self._finish)
        
        # Dots
        self.dots_layout = QHBoxLayout()
        self.dots_layout.setSpacing(8)
        self.dots_layout.setAlignment(Qt.AlignCenter)
        self.dots = []
        for i in range(self.stack.count()):
            dot = QLabel("●")
            dot.setStyleSheet("color: #555; font-size: 16px;")
            self.dots_layout.addWidget(dot)
            self.dots.append(dot)
            
        self.btn_next = QPushButton(t("onb_btn_next"))
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_next.setFixedSize(120, 40)
        self.btn_next.setStyleSheet("""
            QPushButton { background: #f2b42c; color: #111; font-size: 14px; font-weight: bold; border-radius: 8px; }
            QPushButton:hover { background: #ffd257; }
        """)
        self.btn_next.clicked.connect(self._next_slide)
        
        bottom_layout.addWidget(self.btn_back)
        bottom_layout.addWidget(self.btn_skip)
        bottom_layout.addStretch()
        bottom_layout.addLayout(self.dots_layout)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_next)
        
        main_layout.addWidget(self.stack)
        main_layout.addLayout(bottom_layout)
        
    def _setup_remaining_slides(self):
        # Create other slides after language is selected
        slide_prompt = PromptSlide(self)
        slide_mode = ModeSelectionSlide(self)
        slide_game = AddGameSlide(self)
        
        is_dark = self.config.get("dark_mode", True)
        text_color = "#E0E0E0" if is_dark else "#333333"

        slide_finish = QWidget()
        layout_finish = QVBoxLayout(slide_finish)
        layout_finish.setAlignment(Qt.AlignCenter)
        lbl_finish = QLabel(t("onb_finish_title"))
        lbl_finish.setFont(QFont("Segoe UI", 24, QFont.Bold))
        lbl_finish.setStyleSheet("color: #f2b42c;")
        lbl_desc_finish = QLabel(t("onb_finish_desc"))
        lbl_desc_finish.setFont(QFont("Segoe UI", 14))
        lbl_desc_finish.setAlignment(Qt.AlignCenter)
        lbl_desc_finish.setStyleSheet(f"color: {text_color};")
        layout_finish.addWidget(lbl_finish, alignment=Qt.AlignCenter)
        layout_finish.addWidget(lbl_desc_finish, alignment=Qt.AlignCenter)
        
        self.stack.addWidget(slide_prompt)
        self.stack.addWidget(slide_mode)
        self.stack.addWidget(slide_game)
        self.stack.addWidget(slide_finish)
        
        # Update text of buttons
        self.btn_back.setText(t("onb_btn_back"))
        self.btn_next.setText(t("onb_btn_next"))
        self.btn_skip.setText(t("onb_btn_skip"))
        
        # Refresh dots
        for i in reversed(range(self.dots_layout.count())):
            self.dots_layout.itemAt(i).widget().setParent(None)
        self.dots = []
        for i in range(self.stack.count()):
            dot = QLabel("●")
            dot.setStyleSheet("color: #555; font-size: 16px;")
            self.dots_layout.addWidget(dot)
            self.dots.append(dot)
            
        self._update_ui()
        
    def _update_ui(self):
        self.stack.setCurrentIndex(self._current_index)
        
        # Hide bottom controls completely on Language slide (0) and Prompt slide (1)
        if self._current_index <= 1:
            self.btn_next.hide()
            self.btn_skip.hide()
            self.btn_back.hide()
            for dot in self.dots:
                dot.hide()
            return
            
        self.btn_next.show()
        for dot in self.dots:
            dot.show()
            
        for i, dot in enumerate(self.dots):
            if i == self._current_index:
                dot.setStyleSheet("color: #f2b42c; font-size: 16px;")
            else:
                dot.setStyleSheet("color: #555; font-size: 16px;")
                
        if self._current_index == 2:
            self.btn_back.hide()
        else:
            self.btn_back.show()
                
        if self._current_index == self.stack.count() - 1:
            self.btn_next.setText(t("onb_btn_start"))
            self.btn_skip.hide()
        else:
            self.btn_next.setText(t("onb_btn_next"))
            self.btn_skip.show()
            self.btn_skip.setText(t("onb_btn_skip"))
            
    def _prev_slide(self):
        if self._current_index > 2:
            self._current_index -= 1
            self._update_ui()
            
    def _next_slide(self):
        if self._current_index < self.stack.count() - 1:
            self._current_index += 1
            self._update_ui()
        else:
            self._finish()
            
    def _finish(self):
        # Save to config
        self.config["onboarding_completed"] = True
        save_config(self.config)
        self.on_finished.emit()
        self.close()

    def paintEvent(self, event):
        from PyQt5.QtGui import QPainter, QPainterPath
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 16, 16)
        
        is_dark = self.config.get("dark_mode", True)
        bg_color = QColor(30, 30, 30, 255) if is_dark else QColor(255, 255, 255, 255)
        
        painter.fillPath(path, bg_color)
