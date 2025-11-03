from PyQt5 import QtWidgets, QtGui, QtCore
from sensor_and_noise_parameter import Ui_MainWindow as Ui_SensorAndNoiseParameter
import cv2
import numpy as np

class SensorAndNoiseParameterLogic(QtWidgets.QMainWindow):
    def __init__(self, parent=None, img=None, img_size=None):
        super().__init__(parent)
        self.ui = Ui_SensorAndNoiseParameter()
        self.ui.setupUi(self)
        
        self.img = None

        self.connect_signals()
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

    def connect_signals(self):
        self.ui.SensorTypeDropDown.currentIndexChanged.connect(self.update_simulation)
        self.ui.NoiseLevelSlider.valueChanged.connect(self.update_simulation)
        self.ui.ExposureTimeSlider.valueChanged.connect(self.update_simulation)
        self.ui.DynamicRangeSlider.rangeChanged.connect(self.update_simulation)

    def update_simulation(self):
        if not self.img:
            return
        
        img = cv2.imread(self.img)
        img = self.apply_noise(img)

        self.display_image(img)

    def apply_noise(self, img):
        sensor_type = self.ui.SensorTypeDropDown.currentText()
        noise_level = self.ui.NoiseLevelSlider.value()
        self.ui.NoiseLevelNumber.setText(f'{noise_level}')

        if noise_level == 0:
            return img
        
        h, w, c = img.shape
        img_float = img.astype(np.float32)

        if sensor_type == "CMOS":
            mean = 0
            sigma = noise_level
            gaussian_noise = np.random.normal(mean, sigma, (h, w, c))
            noisy_img = img_float + gaussian_noise
            
        elif sensor_type == "CCD":
            scale = (255.0 / noise_level) if noise_level > 0 else 255.0
            noisy_img = np.random.poisson(img / scale) * scale
            
        else:
            mean = 0
            sigma = noise_level
            gaussian_noise = np.random.normal(mean, sigma, (h, w, c))
            noisy_img = img_float + gaussian_noise

        noisy_img = np.clip(noisy_img, 0, 255)
        return noisy_img.astype(np.uint8)
    
    def noise_val_update(self):
        """Lightweight function to update the noise label in real-time."""
        noise_level = self.ui.NoiseLevelSlider.value()
        self.ui.NoiseLevelNumber.setText(f'{noise_level}')

    def exposure_time_val_update(self):
        """Lightweight function to update the exposure label in real-time."""
        exposure_val = self.ui.ExposureTimeSlider.value()
        self.ui.ExposureTimeNumber.setText(f'{exposure_val} ms')

    def dynamic_range_val_update(self, min_val, max_val):
        """Lightweight function to update the dynamic range label in real-time."""
        self.ui.DynamicRangeNumber.setText(f'{min_val} - {max_val}')

    def display_image(self, img):
        """Converts an OpenCV image to QPixmap and displays it."""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        bytes_per_line = ch * w
        qt_image = QtGui.QImage(img_rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qt_image)
        
        label_size = self.ui.OriginalDefault.size()
        pixmap = pixmap.scaled(label_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        
        self.ui.SimulatedDefault.setPixmap(pixmap)