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
        
        self.setFixedSize(60, 60)
        self._drag_pos = None
        self._is_first_show = True
        self._is_hovered = False
        self._has_dragged = False
        
        # Load icon if available
        self._icon_pixmap = None
        if self._icon_path:
            from PyQt5.QtGui import QPixmap
            pix = QPixmap(self._icon_path)
            if not pix.isNull():
                self._icon_pixmap = pix.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
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
        
    def showEvent(self, event):
        if self._is_first_show:
            screen = QApplication.primaryScreen().availableGeometry()
            # Default position: Bottom Right
            x = screen.width() - self.width() - 40
            y = screen.height() - self.height() - 80
            self.move(x, y)
            self._is_first_show = False
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
        """Draw a custom green circular background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw the green circle
        if self._is_hovered:
            painter.setBrush(QColor("#00E676")) # Brighter green when hovered
        else:
            painter.setBrush(QColor("#00C853")) # Normal green
            
        painter.setPen(Qt.NoPen)
        # Slightly larger if hovered
        margin = 3 if self._is_hovered else 5
        size = 54 if self._is_hovered else 50
        painter.drawEllipse(margin, margin, size, size)
        
        # Draw a little text or icon inside the circle
        if self._icon_pixmap:
            # Draw the pixmap centered
            x = (self.width() - self._icon_pixmap.width()) // 2
            y = (self.height() - self._icon_pixmap.height()) // 2
            painter.drawPixmap(x, y, self._icon_pixmap)
        else:
            painter.setPen(QColor("#FFFFFF"))
            font = QFont("Segoe UI", 12, QFont.Bold)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignCenter, "MF")
        
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
