import sys
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics, QPainterPath
from PyQt5.QtCore import Qt, QRectF

class CircularProgress(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.max_value = 100
        self.width_line = 12
        self.color_track = QColor("#3E3E3E")
        self.color_fill = QColor("#f2b42c")
        self.text = ""
        self.text_color = QColor("#FFFFFF")
        
    def setValue(self, val):
        self.value = val
        self.update()
        
    def setMaxValue(self, val):
        self.max_value = val
        self.update()
        
    def setColors(self, track: str, fill: str, text: str):
        self.color_track = QColor(track)
        self.color_fill = QColor(fill)
        self.text_color = QColor(text)
        self.update()
        
    def setText(self, txt):
        self.text = txt
        self.update()
        
    def paintEvent(self, event):
        width = self.width()
        height = self.height()
        
        # Determine the size of the square area to draw the circle
        size = min(width, height)
        margin = self.width_line
        rect = QRectF(
            (width - size) / 2 + margin,
            (height - size) / 2 + margin,
            size - margin * 2,
            size - margin * 2
        )
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw track
        pen_track = QPen()
        pen_track.setColor(self.color_track)
        pen_track.setWidth(self.width_line)
        pen_track.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_track)
        painter.drawArc(rect, 0, 360 * 16)
        
        # Draw fill
        pen_fill = QPen()
        pen_fill.setColor(self.color_fill)
        pen_fill.setWidth(self.width_line)
        pen_fill.setCapStyle(Qt.RoundCap)
        painter.setPen(pen_fill)
        
        # 0 degrees is 3 o'clock, start at 12 o'clock
        start_angle = 90 * 16
        if self.max_value > 0:
            span_angle = int((self.value / self.max_value) * 360 * 16)
        else:
            span_angle = 0
            
        # Draw clockwise from 12 o'clock
        painter.drawArc(rect, start_angle, -span_angle)
        
        # Draw text inside
        painter.setPen(self.text_color)
        font = self.font()
        font.setBold(True)
        # Main text (seconds)
        font.setPointSize(max(10, int(size / 12)))
        painter.setFont(font)
        
        parts = self.text.split("\n\n")
        if len(parts) == 2:
            main_text, sub_text = parts
            
            # Draw main text
            main_rect = QRectF(rect.x(), rect.y() + rect.height()/2 - size/6 - 20, rect.width(), size/3)
            painter.drawText(main_rect, Qt.AlignCenter, main_text)
            
            # Draw sub text
            font.setPointSize(max(8, int(size / 24)))
            font.setBold(False)
            painter.setFont(font)
            
            sub_rect = QRectF(rect.x() + 20, rect.y() + rect.height()/2, rect.width() - 40, size/3)
            painter.drawText(sub_rect, Qt.AlignCenter | Qt.TextWordWrap, sub_text)
        else:
            painter.drawText(rect, Qt.AlignCenter | Qt.TextWordWrap, self.text)
        
        painter.end()
