# HistogramWidget.py
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QPainter, QBrush, QColor, QFont
from PyQt5 import QtCore

class HistogramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(256, 100)
        self._data = []
        self._bar_color = QColor("#1193d4")

        self.title_label = QLabel(self)
        self.title_label.move(10, 5) 

    def setTitle(self, text):
        self.title_label.setText(text)
        self.title_label.adjustSize()

    def setTitleFont(self, font):
        self.title_label.setFont(font)
        self.title_label.adjustSize()

    def setTitleStyleSheet(self, stylesheet):
        self.title_label.setStyleSheet(stylesheet)
        self.title_label.adjustSize()

    def setData(self, data):
        if data and len(data) == 256:
            self._data = data
        else:
            self._data = []
        self.update()

    def paintEvent(self, event):
        if not hasattr(self, '_data') or not self._data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        widget_width = self.width()
        widget_height = self.height()
        x_axis_height = 20
        chart_height = widget_height - x_axis_height
        max_val = max(self._data)
        if max_val == 0: return

        bar_width = widget_width / 256.0
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self._bar_color))

        for i, value in enumerate(self._data):
            bar_height = (value / max_val) * chart_height
            x_pos = i * bar_width
            y_pos = chart_height - bar_height
            rect = QtCore.QRectF(x_pos, y_pos, bar_width, bar_height)
            painter.drawRect(rect)

        painter.setPen(QColor("#9ca3af"))
        try:
            font = QFont("SpaceGrotesk", 8)
            painter.setFont(font)
        except Exception: pass
        
        ticks = [0, 64, 128, 192, 255]
        for tick_value in ticks:
            x = int((tick_value / 255.0) * self.width())
            
            if tick_value == 0:
                alignment = QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter
                text_rect = QtCore.QRect(x, chart_height, 40, x_axis_height)
            elif tick_value == 255:
                alignment = QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
                text_rect = QtCore.QRect(x - 40, chart_height, 40, x_axis_height)
            else:
                alignment = QtCore.Qt.AlignmentFlag.AlignCenter
                text_rect = QtCore.QRect(x - 20, chart_height, 40, x_axis_height)
                
            painter.drawText(text_rect, int(alignment), str(tick_value))