import math
import os
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPixmap, QColor, QPainterPath
from PyQt5.QtCore import QTimer, Qt

class ProgressCharacter(QWidget):
    """
    A widget that displays a base character image and a 'fill' character image.
    The fill image is revealed from bottom to top using a wavy pattern (sine/cosine)
    to simulate liquid filling up based on progress.
    """
    def __init__(self, base_image_path="assets/char_gray.png", fill_image_path="assets/char_green.png", parent=None):
        super().__init__(parent)
        
        # Load images
        self.base_pixmap = QPixmap(base_image_path)
        self.fill_pixmap = QPixmap(fill_image_path)
        
        # Fallback if images are missing
        if self.base_pixmap.isNull():
            self.base_pixmap = QPixmap(150, 150)
            self.base_pixmap.fill(QColor("#777777")) # Gray fallback
        if self.fill_pixmap.isNull():
            self.fill_pixmap = QPixmap(150, 150)
            self.fill_pixmap.fill(QColor("#a6e3a1")) # Green fallback

        # Scale to a fixed size using FastTransformation to preserve pixel art sharpness
        self.fixed_w, self.fixed_h = 150, 150
        self.base_pixmap = self.base_pixmap.scaled(self.fixed_w, self.fixed_h, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.fill_pixmap = self.fill_pixmap.scaled(self.fixed_w, self.fixed_h, Qt.KeepAspectRatio, Qt.FastTransformation)

        # Set widget size based on the scaled pixmap size
        self.setFixedSize(self.base_pixmap.width(), self.base_pixmap.height() + 10) 
        
        self.progress = 0.0 # Current visual progress
        self.target_progress = 0.0 # Target progress to ease towards
        self.time_offset = 0.0
        self._max = 1
        
        # Timer for animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_animation)
        self.timer.start(16) # ~60 fps
        
    def set_progress(self, progress: float):
        """Set target progress from 0.0 to 1.0"""
        self.target_progress = max(0.0, min(1.0, progress))
        
    def setMaximum(self, maximum: int):
        self._max = maximum
        
    def setMaxValue(self, maximum: int):
        self._max = maximum
        
    def setValue(self, value: int):
        if self._max > 0:
            # Water fills UP as time decreases
            self.set_progress((self._max - value) / self._max)
        else:
            self.set_progress(1.0)
            
    def setMinimum(self, val):
        pass
        
    def setTextVisible(self, val):
        pass
        
    def setFixedHeight(self, val):
        # Override to prevent shrinking the character
        pass
        
    def _update_animation(self):
        self.time_offset += 0.06 # Speed of the wave
        
        # Easing: approach target_progress smoothly
        if abs(self.target_progress - self.progress) > 0.001:
            self.progress += (self.target_progress - self.progress) * 0.05
        else:
            self.progress = self.target_progress
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.base_pixmap.width()
        h = self.base_pixmap.height()
        
        # Center horizontally, bottom aligned
        x = (self.width() - w) // 2
        y = self.height() - h
        
        # 1. Draw base image
        painter.drawPixmap(x, y, self.base_pixmap)
        
        # 2. Create the masked fill layer
        mask_pixmap = QPixmap(w, h)
        mask_pixmap.fill(Qt.transparent)
        
        mask_painter = QPainter(mask_pixmap)
        mask_painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw the wave shape (water level)
        wave_path = QPainterPath()
        
        # Base water level (y-coordinate relative to h)
        # progress 0.0 -> base_y = h
        # progress 1.0 -> base_y = 0
        base_y = h - (h * self.progress)
        
        # Amplitude is 0 if completely empty or full, so it doesn't wobble out of bounds
        amplitude = 6 if 0.01 < self.progress < 0.99 else 0
        freq = 0.05
        
        wave_path.moveTo(0, h)
        
        # Draw wave from left to right
        for px in range(w + 1):
            py = base_y + math.cos(px * freq + self.time_offset) * amplitude
            if px == 0:
                wave_path.lineTo(px, py)
            else:
                wave_path.lineTo(px, py)
                
        wave_path.lineTo(w, h)
        wave_path.closeSubpath()
        
        # Fill the path with a solid color to create the mask shape
        mask_painter.fillPath(wave_path, Qt.black)
        
        # CompositionMode_SourceIn: Keep source (fill_pixmap) only where destination (wave shape) is opaque
        mask_painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        mask_painter.drawPixmap(0, 0, self.fill_pixmap)
        
        # CompositionMode_DestinationIn: Keep destination (wave-filled image) only where source (base_pixmap) is opaque
        # This prevents the liquid from spilling outside the character's body boundary
        mask_painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        mask_painter.drawPixmap(0, 0, self.base_pixmap)
        
        mask_painter.end()
        
        # 3. Draw the final masked wave over the base image
        painter.drawPixmap(x, y, mask_pixmap)
