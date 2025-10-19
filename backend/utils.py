# backend/utils.py
import os
import cv2
import numpy as np
import json
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QObject, pyqtSignal

def np_to_qt_pixmap(img: np.ndarray) -> QPixmap:
    if img is None or not isinstance(img, np.ndarray): return QPixmap()
    if img.ndim == 2:
        h, w = img.shape
        qimg = QImage(img.data, w, h, w, QImage.Format_Indexed8)
        return QPixmap.fromImage(qimg)
    h, w, channels = img.shape
    if channels == 3:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return QPixmap.fromImage(QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888))
    elif channels == 4:
        rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        return QPixmap.fromImage(QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888))
    return QPixmap()

def compute_histogram(img: np.ndarray) -> list:
    if img is None: return [0] * 256
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten().tolist()
    return hist

class ParamsManager(QObject):
    sim_updated = pyqtSignal()

    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self._params = {
            'input_img': None,
            'sim_img': None,
            'real_img': None,
            'batch_imgs': [],
            'zoom': 1.0, 'fov': 60, 'defocus': 0.0,
            'chromatic_aberration': 0.0, 'vignetting': 0.0,
            'distortion_type': 'None', 'distortion_intensity': 0.0,
            'brightness': 50, 'light_direction': 0, 'shadows': 0.0, 'specular': 0.0,
            'noise_level': 0.0, 'exposure': 50, 'dynamic_range': (0, 255),
            'sensor_type': 'CMOS', 'resolution': 'Unchanged', 'cfa': False,
        }

    def get(self, key, default=None):
        return self._params.get(key, default)

    def set(self, key, value):
        self._params[key] = value

    def get_params(self) -> dict:
        return self._params.copy()

    def update(self, updates: dict):
        for k, v in updates.items():
            self._params[k] = v
        
        input_img = self.get('input_img')
        if input_img is not None:
            all_params = self.get_params()
            sim_result = self.engine.run_pipeline(input_img.copy(), all_params)
            self._params['sim_img'] = sim_result
        else:
            self._params['sim_img'] = None

        self.sim_updated.emit()