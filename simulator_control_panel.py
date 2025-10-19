# simulator_control_panel.py
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QWidget, QHBoxLayout, QFormLayout, QGroupBox, QScrollArea
from backend.utils import ParamsManager, np_to_qt_pixmap
from RangeSlider import RangeSlider
from ui_components import ScalableImageLabel
import resources_rc, cv2

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        try:
            self.space_grotesk = QtGui.QFont(QtGui.QFontDatabase.applicationFontFamilies(QtGui.QFontDatabase.addApplicationFont(":/fonts/resources/fonts/SpaceGrotesk.ttf"))[0])
        except (IndexError, AttributeError):
            self.space_grotesk = QtGui.QFont("Arial", 10)

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1400, 1000)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        
        self.control_panel_widget = QtWidgets.QWidget(self.centralwidget)
        self.control_panel_widget.setStyleSheet("background-color: #0f1b23;")
        
        main_layout = QtWidgets.QVBoxLayout(self.control_panel_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        self.Icon = QtWidgets.QPushButton()
        self.Icon.setStyleSheet("background-color: #1193d4; color: white; padding: 6px; border: 2px solid #1193d4; border-radius: 8px;")
        self.Icon.setIcon(QtGui.QIcon(":/icons/resources/icons/photo_camera.svg"))
        self.Icon.setIconSize(QtCore.QSize(28, 28))
        header_layout.addWidget(self.Icon)
        
        title_label = QtWidgets.QLabel("Simulator Control Panel")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 28px;")
        title_label.setFont(self.space_grotesk)
        header_layout.addWidget(title_label)
        main_layout.addWidget(header_widget)

        self.load_image_button = QtWidgets.QPushButton("Load Input Image...")
        self.load_image_button.setStyleSheet("QPushButton { background-color: #1193d4; color: #ffffff; font-size: 14px; padding: 8px 0px; border-radius: 4px; border: none; } QPushButton:hover { background-color: #15a4e5; }")
        self.load_image_button.setFont(self.space_grotesk)
        main_layout.addWidget(self.load_image_button)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        main_layout.addWidget(scroll)
        
        content_widget = QWidget()
        scroll.setWidget(content_widget)
        layout = QtWidgets.QVBoxLayout(content_widget)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self._create_all_groups(layout)
        self.horizontalLayout.addWidget(self.control_panel_widget)

        self.display_panel_widget = QtWidgets.QWidget(self.centralwidget)
        self.display_panel_widget.setStyleSheet("background-color: #0f1b23; border-left: 1px solid #2d3748;")
        display_layout = QtWidgets.QHBoxLayout(self.display_panel_widget)
        
        original_container, self.original_image_label = self._create_display_widget("Original Image")
        display_layout.addWidget(original_container)

        simulated_container, self.simulated_image_label = self._create_display_widget("Simulated Image")
        display_layout.addWidget(simulated_container)
        
        self.horizontalLayout.addWidget(self.display_panel_widget)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)

    def _create_display_widget(self, title):
        container_widget = QWidget()
        layout = QtWidgets.QVBoxLayout(container_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("color: white; font-size: 18px; font-weight: 600; border: none;")
        layout.addWidget(title_label)
        
        image_label = ScalableImageLabel()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Ignored, QtWidgets.QSizePolicy.Policy.Ignored)
        image_label.setSizePolicy(sizePolicy)
        image_label.setStyleSheet("background-color: #1c2a35; border: 1px solid #2d3748; border-radius: 8px;")
        layout.addWidget(image_label)
        layout.setStretch(1,1)
        return container_widget, image_label

    def _create_all_groups(self, parent_layout):
        parent_layout.addWidget(self._create_optics_group())
        parent_layout.addWidget(self._create_lighting_group())
        parent_layout.addWidget(self._create_sensor_group())

    def _create_group_box(self, title):
        group = QGroupBox(title)
        group.setStyleSheet("QGroupBox { color: white; font-weight: bold; font-size: 16px; border: 1px solid #374151; border-radius: 8px; margin-top: 10px; padding-top: 15px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; } QLabel { color: #e5e7eb; font-size: 14px; }")
        group.setFont(self.space_grotesk)
        return group, QFormLayout()

    def create_slider_layout(self, slider, label):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(slider)
        label.setMinimumWidth(50)
        label.setStyleSheet("color: #9ca3af; font-family: monospace; font-size: 12px;")
        layout.addWidget(label)
        return widget

    def _create_optics_group(self):
        group, layout = self._create_group_box("Camera Optics")
        self.zoom_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); self.zoom_slider.setRange(50, 200); self.zoom_slider.setValue(100)
        self.zoom_label = QtWidgets.QLabel("1.00x")
        layout.addRow("Zoom:", self.create_slider_layout(self.zoom_slider, self.zoom_label))
        
        self.fov_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); self.fov_slider.setRange(30, 90); self.fov_slider.setValue(60)
        self.fov_label = QtWidgets.QLabel("60.0°")
        layout.addRow("Field of View:", self.create_slider_layout(self.fov_slider, self.fov_label))
        
        self.defocus_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); self.defocus_slider.setRange(0, 100); self.defocus_slider.setValue(0)
        self.defocus_label = QtWidgets.QLabel("0.0")
        layout.addRow("Defocus Blur:", self.create_slider_layout(self.defocus_slider, self.defocus_label))

        self.cab_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); self.cab_slider.setRange(0, 100); self.cab_slider.setValue(0)
        self.cab_label = QtWidgets.QLabel("0.00")
        layout.addRow("Chromatic Ab.:", self.create_slider_layout(self.cab_slider, self.cab_label))

        self.vignette_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); self.vignette_slider.setRange(0, 100); self.vignette_slider.setValue(0)
        self.vignette_label = QtWidgets.QLabel("0.00")
        layout.addRow("Vignetting:", self.create_slider_layout(self.vignette_slider, self.vignette_label))
        
        group.setLayout(layout)
        return group

    def _create_lighting_group(self):
        group, layout = self._create_group_box("Lighting & Illumination")
        self.brightness_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); self.brightness_slider.setRange(0, 100); self.brightness_slider.setValue(50)
        self.brightness_label = QtWidgets.QLabel("+0.00")
        layout.addRow("Brightness:", self.create_slider_layout(self.brightness_slider, self.brightness_label))

        self.light_dir_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); self.light_dir_slider.setRange(0, 360); self.light_dir_slider.setValue(0)
        self.light_dir_label = QtWidgets.QLabel("0°")
        layout.addRow("Light Direction:", self.create_slider_layout(self.light_dir_slider, self.light_dir_label))

        self.shadow_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); self.shadow_slider.setRange(0, 100); self.shadow_slider.setValue(0)
        self.shadow_label = QtWidgets.QLabel("0.00")
        layout.addRow("Shadows:", self.create_slider_layout(self.shadow_slider, self.shadow_label))

        self.specular_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); self.specular_slider.setRange(0, 100); self.specular_slider.setValue(0)
        self.specular_label = QtWidgets.QLabel("0.00")
        layout.addRow("Specular:", self.create_slider_layout(self.specular_slider, self.specular_label))
        
        group.setLayout(layout)
        return group

    def _create_sensor_group(self):
        group, layout = self._create_group_box("Sensor & Capture")
        self.dist_type_combo = QtWidgets.QComboBox(); self.dist_type_combo.addItems(["None", "Barrel", "Pincushion"])
        layout.addRow("Distortion Type:", self.dist_type_combo)

        self.dist_intensity_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); self.dist_intensity_slider.setRange(0, 100); self.dist_intensity_slider.setValue(0)
        self.dist_intensity_label = QtWidgets.QLabel("0.00")
        layout.addRow("Distortion:", self.create_slider_layout(self.dist_intensity_slider, self.dist_intensity_label))
        
        self.noise_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); self.noise_slider.setRange(0, 100); self.noise_slider.setValue(0)
        self.noise_label = QtWidgets.QLabel("0.00")
        layout.addRow("Noise Level:", self.create_slider_layout(self.noise_slider, self.noise_label))

        self.exposure_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); self.exposure_slider.setRange(0, 100); self.exposure_slider.setValue(50)
        self.exposure_label = QtWidgets.QLabel("1.00x")
        layout.addRow("Exposure:", self.create_slider_layout(self.exposure_slider, self.exposure_label))
        
        self.dr_slider = RangeSlider(QtCore.Qt.Orientation.Horizontal); self.dr_slider.setRange(0, 255); self.dr_slider.setValues(0, 255)
        self.dr_label = QtWidgets.QLabel("0-255")
        layout.addRow("Dynamic Range:", self.create_slider_layout(self.dr_slider, self.dr_label))

        self.sensor_type_combo = QtWidgets.QComboBox(); self.sensor_type_combo.addItems(["CMOS", "CCD", "sCMOS"])
        layout.addRow("Sensor Type:", self.sensor_type_combo)

        self.res_combo = QtWidgets.QComboBox(); self.res_combo.addItems(["Unchanged", "1920 x 1080", "1280 x 720", "640 x 480"])
        layout.addRow("Resolution:", self.res_combo)

        self.cfa_check = QtWidgets.QCheckBox("Simulate Bayer Pattern (CFA)"); self.cfa_check.setStyleSheet("color: #e5e7eb;")
        layout.addRow(self.cfa_check)
        
        group.setLayout(layout)
        return group

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Image Simulator")
    
    def init_backend_connections(self, params_manager: ParamsManager):
        self.params_manager = params_manager
        self.load_image_button.clicked.connect(self.load_input_image)

        self.zoom_slider.valueChanged.connect(lambda v: self.zoom_label.setText(f"{v/100.0:.2f}x"))
        self.fov_slider.valueChanged.connect(lambda v: self.fov_label.setText(f"{v:.1f}°"))
        self.dist_intensity_slider.valueChanged.connect(lambda v: self.dist_intensity_label.setText(f"{v/100.0:.2f}"))
        self.defocus_slider.valueChanged.connect(lambda v: self.defocus_label.setText(f"{v/10.0:.1f}"))
        self.cab_slider.valueChanged.connect(lambda v: self.cab_label.setText(f"{v/100.0:.2f}"))
        self.vignette_slider.valueChanged.connect(lambda v: self.vignette_label.setText(f"{v/100.0:.2f}"))
        self.brightness_slider.valueChanged.connect(lambda v: self.brightness_label.setText(f"{(v-50)/50.0:+.2f}"))
        self.light_dir_slider.valueChanged.connect(lambda v: self.light_dir_label.setText(f"{v}°"))
        self.shadow_slider.valueChanged.connect(lambda v: self.shadow_label.setText(f"{v/100.0:.2f}"))
        self.specular_slider.valueChanged.connect(lambda v: self.specular_label.setText(f"{v/100.0:.2f}"))
        self.noise_slider.valueChanged.connect(lambda v: self.noise_label.setText(f"{v/100.0:.2f}"))
        self.exposure_slider.valueChanged.connect(lambda v: self.exposure_label.setText(f"{v/50.0:.2f}x"))
        self.dr_slider.valueChanged.connect(lambda: self.dr_label.setText(f"{self.dr_slider.low()}-{self.dr_slider.high()}"))

        sliders = [self.zoom_slider, self.fov_slider, self.dist_intensity_slider, self.defocus_slider, self.cab_slider, self.vignette_slider, self.brightness_slider, self.light_dir_slider, self.shadow_slider, self.specular_slider, self.noise_slider, self.exposure_slider, self.dr_slider]
        for slider in sliders:
            slider.sliderReleased.connect(self.update_params)
        
        combos = [self.dist_type_combo, self.sensor_type_combo, self.res_combo]
        for combo in combos:
            combo.currentTextChanged.connect(self.update_params)
            
        self.cfa_check.toggled.connect(self.update_params)
        self.params_manager.sim_updated.connect(self.update_displays)
        self.update_displays()

    def load_input_image(self):
        file_path, _ = QFileDialog.getOpenFileName(None, "Open Input Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            img = cv2.imread(file_path)
            if img is not None:
                self.params_manager.update({'input_img': img})
            else:
                print(f"Failed to load image: {file_path}")

    def update_params(self):
        if self.params_manager.get('input_img') is None: return

        w, h = self.params_manager.get('input_img').shape[1], self.params_manager.get('input_img').shape[0]
        res_selection = self.res_combo.currentText()
        low, high = self.dr_slider.getValues()

        current_params = {
            'zoom': self.zoom_slider.value() / 100.0, 'fov': self.fov_slider.value(),
            'distortion_type': self.dist_type_combo.currentText(), 'distortion_intensity': self.dist_intensity_slider.value() / 100.0,
            'defocus': self.defocus_slider.value() / 10.0, 'chromatic_aberration': self.cab_slider.value() / 100.0,
            'vignetting': self.vignette_slider.value() / 100.0, 'brightness': self.brightness_slider.value(),
            'light_direction': self.light_dir_slider.value(), 'shadows': self.shadow_slider.value() / 100.0,
            'specular': self.specular_slider.value() / 100.0, 'noise_level': self.noise_slider.value() / 100.0,
            'exposure': self.exposure_slider.value(), 'dynamic_range': (low, high),
            'sensor_type': self.sensor_type_combo.currentText(), 'resolution': f"{w} x {h}" if res_selection == "Unchanged" else res_selection,
            'cfa': self.cfa_check.isChecked(),
        }
        self.params_manager.update(current_params)

    def update_displays(self):
        self.zoom_slider.setValue(int(self.params_manager.get('zoom', 1.0) * 100))
        self.fov_slider.setValue(int(self.params_manager.get('fov', 60)))
        self.dist_type_combo.setCurrentText(self.params_manager.get('distortion_type', 'None'))
        self.dist_intensity_slider.setValue(int(self.params_manager.get('distortion_intensity', 0) * 100))
        self.defocus_slider.setValue(int(self.params_manager.get('defocus', 0) * 10))
        self.cab_slider.setValue(int(self.params_manager.get('chromatic_aberration', 0) * 100))
        self.vignette_slider.setValue(int(self.params_manager.get('vignetting', 0) * 100))
        self.brightness_slider.setValue(int(self.params_manager.get('brightness', 50)))
        self.light_dir_slider.setValue(int(self.params_manager.get('light_direction', 0)))
        self.shadow_slider.setValue(int(self.params_manager.get('shadows', 0) * 100))
        self.specular_slider.setValue(int(self.params_manager.get('specular', 0) * 100))
        self.noise_slider.setValue(int(self.params_manager.get('noise_level', 0) * 100))
        self.exposure_slider.setValue(int(self.params_manager.get('exposure', 50)))
        dr_low, dr_high = self.params_manager.get('dynamic_range', (0, 255))
        self.dr_slider.setValues(dr_low, dr_high)
        self.sensor_type_combo.setCurrentText(self.params_manager.get('sensor_type', 'CMOS'))
        self.res_combo.setCurrentText(self.params_manager.get('resolution', 'Unchanged'))
        self.cfa_check.setChecked(self.params_manager.get('cfa', False))

        input_img = self.params_manager.get('input_img')
        sim_img = self.params_manager.get('sim_img')

        if input_img is not None:
            self.original_image_label.setPixmap(np_to_qt_pixmap(input_img))
        else:
            self.original_image_label.setPixmap(QtGui.QPixmap())

        if sim_img is not None:
            self.simulated_image_label.setPixmap(np_to_qt_pixmap(sim_img))
        else:
            self.simulated_image_label.setPixmap(QtGui.QPixmap())