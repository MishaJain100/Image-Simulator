# sensor_and_noise_parameter.py
from PyQt5 import QtCore, QtGui, QtWidgets
from RangeSlider import RangeSlider
from backend.utils import ParamsManager, np_to_qt_pixmap
import resources_rc
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
        title = QtWidgets.QLabel("Sensor and Noise", header_widget)
        title.setFont(self.space_grotesk)
        title.setStyleSheet("color: white; font-weight: bold; font-size: 28px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        self.verticalLayout.addWidget(header_widget)

        self.Parameters = QtWidgets.QWidget(self.Scrollers)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.Parameters)
        
        self.SensorConfiguration = QtWidgets.QLabel("Sensor Configuration", self.Parameters)
        self.SensorConfiguration.setFont(self.space_grotesk)
        self.SensorConfiguration.setStyleSheet("color: white; font-weight: bold; font-size: 26px;")
        self.verticalLayout_3.addWidget(self.SensorConfiguration)
        
        self.NoiseLevelSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.NoiseLevelSlider.setMaximum(100)
        self.NoiseLevelNumber = QtWidgets.QLabel("0.00")
        self.verticalLayout_3.addWidget(self.create_slider_widget("Noise Level", self.NoiseLevelSlider, self.NoiseLevelNumber))

        self.ExposureTimeSlider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.ExposureTimeSlider.setMaximum(100); self.ExposureTimeSlider.setValue(50)
        self.ExposureTimeNumber = QtWidgets.QLabel("1.00x")
        self.verticalLayout_3.addWidget(self.create_slider_widget("Exposure", self.ExposureTimeSlider, self.ExposureTimeNumber))

        self.DynamicRangeSlider = RangeSlider(QtCore.Qt.Orientation.Horizontal)
        self.DynamicRangeSlider.setRange(0, 255); self.DynamicRangeSlider.setValues(0, 255)
        self.DynamicRangeNumber = QtWidgets.QLabel("0 - 255")
        self.verticalLayout_3.addWidget(self.create_slider_widget("Dynamic Range", self.DynamicRangeSlider, self.DynamicRangeNumber))
        
        self.SensorTypeDropDown = QtWidgets.QComboBox()
        self.SensorTypeDropDown.addItems(["CMOS", "CCD", "sCMOS"])
        self.verticalLayout_3.addWidget(self.SensorTypeDropDown)

        self.ResolutionDropDown = QtWidgets.QComboBox()
        self.ResolutionDropDown.addItems(["Unchanged", "1920 x 1080", "1280 x 720", "800 x 600"])
        self.verticalLayout_3.addWidget(self.ResolutionDropDown)
        
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
        
    def _create_display_widget(self, title):
        container_widget = QWidget()
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

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Image Simulator")
        
    def init_backend_connections(self, params_manager: ParamsManager):
        self.params_manager = params_manager

        self.NoiseLevelSlider.valueChanged.connect(lambda v: self.NoiseLevelNumber.setText(f"{v/100.0:.2f}"))
        self.ExposureTimeSlider.valueChanged.connect(lambda v: self.ExposureTimeNumber.setText(f"{v/50.0:.2f}x"))
        self.DynamicRangeSlider.valueChanged.connect(lambda vals: self.DynamicRangeNumber.setText(f"{vals[0]} - {vals[1]}"))

        self.NoiseLevelSlider.sliderReleased.connect(self.update_params)
        self.ExposureTimeSlider.sliderReleased.connect(self.update_params)
        self.DynamicRangeSlider.sliderReleased.connect(self.update_params)
        self.SensorTypeDropDown.currentTextChanged.connect(self.update_params)
        self.ResolutionDropDown.currentTextChanged.connect(self.update_params)
        
        self.params_manager.sim_updated.connect(self.update_displays)
        self.update_displays()

    def update_params(self):
        w, h = (1920, 1080)
        input_img = self.params_manager.get('input_img')
        if input_img is not None:
            h, w = input_img.shape[:2]
        
        res_selection = self.ResolutionDropDown.currentText()
        low, high = self.DynamicRangeSlider.getValues()

        current_params = {
            'noise_level': self.NoiseLevelSlider.value() / 100.0,
            'exposure': self.ExposureTimeSlider.value(),
            'dynamic_range': (low, high),
            'sensor_type': self.SensorTypeDropDown.currentText(),
            'resolution': f"{w} x {h}" if res_selection == "Unchanged" else res_selection,
        }
        self.params_manager.update(current_params)

    def update_displays(self):
        self.NoiseLevelSlider.setValue(int(self.params_manager.get('noise_level', 0) * 100))
        self.ExposureTimeSlider.setValue(int(self.params_manager.get('exposure', 50)))
        dr_low, dr_high = self.params_manager.get('dynamic_range', (0, 255))
        self.DynamicRangeSlider.setValues(dr_low, dr_high)
        self.SensorTypeDropDown.setCurrentText(self.params_manager.get('sensor_type', 'CMOS'))
        self.ResolutionDropDown.setCurrentText(self.params_manager.get('resolution', 'Unchanged'))
        
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