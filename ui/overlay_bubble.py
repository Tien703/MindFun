import logging
from PyQt5.QtWidgets import QWidget, QLabel, QApplication, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QMouseEvent, QFont

logger = logging.getLogger("mindfun.chat_head")

class OverlayBubble(QWidget):
    """
    A draggable, topmost floating circular chat bubble (Chat Head).
    Displays messages as a side pop-up when triggered.
    """
    on_double_click = pyqtSignal()
    on_single_click = pyqtSignal()
    on_right_click = pyqtSignal(QPoint)
    
    def __init__(self, icon_path: str = None, parent=None):
        super().__init__(parent)
        self._icon_path = icon_path
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setFixedSize(120, 120)
        self._drag_pos = None
        self._is_first_show = True
        self._is_hovered = False
        self._has_dragged = False
        
        self._full_opacity = 0.0
        self._is_angry = False
        
        import os
        from PyQt5.QtGui import QPixmap
        from core.utils import get_resource_path
        base_dir = get_resource_path("assets/sprites")
        def load_sprite(name):
            pix = QPixmap(os.path.join(base_dir, name))
            if not pix.isNull():
                return pix.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            return None
            
        self._pix_empty = load_sprite("meditation empty.png")
        self._pix_full = load_sprite("meditation full ball.png")
        self._pix_angry = load_sprite("aangry ball.png")
        
        self._fade_timer = QTimer(self)
        self._fade_timer.timeout.connect(self._update_fade)
        
        self._night_timer = QTimer(self)
        self._night_timer.timeout.connect(self._check_night_time)
        self._night_timer.start(10000)
        
        # The message popup widget
        self.popup = QLabel()
        self.popup.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.X11BypassWindowManagerHint
        )
        self.popup.setAttribute(Qt.WA_TranslucentBackground)
        self.popup.setStyleSheet("""
            QLabel {
                background-color: rgba(30, 30, 30, 240);
                color: #FFFFFF;
                border: 1px solid #555;
                border-radius: 12px;
                padding: 12px 16px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
        """)
        self.popup.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Auto-hide timer for the popup message
        self._auto_hide_timer = QTimer(self)
        self._auto_hide_timer.setSingleShot(True)
        self._auto_hide_timer.timeout.connect(self.hide_message)
        
    def _update_fade(self):
        self._full_opacity += 0.02
        if self._full_opacity >= 1.0:
            self._full_opacity = 1.0
            self._fade_timer.stop()
        self.update()
        
    def _check_night_time(self):
        from core.night_guard import is_night_time
        is_angry = is_night_time()
        if self._is_angry != is_angry:
            self._is_angry = is_angry
            self.update()

    def showEvent(self, event):
        if self._is_first_show:
            screen = QApplication.primaryScreen().availableGeometry()
            # Default position: Bottom Right
            x = screen.width() - self.width() - 40
            y = screen.height() - self.height() - 80
            self.move(x, y)
            self._is_first_show = False
            QTimer.singleShot(1000, lambda: self._fade_timer.start(50))
            
        self._check_night_time()
        super().showEvent(event)
        
    def show_message(self, text: str, duration_ms: int = 15000):
        """Show the message popup next to the chat head."""
        self.popup.setText(text)
        self.popup.adjustSize()
        
        # Position popup to the left of the chat head
        pos = self.pos()
        # If there's no space on the left, show it on the right
        x_pos = pos.x() - self.popup.width() - 10
        if x_pos < 0:
            x_pos = pos.x() + self.width() + 10
            
        y_pos = pos.y() + (self.height() - self.popup.height()) // 2
        
        self.popup.move(x_pos, y_pos)
        self.popup.show()
        
        if duration_ms > 0:
            self._auto_hide_timer.start(duration_ms)
            
    def hide_message(self):
        """Hide the popup message."""
        self.popup.hide()
        
    def hideEvent(self, event):
        self.hide_message()
        super().hideEvent(event)
        
    def enterEvent(self, event):
        self._is_hovered = True
        self.update()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._is_hovered = False
        self.update()
        super().leaveEvent(event)
            
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self._is_angry and self._pix_angry:
            x = (self.width() - self._pix_angry.width()) // 2
            y = (self.height() - self._pix_angry.height()) // 2
            painter.drawPixmap(x, y, self._pix_angry)
        else:
            if self._pix_empty:
                painter.setOpacity(1.0 - self._full_opacity)
                x = (self.width() - self._pix_empty.width()) // 2
                y = (self.height() - self._pix_empty.height()) // 2
                painter.drawPixmap(x, y, self._pix_empty)
                
            if self._pix_full and self._full_opacity > 0:
                painter.setOpacity(self._full_opacity)
                x = (self.width() - self._pix_full.width()) // 2
                y = (self.height() - self._pix_full.height()) // 2
                painter.drawPixmap(x, y, self._pix_full)
        
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            self._has_dragged = False
            event.accept()
        elif event.button() == Qt.RightButton:
            self.on_right_click.emit(event.globalPos())
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton and self._drag_pos is not None:
            # Check if actually dragged
            if (event.globalPos() - self.frameGeometry().topLeft() - self._drag_pos).manhattanLength() > 3:
                self._has_dragged = True
                
            self.move(event.globalPos() - self._drag_pos)
            # Move the popup along with the chat head if it's visible
            if self.popup.isVisible():
                pos = self.pos()
                x_pos = pos.x() - self.popup.width() - 10
                if x_pos < 0:
                    x_pos = pos.x() + self.width() + 10
                y_pos = pos.y() + (self.height() - self.popup.height()) // 2
                self.popup.move(x_pos, y_pos)
            event.accept()
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            if not self._has_dragged:
                self.on_single_click.emit()
            self._drag_pos = None
        event.accept()
        
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Double click to emit signal or hide message."""
        if event.button() == Qt.LeftButton:
            if self.popup.isVisible():
                self.hide_message()
            else:
                self.on_double_click.emit()
            event.accept()

