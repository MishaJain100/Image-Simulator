import sys
from PyQt5 import QtCore, QtWidgets
from simulator_control_panel_logic import SimulatorControlPanelLogic
from sensor_and_noise_parameter_logic import SensorAndNoiseParameterLogic
from distortion_presets_and_customization_logic import DistortionPresetsAndCustomizationLogic
from comparison_and_metrics_display_logic import ComparisonAndMetricsDisplayLogic
from autotuning_and_calibration_logic import AutotuningAndCalibrationLogic

MENU_WIDTH = 250

class AppWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        global_stylesheet = """
            QSlider::groove:horizontal {
                background-color: #4a5568;
                border: 0px solid #4a5568;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background-color: #1193d4;
                border: 0px solid #1193d4;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -5px 0px;
            }
            QSlider::handle:horizontal:hover {
                background-color: #15a4e5;
            }
        """
        self.setStyleSheet(global_stylesheet)
        self.current_controller = None
        self.menu_frame = QtWidgets.QFrame(self)
        self.menu_frame.setGeometry(QtCore.QRect(-MENU_WIDTH, 0, MENU_WIDTH, self.height()))
        self.menu_frame.setStyleSheet("background-color: #0f1b23; border-right: 1px solid #1e293b;")
        self._create_menu_buttons()
        self.menu_animation = QtCore.QPropertyAnimation(self.menu_frame, b"geometry")
        self.menu_animation.setDuration(250)
        self.menu_animation.setEasingCurve(QtCore.QEasingCurve.InOutCubic)
        self.menu_frame.raise_()

        self.img = None
        self.img_display_size = None
        self.autotuned_params = None
        self.current_params = {
            'zoom': 0,
            'fov': 60,
            'distortion': 0,
            'brightness': 0,
            'ld': 45,
            'shadows': 0,
            'noise': 0,
            'exposure': 50
        }

        self._switch_ui(SimulatorControlPanelLogic)

    def _create_menu_buttons(self):
        self.menu_layout = QtWidgets.QVBoxLayout(self.menu_frame)
        self.menu_layout.setContentsMargins(10, 50, 10, 10)
        self.menu_layout.setSpacing(10)
        self.menu_layout.setAlignment(QtCore.Qt.AlignTop)
        self.menu_map = {
            "Simulator Control Panel": SimulatorControlPanelLogic,
            "Sensor and Noise Parameters": SensorAndNoiseParameterLogic,
            "Distortion Presets and Customisation": DistortionPresetsAndCustomizationLogic,
            "Comparison and Metrics Display": ComparisonAndMetricsDisplayLogic,
            "Auto-Tuning and Calibration": AutotuningAndCalibrationLogic
        }
        menu_button_style = """
            QPushButton {
                color: #e5e7eb;
                background-color: transparent;
                border: none;
                padding: 10px;
                border-radius: 4px;
                text-align: left;
                font-family: SpaceGrotesk;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1e293b;
            }
        """
        for option_text in self.menu_map.keys():
            button = QtWidgets.QPushButton(option_text, self)
            button.setStyleSheet(menu_button_style)
            button.clicked.connect(self.on_menu_button_clicked)
            self.menu_layout.addWidget(button)

    def on_menu_button_clicked(self):
        clicked_button = self.sender()
        ui_class_to_load = self.menu_map.get(clicked_button.text())
        if ui_class_to_load:
            self._switch_ui(ui_class_to_load)
        if self.menu_frame.x() == 0:
            self.toggle_menu()

    def _switch_ui(self, logic_class):
        if hasattr(logic_class, "__init__") and "img" in logic_class.__init__.__code__.co_varnames:
            self.current_controller = logic_class(self, img=self.img, img_size=self.img_display_size)
        else:
            self.current_controller = logic_class(self)

        content_widget = self.current_controller.centralWidget()
        content_widget.setParent(self)
        self.setCentralWidget(content_widget)
        menu_button = self.centralWidget().findChild(QtWidgets.QPushButton, "Icon")
        if menu_button:
            try:
                menu_button.clicked.disconnect()
            except TypeError:
                pass
            menu_button.clicked.connect(self.toggle_menu)
        
        self.centralWidget().installEventFilter(self)

    def eventFilter(self, source, event):
        if self.menu_frame.x() == 0 and event.type() == QtCore.QEvent.MouseButtonPress:
            if source is self.centralWidget():
                self.toggle_menu()
                return True
        return super().eventFilter(source, event)

    def toggle_menu(self):
        self.menu_frame.raise_()
        current_x = self.menu_frame.x()
        if current_x < 0:
            end_pos = QtCore.QRect(0, 0, MENU_WIDTH, self.height())
        else:
            end_pos = QtCore.QRect(-MENU_WIDTH, 0, MENU_WIDTH, self.height())
        self.menu_animation.setStartValue(self.menu_frame.geometry())
        self.menu_animation.setEndValue(end_pos)
        self.menu_animation.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.menu_frame.raise_()
        current_x = self.menu_frame.x()
        if current_x < 0:
            self.menu_frame.setGeometry(-MENU_WIDTH, 0, MENU_WIDTH, self.height())
        else:
            self.menu_frame.setGeometry(0, 0, MENU_WIDTH, self.height())

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec_())