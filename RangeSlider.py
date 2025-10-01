from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen, QFont

class RangeSlider(QWidget):
    rangeChanged = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 45)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)    

        self._min = 0
        self._max = 255
        self._lower_value = 64
        self._upper_value = 192
        self._handle_radius = 10
        self._bar_height = 8
        self._first_handle_pressed = False
        self._second_handle_pressed = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        w = self.width()
        h = self.height()
        bar_y_pos = (h - self._bar_height) // 2
        padding = self._handle_radius

        lower_x_pos = self._value_to_pos(self._lower_value)
        upper_x_pos = self._value_to_pos(self._upper_value)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor("#4a5568")))
        painter.drawRoundedRect(padding, bar_y_pos, w - 2 * padding, self._bar_height, self._bar_height / 2, self._bar_height / 2)

        painter.save()
        clip_rect = QRect(lower_x_pos, bar_y_pos, upper_x_pos - lower_x_pos, self._bar_height)
        painter.setClipRect(clip_rect)

        painter.setBrush(QBrush(QColor("#1193d4")))
        painter.drawRoundedRect(padding, bar_y_pos, w - 2 * padding, self._bar_height, self._bar_height / 2, self._bar_height / 2)
        
        painter.restore()

        pen = QPen(QColor("#0d7ab5"), 2)
        brush = QBrush(QColor("#1193d4"))
        
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawEllipse(QPoint(lower_x_pos, h // 2), self._handle_radius, self._handle_radius)
        painter.drawEllipse(QPoint(upper_x_pos, h // 2), self._handle_radius, self._handle_radius)
        
    def mousePressEvent(self, event):
        lower_handle_rect = self._get_handle_rect(self._lower_value)
        upper_handle_rect = self._get_handle_rect(self._upper_value)

        if upper_handle_rect.contains(event.pos()):
            self._second_handle_pressed = True
        elif lower_handle_rect.contains(event.pos()):
            self._first_handle_pressed = True
            
        self.update()

    def _pos_to_value(self, x_pos):
        padding = self._handle_radius
        w = self.width() - 2 * padding
        value_range = self._max - self._min
        
        clamped_pos = max(padding, min(x_pos, w + padding))
        
        if w == 0:
            return self._min
            
        value = self._min + (clamped_pos - padding) * value_range / w
        return int(round(value))

    def mouseMoveEvent(self, event):
        if self._first_handle_pressed:
            new_value = self._pos_to_value(event.pos().x())
            if new_value <= self._upper_value:
                self.setLowerValue(new_value)
        elif self._second_handle_pressed:
            new_value = self._pos_to_value(event.pos().x())
            if new_value >= self._lower_value:
                self.setUpperValue(new_value)

    def mouseReleaseEvent(self, event):
        self._first_handle_pressed = False
        self._second_handle_pressed = False
        self.update()

    def _value_to_pos(self, value):
        padding = self._handle_radius
        w = self.width() - 2 * padding
        value_range = self._max - self._min
        if value_range == 0:
            return padding
        return int(padding + (value - self._min) * w / value_range)

    def _get_handle_rect(self, value):
        x_pos = self._value_to_pos(value)
        y_pos = (self.height() - 2 * self._handle_radius) // 2
        return QRect(x_pos - self._handle_radius, y_pos, 2 * self._handle_radius, 2 * self._handle_radius)

    def setRange(self, min_val, max_val):
        self._min = min_val
        self._max = max_val
        self.update()

    def setLowerValue(self, value):
        if self._min <= value < self._upper_value:
            self._lower_value = value
            self.rangeChanged.emit(self._lower_value, self._upper_value)
            self.update()

    def setUpperValue(self, value):
        if self._lower_value < value <= self._max:
            self._upper_value = value
            self.rangeChanged.emit(self._lower_value, self._upper_value)
            self.update()
            
    def getValues(self):
        return self._lower_value, self._upper_value