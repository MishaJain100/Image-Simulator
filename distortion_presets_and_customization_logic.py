from PyQt5 import QtWidgets, QtCore, QtGui
from distortion_presets_and_customization import Ui_MainWindow as Ui_DistortionPresetsAndCustomization
import numpy as np
import cv2

class DistortionPresetsAndCustomizationLogic(QtWidgets.QMainWindow):
    def __init__(self, parent=None, img=None, img_size=None):
        super().__init__(parent)
        self.ui = Ui_DistortionPresetsAndCustomization()
        self.ui.setupUi(self)
        self.reset()
        self.connect_signals()
        self.selection = 'None'
        self.set_img(img, img_size)
        
    def set_img(self, img=None, img_size=None):
        self.img = img
        if self.img:
            pixmap = QtGui.QPixmap(img)
            
            if img_size:
                label_size = img_size
            else:
                label_size = self.ui.OriginalDefault.size()
            
            pixmap = pixmap.scaled(label_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.ui.OriginalDefault.setPixmap(pixmap)
            self.ui.SimulatedDefault.setPixmap(pixmap)
            self.ui.OriginalDefault.setScaledContents(False)
            self.ui.SimulatedDefault.setScaledContents(False)
            
            img_data = cv2.imread(img)
            h, w = img_data.shape[:2]
            self.ui.CenterXSlider.setRange(0, w)
            self.ui.CenterYSlider.setRange(0, h)

    def reset(self):
        _translate = QtCore.QCoreApplication.translate
        self.ui.Barrel.setChecked(False)
        self.ui.Pinpoint.setChecked(False)
        self.ui.Nonee.setChecked(False)
        self.selection = 'None'
        self.img = None
        self.ui.CenterXSlider.setRange(0, 100)
        self.ui.CenterXSlider.setRange(0, 100)
        self.ui.CenterXSlider.setValue(0)
        self.ui.CenterYSlider.setValue(0)
        self.ui.IntensitySlider.setValue(0)
        self.ui.IntensityNumber.setText(_translate("MainWindow", "0"))
        self.ui.CenterXNumber.setText(_translate("MainWindow", "0"))
        self.ui.CenterYNumber.setText(_translate("MainWindow", "0"))

    def connect_signals(self):
        self.ui.Barrel.clicked.connect(self.selection_changed)
        self.ui.Pinpoint.clicked.connect(self.selection_changed)
        self.ui.Nonee.clicked.connect(self.selection_changed)
        self.ui.IntensitySlider.valueChanged.connect(self.update_distortion)
        self.ui.CenterXSlider.valueChanged.connect(self.update_distortion)
        self.ui.CenterYSlider.valueChanged.connect(self.update_distortion)

    def update_distortion(self):
        if not self.img:
            return
        img = cv2.imread(self.img)
        h, w = img.shape[:2]
        value = self.ui.IntensitySlider.value()
        cx = self.ui.CenterXSlider.value()
        cy = self.ui.CenterYSlider.value()
        self.ui.IntensityNumber.setText(f'{value / 1000.0}')
        self.ui.CenterXNumber.setText(f'{cx}')
        self.ui.CenterYNumber.setText(f'{cy}')
        
        if self.selection == 'None':
            pixmap = QtGui.QPixmap(self.img)
            self.ui.SimulatedDefault.setPixmap(pixmap)
            return
        elif self.selection == 'Barrel':
            k1 = value / 1000.0
        else:
            k1 = -value / 1000.0

        map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
        dx, dy = map_x - cx, map_y - cy
        r_sq = dx**2 + dy**2
        norm_denom = (w/2)**2 + (h/2)**2
        if norm_denom == 0: 
            norm_denom = 1
        r_sq_norm = r_sq / norm_denom
        radial = 1 + k1 * r_sq_norm
        map_x = cx + dx * radial
        map_y = cy + dy * radial
        distorted = cv2.remap(img, map_x.astype(np.float32), map_y.astype(np.float32), 
                            cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        
        distorted_rgb = cv2.cvtColor(distorted, cv2.COLOR_BGR2RGB)
        h, w, ch = distorted_rgb.shape
        bytes_per_line = ch * w
        qt_image = QtGui.QImage(distorted_rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qt_image)
        self.ui.SimulatedDefault.setPixmap(pixmap)

    def selection_changed(self):
        if self.ui.Barrel.isChecked():
            self.selection = 'Barrel'
        elif self.ui.Pinpoint.isChecked():
            self.selection = 'Pinpoint'
        else:
            self.selection = 'None'