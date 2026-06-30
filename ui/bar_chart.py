from PyQt5.QtWidgets import QWidget, QToolTip
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush
from PyQt5.QtCore import Qt, QRect
from datetime import datetime, timedelta
from core.i18n import t

import ui.theme as theme
from core.config_manager import load_config

class PlayTimeBarChart(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(250)
        self._data = {}
        self._days = 7
        self._is_dark = load_config().get("dark_mode", True)
        self._bars_rects = []  # Stores (QRect, total_hours, violation_hours, date_str) for tooltips
        self.setMouseTracking(True)

    def set_data(self, data: dict, days: int = 7):
        """
        data: dict of date_str (YYYY-MM-DD) -> dict with 'total_seconds' and 'violation_seconds'
        """
        self._data = data
        self._days = days
        self.setMinimumWidth(days * 40 + 60) # Ensure each bar has enough space
        self.update()

    def set_dark_mode(self, is_dark: bool):
        self._is_dark = is_dark
        self.update()

    def paintEvent(self, event):
        colors = theme.get_chart_colors(getattr(self, '_is_dark', True))
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        # Margins
        margin_left = 40
        margin_right = 20
        margin_top = 20
        margin_bottom = 30

        # Draw axes
        painter.setPen(QPen(QColor(colors["axes"]), 1))
        painter.drawLine(margin_left, margin_top, margin_left, height - margin_bottom) # Y axis
        painter.drawLine(margin_left, height - margin_bottom, width - margin_right, height - margin_bottom) # X axis

        # Generate last N days
        today = datetime.now()
        dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(self._days - 1, -1, -1)]

        # Find max hours
        max_seconds = 3600  # Minimum 1 hour scale
        for d in dates:
            if d in self._data:
                max_seconds = max(max_seconds, self._data[d].get("total_seconds", 0))

        max_hours = (max_seconds // 3600) + 1

        # Draw Y axis labels
        painter.setPen(QPen(QColor(colors["axes"]), 1))
        font = QFont("Segoe UI", 8)
        painter.setFont(font)
        
        y_steps = 4
        for i in range(y_steps + 1):
            h = max_hours * i / y_steps
            y = height - margin_bottom - (i / y_steps) * (height - margin_top - margin_bottom)
            
            # Grid line
            if i > 0:
                painter.setPen(QPen(QColor(colors["grid"]), 1, Qt.DashLine))
                painter.drawLine(margin_left, int(y), width - margin_right, int(y))
            
            # Label
            painter.setPen(QPen(QColor(colors["axes"]), 1))
            painter.drawText(0, int(y) - 10, margin_left - 10, 20, Qt.AlignRight | Qt.AlignVCenter, f"{h:.1f}h")

        # Draw Bars
        self._bars_rects.clear()
        if self._days == 0: return

        bar_spacing = (width - margin_left - margin_right) / self._days
        bar_width = min(bar_spacing * 0.6, 40)
        
        for i, date_str in enumerate(dates):
            x_center = margin_left + bar_spacing * i + bar_spacing / 2
            x = int(x_center - bar_width / 2)
            
            day_data = self._data.get(date_str, {"total_seconds": 0, "violation_seconds": 0})
            total_sec = day_data.get("total_seconds", 0)
            viol_sec = day_data.get("violation_seconds", 0)
            
            # Clamp violation to not exceed total (just in case)
            viol_sec = min(viol_sec, total_sec)

            # Calculate heights
            graph_height = height - margin_top - margin_bottom
            total_h = (total_sec / (max_hours * 3600)) * graph_height
            viol_h = (viol_sec / (max_hours * 3600)) * graph_height
            valid_h = total_h - viol_h

            y_bottom = height - margin_bottom
            
            # Draw valid part (Green/Gray)
            if valid_h > 0:
                rect = QRect(x, int(y_bottom - valid_h), int(bar_width), int(valid_h))
                painter.setBrush(QBrush(QColor(colors["valid"]))) # Green for valid
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(rect, 4, 4)
                
            # Draw violation part (Red)
            if viol_h > 0:
                rect = QRect(x, int(y_bottom - total_h), int(bar_width), int(viol_h))
                painter.setBrush(QBrush(QColor(colors["violation"]))) # Red for violation
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(rect, 4, 4)
                
            # Save rect for tooltip (full bar)
            if total_sec > 0:
                full_rect = QRect(x, int(y_bottom - total_h), int(bar_width), int(total_h))
                self._bars_rects.append((full_rect, total_sec / 3600, viol_sec / 3600, date_str))

            # X Axis label (e.g. DD/MM)
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            label_str = date_obj.strftime("%d/%m")
            if self._days <= 14 or i % 3 == 0:  # Avoid crowding labels if too many days
                painter.setPen(QPen(QColor(colors["axes"]), 1))
                painter.drawText(int(x_center - 20), height - margin_bottom + 5, 40, 20, Qt.AlignCenter, label_str)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        for rect, total_h, viol_h, date_str in self._bars_rects:
            if rect.contains(pos):
                valid_h = total_h - viol_h
                text = (f"{date_str}\n"
                        f"{t('chart_total', total_h=total_h)}\n"
                        f"{t('chart_valid', valid_h=valid_h)}\n"
                        f"{t('chart_viol', viol_h=viol_h)}")
                QToolTip.showText(self.mapToGlobal(pos), text, self)
                return
        QToolTip.hideText()
