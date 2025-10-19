# RangeSlider.py
from PyQt5.QtWidgets import QWidget, QSlider, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt

class RangeSlider(QWidget):
    valueChanged = pyqtSignal(tuple)
    sliderReleased = pyqtSignal()

    def __init__(self, orientation, parent=None):
        super().__init__(parent)

        self.min_slider = QSlider(orientation)
        self.max_slider = QSlider(orientation)

        if orientation == Qt.Orientation.Horizontal:
            layout = QHBoxLayout(self)
        else:
            layout = QVBoxLayout(self)
        
        layout.addWidget(self.min_slider)
        layout.addWidget(self.max_slider)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.min_slider.valueChanged.connect(self._min_changed)
        self.max_slider.valueChanged.connect(self._max_changed)
        
        self.min_slider.sliderReleased.connect(self.sliderReleased.emit)
        self.max_slider.sliderReleased.connect(self.sliderReleased.emit)

    def _min_changed(self, value):
        if value > self.max_slider.value():
            self.max_slider.setValue(value)
        self.valueChanged.emit(self.getValues())

    def _max_changed(self, value):
        if value < self.min_slider.value():
            self.min_slider.setValue(value)
        self.valueChanged.emit(self.getValues())

    def setRange(self, min_val, max_val):
        self.min_slider.setRange(min_val, max_val)
        self.max_slider.setRange(min_val, max_val)

    def setValues(self, min_val, max_val):
        self.min_slider.blockSignals(True)
        self.max_slider.blockSignals(True)
        self.min_slider.setValue(min_val)
        self.max_slider.setValue(max_val)
        self.min_slider.blockSignals(False)
        self.max_slider.blockSignals(False)

    def getValues(self):
        return self.min_slider.value(), self.max_slider.value()
    
    def low(self):
        return self.min_slider.value()
    
    def high(self):
        return self.max_slider.value()