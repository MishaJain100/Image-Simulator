# distortion_presets_and_customization.py
from PyQt5 import QtCore, QtGui, QtWidgets
import resources_rc
from backend.utils import ParamsManager, np_to_qt_pixmap
from ui_components import ScalableImageLabel

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        try:
            self.space_grotesk = QtGui.QFont(QtGui.QFontDatabase.applicationFontFamilies(QtGui.QFontDatabase.addApplicationFont(":/fonts/resources/fonts/SpaceGrotesk.ttf"))[0])
        except (IndexError, AttributeError):
            self.space_grotesk = QtGui.QFont("Arial", 10)

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1400, 1000)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        
        self.Scrollers = QtWidgets.QWidget(self.centralwidget)
        self.Scrollers.setStyleSheet("#Scrollers { background-color: #0f1b23; }")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.Scrollers)
        self.verticalLayout.setContentsMargins(24, 24, 24, 24)
        self.verticalLayout.setSpacing(30)
        
        header_widget = QtWidgets.QWidget(self.Scrollers)
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0,0,0,0)
        self.Icon = QtWidgets.QPushButton(header_widget)
        self.Icon.setIcon(QtGui.QIcon(":/icons/resources/icons/photo_camera.svg"))
        self.Icon.setIconSize(QtCore.QSize(28, 28))
        self.Icon.setStyleSheet("background-color: #1193d4; color: white; padding: 6px; border-radius: 8px;")
        header_layout.addWidget(self.Icon)
        title = QtWidgets.QLabel("Distortion Presets", header_widget)
        title.setFont(self.space_grotesk)
        title.setStyleSheet("color: white; font-weight: bold; font-size: 28px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        self.verticalLayout.addWidget(header_widget)

        self.Parameters = QtWidgets.QWidget(self.Scrollers)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.Parameters)
        
        self.DistortionSettings = QtWidgets.QLabel("Distortion Settings", self.Parameters)
        self.DistortionSettings.setFont(self.space_grotesk)
        self.DistortionSettings.setStyleSheet("color: white; font-weight: bold; font-size: 26px;")
        self.verticalLayout_3.addWidget(self.DistortionSettings)

        self.verticalLayout_3.addWidget(self._create_presets_widget())

        self.DistortionTypeRadios = QtWidgets.QWidget(self.Parameters)
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout(self.DistortionTypeRadios)
        self.Barrel = QtWidgets.QRadioButton("Barrel", self.DistortionTypeRadios)
        self.Pincushion = QtWidgets.QRadioButton("Pincushion", self.DistortionTypeRadios)
        self.Nonee = QtWidgets.QRadioButton("None", self.DistortionTypeRadios)
        self.Nonee.setChecked(True)
        self.horizontalLayout_14.addWidget(self.Barrel)
        self.horizontalLayout_14.addWidget(self.Pincushion)
        self.horizontalLayout_14.addWidget(self.Nonee)
        self.verticalLayout_3.addWidget(self.DistortionTypeRadios)
        
        self.IntensitySlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.IntensitySlider.setMaximum(100)
        self.IntensityNumber = QtWidgets.QLabel("0.00")
        intensity_widget = self.create_slider_widget("Intensity", self.IntensitySlider, self.IntensityNumber)
        self.verticalLayout_3.addWidget(intensity_widget)

        self.verticalLayout.addWidget(self.Parameters)
        self.verticalLayout.addStretch()
        self.horizontalLayout.addWidget(self.Scrollers)

        self.ImageWindow = QtWidgets.QWidget(self.centralwidget)
        self.ImageWindow.setStyleSheet("background-color: #0f1b23; border-left: 1px solid #2d3748;")
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout(self.ImageWindow)
        
        original_container, self.OriginalDefault = self._create_display_widget("Original Image")
        self.horizontalLayout_13.addWidget(original_container)
        
        simulated_container, self.SimulatedDefault = self._create_display_widget("Simulated Image")
        self.horizontalLayout_13.addWidget(simulated_container)

        self.horizontalLayout.addWidget(self.ImageWindow)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)

    def _create_display_widget(self, title):
        container_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container_widget)
        layout.setContentsMargins(15,15,15,15)
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 18px; font-weight: 600; border: none;")
        layout.addWidget(title_label)
        image_label = ScalableImageLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Ignored)
        image_label.setSizePolicy(sizePolicy)
        image_label.setStyleSheet("background-color: #1c2a35; border: 1px solid #2d3748; border-radius: 8px;")
        layout.addWidget(image_label)
        layout.setStretch(1, 1)
        return container_widget, image_label
    
    def create_slider_widget(self, label_text, slider, number_label):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(0,0,0,0)
        label = QtWidgets.QLabel(label_text)
        label.setStyleSheet("font-size: 14px; color: #e5e7eb;")
        layout.addWidget(label)
        
        slider_layout = QtWidgets.QHBoxLayout()
        slider_layout.addWidget(slider)
        number_label.setMinimumWidth(50)
        number_label.setStyleSheet("font-family: monospace; font-size: 14px; color: #9ca3af;")
        slider_layout.addWidget(number_label)
        layout.addLayout(slider_layout)
        return widget

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Image Simulator")
        
    def _create_presets_widget(self):
        presets_widget = QtWidgets.QWidget()
        presets_layout = QtWidgets.QHBoxLayout(presets_widget)
        presets_layout.setContentsMargins(0, 0, 0, 0)
        presets_label = QtWidgets.QLabel("Presets:")
        presets_label.setStyleSheet("color: white; font-size: 14px;")
        presets_label.setFont(self.space_grotesk)
        presets_layout.addWidget(presets_label)
        presets = {"Slight Barrel": 0.2, "Strong Barrel": 0.5, "Slight Pincushion": -0.2, "Strong Pincushion": -0.5}
        for name, value in presets.items():
            button = QtWidgets.QPushButton(name)
            button.setStyleSheet("QPushButton { background-color: #374151; color: white; padding: 5px; border-radius: 4px; } QPushButton:hover { background-color: #4a5568; }")
            button.clicked.connect(lambda checked, v=value: self.apply_preset(v))
            presets_layout.addWidget(button)
        return presets_widget

    def apply_preset(self, value):
        if value > 0:
            self.Barrel.setChecked(True)
            self.IntensitySlider.setValue(int(value * 100))
        elif value < 0:
            self.Pincushion.setChecked(True)
            self.IntensitySlider.setValue(int(abs(value) * 100))
        else:
            self.Nonee.setChecked(True)
            self.IntensitySlider.setValue(0)
        self.update_params()
        
    def init_backend_connections(self, params_manager: ParamsManager):
        self.params_manager = params_manager

        self.Barrel.toggled.connect(self.update_params)
        self.Pincushion.toggled.connect(self.update_params)
        self.Nonee.toggled.connect(self.update_params)
        self.IntensitySlider.valueChanged.connect(lambda v: self.IntensityNumber.setText(f"{v/100.0:.2f}"))
        self.IntensitySlider.sliderReleased.connect(self.update_params)

        self.params_manager.sim_updated.connect(self.update_displays)
        self.update_displays()

    def update_params(self):
        dist_type = "None"
        if self.Barrel.isChecked(): dist_type = "Barrel"
        elif self.Pincushion.isChecked(): dist_type = "Pincushion"
        
        current_params = {
            'distortion_type': dist_type,
            'distortion_intensity': self.IntensitySlider.value() / 100.0,
        }
        self.params_manager.update(current_params)

    def update_displays(self):
        dist_type = self.params_manager.get('distortion_type', 'None')
        if dist_type == 'Barrel': self.Barrel.setChecked(True)
        elif dist_type == 'Pincushion': self.Pincushion.setChecked(True)
        else: self.Nonee.setChecked(True)
        self.IntensitySlider.setValue(int(self.params_manager.get('distortion_intensity', 0) * 100))
        
        input_img = self.params_manager.get('input_img')
        sim_img = self.params_manager.get('sim_img')
        
        if input_img is not None:
            self.OriginalDefault.setPixmap(np_to_qt_pixmap(input_img))
        else:
            self.OriginalDefault.setPixmap(QtGui.QPixmap())

        if sim_img is not None:
            self.SimulatedDefault.setPixmap(np_to_qt_pixmap(sim_img))
        else:
            self.SimulatedDefault.setPixmap(QtGui.QPixmap())