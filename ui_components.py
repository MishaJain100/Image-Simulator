# ui_components.py
from PyQt5 import QtWidgets, QtGui, QtCore

class ScalableImageLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pixmap = QtGui.QPixmap()
        self.setMinimumSize(1, 1)

    def setPixmap(self, pixmap):
        if not isinstance(pixmap, QtGui.QPixmap) or pixmap.isNull():
            self._pixmap = QtGui.QPixmap()
            super().setPixmap(self._pixmap)
        else:
            self._pixmap = pixmap
            self._rescale_pixmap()

    def resizeEvent(self, event):
        self._rescale_pixmap()
        super().resizeEvent(event)

    def _rescale_pixmap(self):
        if self._pixmap.isNull():
            return
        
        scaled_pixmap = self._pixmap.scaled(
            self.size(),
            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
            QtCore.Qt.TransformationMode.SmoothTransformation
        )
        super().setPixmap(scaled_pixmap)