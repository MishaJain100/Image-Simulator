from PyQt5 import QtWidgets, QtGui, QtCore
from simulator_control_panel import Ui_MainWindow as Ui_SimulatorControlPanel
import cv2
import numpy as np

class SimulatorControlPanelLogic(QtWidgets.QMainWindow):
    def __init__(self, parent=None, img=None, img_size=None):
        super().__init__(parent)
        self.ui = Ui_SimulatorControlPanel()
        self.ui.setupUi(self)
        self.connect_signals()

        self.img = None
        self.img_size = None
        self.set_img(img, img_size)
        self.set_current_params()

    def set_current_params(self):
        self.ui.ZoomSlider.setValue(self.parent().current_params['zoom'])
        self.ui.FOVSlider.setValue(self.parent().current_params['fov'])
        self.ui.DistortionSlider.setValue(self.parent().current_params['distortion'])
        self.ui.BrightnessSlider.setValue(self.parent().current_params['brightness'])
        self.ui.LDSlider.setValue(self.parent().current_params['ld'])
        self.ui.ShadowsSlider.setValue(self.parent().current_params['shadows'])
        self.ui.NoiseSlider.setValue(self.parent().current_params['noise'])
        self.ui.ExposureSlider.setValue(self.parent().current_params['exposure'])

    def reset(self):
        self.parent().current_params = {
            'zoom': 0,
            'fov': 60,
            'distortion': 0,
            'brightness': 0,
            'ld': 45,
            'shadows': 0,
            'noise': 0,
            'exposure': 50
        }
        self.ui.ZoomSlider.setValue(0)
        self.ui.ZoomNumber.setText('0%')
        self.ui.FOVSlider.setValue(60)
        self.ui.FOVNumber.setText('60°')
        self.ui.DistortionSlider.setValue(0)
        self.ui.DistortionNumber.setText('0.0')
        self.ui.BrightnessSlider.setValue(0)
        self.ui.BrightnessNumber.setText('0')
        self.ui.LDSlider.setValue(45)
        self.ui.LDNumber.setText('45°')
        self.ui.ShadowsSlider.setValue(0)
        self.ui.ShadowsNumber.setText('0')
        self.ui.NoiseSlider.setValue(0)
        self.ui.NoiseNumber.setText('0')
        self.ui.ExposureSlider.setValue(50)
        self.ui.ExposureNumber.setText('50')
        self.set_img(self.img, self.img_size)

    def set_img(self, img=None, img_size=None):
        self.img = img
        self.img_size = img_size
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
        self.ui.UploadButton.clicked.connect(self.upload_image)
        self.ui.UploadIcon.clicked.connect(self.upload_image)
        self.ui.ConstraintsText.clicked.connect(self.upload_image)
        self.ui.ZoomSlider.valueChanged.connect(self.zoom_val)
        self.ui.ZoomSlider.sliderReleased.connect(lambda: self.update_simulation('zoom'))
        self.ui.FOVSlider.valueChanged.connect(self.fov_val)
        self.ui.FOVSlider.sliderReleased.connect(lambda: self.update_simulation('fov'))
        self.ui.DistortionSlider.valueChanged.connect(self.distortion_val)
        self.ui.DistortionSlider.sliderReleased.connect(lambda: self.update_simulation('distortion'))
        self.ui.BrightnessSlider.valueChanged.connect(self.brightness_val)
        self.ui.BrightnessSlider.sliderReleased.connect(lambda: self.update_simulation('brightness'))
        self.ui.LDSlider.valueChanged.connect(self.ld_val)
        self.ui.LDSlider.sliderReleased.connect(lambda: self.update_simulation('ld'))
        self.ui.ShadowsSlider.valueChanged.connect(self.shadows_val)
        self.ui.ShadowsSlider.sliderReleased.connect(lambda: self.update_simulation('shadows'))
        self.ui.NoiseSlider.valueChanged.connect(self.noise_val)
        self.ui.NoiseSlider.sliderReleased.connect(lambda: self.update_simulation('noise'))
        self.ui.ExposureSlider.valueChanged.connect(self.exposure_val)
        self.ui.ExposureSlider.sliderReleased.connect(lambda: self.update_simulation('exposure'))
        self.ui.Apply.clicked.connect(self.apply)
        self.ui.Reset.clicked.connect(self.reset)
        self.ui.ResolutionDropDown.currentIndexChanged.connect(lambda: self.update_simulation('resolution'))

    def upload_image(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select an Image", "", "Images (*.png *.jpg *.jpeg *.svg)", options=options)
        if file_name:
            self.img = file_name
            print(f"Selected file: {file_name}")
            pixmap = QtGui.QPixmap(file_name)
            label_size = self.ui.OriginalDefault.size()
            pixmap = pixmap.scaled(label_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.ui.OriginalDefault.setPixmap(pixmap)
            self.ui.SimulatedDefault.setPixmap(pixmap)
            self.ui.OriginalDefault.setScaledContents(False)
            self.ui.SimulatedDefault.setScaledContents(False)

            self.parent().img = file_name
            self.parent().img_display_size = label_size
            
            self.update_simulation('all')
        else:
            print("No file selected.")

    def update_simulation(self, changed_param='all'):
        if self.img is None:
            return
        
        img = cv2.imread(self.img)
        
        result = self.apply_zoom(img)
        result = self.apply_fov(result)
        result = self.apply_distortion(result)
        result = self.apply_brightness(result)
        result = self.apply_ld(result)
        result = self.apply_shadows(result)
        result = self.apply_noise(result)
        result = self.apply_exposure(result)
        result = self.apply_resolution(result)
        
        self.display_image(result)

    def zoom_val(self):
        zoom_percent = self.ui.ZoomSlider.value()
        self.ui.ZoomNumber.setText(f'{zoom_percent}%')

    def apply_zoom(self, img):
        zoom_percent = self.ui.ZoomSlider.value()
        self.ui.ZoomNumber.setText(f'{zoom_percent}%')
        
        if zoom_percent == 0:
            return img
        
        h, w = img.shape[:2]
        if zoom_percent > 0:
            scale = 1.0 + (zoom_percent / 100.0)
        else:
            scale = 1.0 + (zoom_percent / 200.0)
        
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        if scale > 1.0:
            start_x = (new_w - w) // 2
            start_y = (new_h - h) // 2
            return resized[start_y:start_y + h, start_x:start_x + w]
        else:
            zoomed = np.zeros((h, w, img.shape[2]), dtype=img.dtype)
            start_x = (w - new_w) // 2
            start_y = (h - new_h) // 2
            zoomed[start_y:start_y + new_h, start_x:start_x + new_w] = resized
            return zoomed

    def fov_val(self):
        fov_degrees = self.ui.FOVSlider.value()
        self.ui.FOVNumber.setText(f'{fov_degrees}°')

    def apply_fov(self, img):
        fov_degrees = self.ui.FOVSlider.value()
        self.ui.FOVNumber.setText(f'{fov_degrees}°')
        
        if fov_degrees == 60:
            return img
        
        h, w = img.shape[:2]
        default_fov = 60
        default_focal = (w / 2.0) / np.tan(np.radians(default_fov / 2.0))
        new_focal = (w / 2.0) / np.tan(np.radians(fov_degrees / 2.0))
        
        K_default = np.array([
            [default_focal, 0, w / 2.0],
            [0, default_focal, h / 2.0],
            [0, 0, 1]
        ], dtype=np.float32)
        
        K_new = np.array([
            [new_focal, 0, w / 2.0],
            [0, new_focal, h / 2.0],
            [0, 0, 1]
        ], dtype=np.float32)
        
        map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
        pts = np.stack([map_x.ravel(), map_y.ravel(), np.ones(w * h)], axis=0)
        pts_normalized = np.linalg.inv(K_new) @ pts
        pts_transformed = K_default @ pts_normalized
        
        map_x_new = pts_transformed[0, :].reshape(h, w).astype(np.float32)
        map_y_new = pts_transformed[1, :].reshape(h, w).astype(np.float32)
        
        return cv2.remap(img, map_x_new, map_y_new, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

    def distortion_val(self):
        distortion = self.ui.DistortionSlider.value()
        self.ui.DistortionNumber.setText(f'{distortion / 1000.0}')

    def apply_distortion(self, img):
        distortion = self.ui.DistortionSlider.value()
        self.ui.DistortionNumber.setText(f'{distortion / 1000.0}')
        
        if distortion == 0:
            return img
        
        h, w = img.shape[:2]
        cx, cy = w // 2, h // 2
        k1 = distortion / 1000.0
        
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
        
        return cv2.remap(img, map_x.astype(np.float32), map_y.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

    def brightness_val(self):
        brightness = self.ui.BrightnessSlider.value()
        self.ui.BrightnessNumber.setText(f'{brightness}')

    def apply_brightness(self, img):
        brightness = self.ui.BrightnessSlider.value()
        self.ui.BrightnessNumber.setText(f'{brightness}')
        
        if brightness == 0:
            return img
        
        img_float = img.astype(np.float32)

        if brightness > 0:
            img_float = img_float + (brightness * 2.55)
        else:
            img_float = img_float + (brightness * 2.55)
        
        img_float = np.clip(img_float, 0, 255)
        
        return img_float.astype(np.uint8)

    def ld_val(self):
        azimuth = self.ui.LDSlider.value()
        self.ui.LDNumber.setText(f'{azimuth}°')

    def apply_ld(self, img):
        azimuth = self.ui.LDSlider.value()
        self.ui.LDNumber.setText(f'{azimuth}°')
        
        if azimuth == 45:
            return img
        
        h, w = img.shape[:2]
        
        azimuth_rad = np.radians(azimuth)

        y_coords = np.linspace(-1, 1, h)
        x_coords = np.linspace(-1, 1, w)
        xx, yy = np.meshgrid(x_coords, y_coords)

        light_x = np.cos(azimuth_rad)
        light_y = np.sin(azimuth_rad)

        alignment = (xx * light_x + yy * light_y) # Sliders angle

        min_intensity = 0.7
        max_intensity = 1.0
        intensity = min_intensity + (alignment + 1) / 2 * (max_intensity - min_intensity)
        intensity = np.clip(intensity, min_intensity, max_intensity)
        
        img_float = img.astype(np.float32)
        for i in range(3):
            img_float[:, :, i] = img_float[:, :, i] * intensity
        
        img_float = np.clip(img_float, 0, 255)
        return img_float.astype(np.uint8)

    def shadows_val(self):
        shadow_intensity = self.ui.ShadowsSlider.value()
        self.ui.ShadowsNumber.setText(f'{shadow_intensity}')

    def apply_shadows(self, img):
        shadow_intensity = self.ui.ShadowsSlider.value()
        self.ui.ShadowsNumber.setText(f'{shadow_intensity}')
        
        if shadow_intensity == 0:
            return img
        
        h, w = img.shape[:2]

        y_gradient = np.linspace(0, 1, h)
        x_gradient = np.linspace(0, 1, w)
        xx, yy = np.meshgrid(x_gradient, y_gradient)
        
        shadow_mask = 1.0 - ((xx + yy) / 2.0)
        
        shadow_strength = shadow_intensity / 100.0
        shadow_mask = 1.0 - (shadow_mask * shadow_strength * 0.5)
        shadow_mask = np.clip(shadow_mask, 0.5, 1.0)
        
        img_float = img.astype(np.float32)
        for i in range(3):
            img_float[:, :, i] = img_float[:, :, i] * shadow_mask
        
        img_float = np.clip(img_float, 0, 255)
        return img_float.astype(np.uint8)

    def noise_val(self):
        noise_level = self.ui.NoiseSlider.value()
        self.ui.NoiseNumber.setText(f'{noise_level}')

    def apply_noise(self, img):
        noise_level = self.ui.NoiseSlider.value()
        self.ui.NoiseNumber.setText(f'{noise_level}')
        
        if noise_level == 0:
            return img
        h, w, c = img.shape
        mean = 0
        sigma = noise_level
        gaussian_noise = np.random.normal(mean, sigma, (h, w, c))
        
        noisy_img = img.astype(np.float32) + gaussian_noise
        noisy_img = np.clip(noisy_img, 0, 255)
        
        return noisy_img.astype(np.uint8)

    def exposure_val(self):
        exposure = self.ui.ExposureSlider.value()
        self.ui.ExposureNumber.setText(f'{exposure}')

    def apply_exposure(self, img):
        exposure = self.ui.ExposureSlider.value()
        self.ui.ExposureNumber.setText(f'{exposure}')
        
        if exposure == 50:
            return img
        
        if exposure < 50:
            exposure_factor = 0.1 + (exposure / 50.0) * 0.9
        else:
            exposure_factor = 1.0 + ((exposure - 50) / 50.0) * 2.0
        
        img_float = img.astype(np.float32) * exposure_factor
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

    def display_image(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.parent().sim = img_rgb
        h, w, ch = img_rgb.shape
        bytes_per_line = ch * w
        qt_image = QtGui.QImage(img_rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qt_image)
        label_size = self.ui.OriginalDefault.size()
        pixmap = pixmap.scaled(label_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.ui.SimulatedDefault.setPixmap(pixmap)

    def apply(self):
        self.parent().current_params = {
            'zoom': self.ui.ZoomSlider.value(),
            'fov': self.ui.FOVSlider.value(),
            'distortion': self.ui.DistortionSlider.value(),
            'brightness': self.ui.BrightnessSlider.value(),
            'ld': self.ui.LDSlider.value(),
            'shadows': self.ui.ShadowsSlider.value(),
            'noise': self.ui.NoiseSlider.value(),
            'exposure': self.ui.ExposureSlider.value()
        }