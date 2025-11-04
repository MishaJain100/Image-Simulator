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
        self.ui.NoiseLevelSlider.valueChanged.connect(self.noise_val_update)
        self.ui.NoiseLevelSlider.sliderReleased.connect(self.update_simulation)
        self.ui.ExposureTimeSlider.valueChanged.connect(self.exposure_time_val_update)
        self.ui.ExposureTimeSlider.sliderReleased.connect(self.update_simulation)
        self.ui.DynamicRangeSlider.rangeChanged.connect(self.dynamic_range_val_update)
        self.ui.DynamicRangeSlider.sliderReleased.connect(self.update_simulation)
        self.ui.ResolutionDropDown.currentIndexChanged.connect(self.update_simulation)

    def update_simulation(self):
        if not self.img:
            return
        
        img = cv2.imread(self.img)
        img = self.apply_exposure_time(img)
        img = self.apply_dynamic_range(img)
        img = self.apply_noise(img)
        img = self.apply_resolution(img)

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

    def apply_exposure_time(self, img):
        exposure = self.ui.ExposureTimeSlider.value()
        if exposure == 50:
            return img
        if exposure < 50:
            exposure_factor = 0.1 + (exposure / 50.0) * 0.9
        else:
            exposure_factor = 1.0 + ((exposure - 50) / 50.0) * 2.0
        
        img_float = img.astype(np.float32) * exposure_factor
        img_float = np.clip(img_float, 0, 255)
        return img_float.astype(np.uint8)

    def apply_dynamic_range(self, img):
        min_val, max_val = self.ui.DynamicRangeSlider.getValues()
        
        img_float = img.astype(np.float32)
        img_float = np.clip(img_float, min_val, max_val)
        
        if max_val > min_val:
            img_float = (img_float - min_val) * (255.0 / (max_val - min_val))
            
        img_float = np.clip(img_float, 0, 255)
        
        return img_float.astype(np.uint8)

    def apply_resolution(self, img):
        resolution_text = self.ui.ResolutionDropDown.currentText()
        
        parts = resolution_text.split(' x ')
        target_w = int(parts[0])
        target_h = int(parts[1])

        if img.shape[1] == target_w and img.shape[0] == target_h:
            return img
            
        resized_img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
        return resized_img

    def noise_val_update(self):
        noise_level = self.ui.NoiseLevelSlider.value()
        self.ui.NoiseLevelNumber.setText(f'{noise_level}')

    def exposure_time_val_update(self):
        exposure_val = self.ui.ExposureTimeSlider.value()
        self.ui.ExposureTimeNumber.setText(f'{exposure_val} ms')

    def dynamic_range_val_update(self, min_val, max_val):
        self.ui.DynamicRangeNumber.setText(f'{min_val} - {max_val}')

    def display_image(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        bytes_per_line = ch * w
        qt_image = QtGui.QImage(img_rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qt_image)
        
        label_size = self.ui.OriginalDefault.size()
        pixmap = pixmap.scaled(label_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        
        self.ui.SimulatedDefault.setPixmap(pixmap)