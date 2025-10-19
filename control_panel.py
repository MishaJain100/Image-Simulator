# control_panel.py
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from backend.utils import np_to_qt_pixmap
from ui_components import ScalableImageLabel
import cv2

class SimulatorControlWidget(QtWidgets.QWidget):
    def __init__(self, params_manager):
        super().__init__()
        self.params_manager = params_manager
        self._dist_slider = None
        self._noise_slider = None
        self._bright_slider = None
        self._light_slider = None
        self._fov_slider = None
        self._shadow_slider = None
        self._zoom_slider = None
        self._exp_slider = None
        self._dist_label = None
        self._noise_label = None
        self._bright_label = None
        self._light_label = None
        self._fov_label = None
        self._shadow_label = None
        self._zoom_label = None
        self._exp_label = None
        self.setup_ui()
        self.init_connections()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Upload Button
        self.upload_btn = QtWidgets.QPushButton("Load Input Image")
        layout.addWidget(self.upload_btn)

        # Params Groups
        self._dist_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)  # type: ignore
        self._dist_label = QtWidgets.QLabel("0.00")
        self.create_param_group(layout, "Distortion Intensity", self._dist_slider, self._dist_label)
        self._noise_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)  # type: ignore
        self._noise_label = QtWidgets.QLabel("0.00")
        self.create_param_group(layout, "Noise Level", self._noise_slider, self._noise_label)
        self._bright_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)  # type: ignore
        self._bright_label = QtWidgets.QLabel("50")
        self.create_param_group(layout, "Brightness", self._bright_slider, self._bright_label)
        self._light_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)  # type: ignore
        self._light_label = QtWidgets.QLabel("0")
        self.create_param_group(layout, "Light Direction (degrees)", self._light_slider, self._light_label)
        self._fov_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)  # type: ignore
        self._fov_label = QtWidgets.QLabel("60")
        self.create_param_group(layout, "Field of View (degrees)", self._fov_slider, self._fov_label)
        self._shadow_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)  # type