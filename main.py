# main.py
import sys
from PyQt5 import QtCore, QtWidgets, QtGui

# Import all five of your UI panel classes
from simulator_control_panel import Ui_MainWindow as Ui_SimulatorControlPanel
from sensor_and_noise_parameter import Ui_MainWindow as Ui_SensorAndNoise
from distortion_presets_and_customization import Ui_MainWindow as Ui_Distortion
from comparison_and_metrics_display import Ui_MainWindow as Ui_Comparison
from autotuning_and_calibration import Ui_MainWindow as Ui_AutoTuning

from backend.simulator_engine import SimulatorEngine
from backend.utils import ParamsManager

MENU_WIDTH = 320 # Increased width for longer names

class AppWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # Create a SINGLE, shared instance of the engine and params manager
        self.engine = SimulatorEngine()
        # IMPORTANT: The engine is now passed to the manager to handle simulation runs
        self.params_manager = ParamsManager(self.engine)
        self.current_ui_instance = None

        self.setup_main_window()
        self._create_menu_buttons()
        self.menu_animation = self.setup_menu_animation()

        # Load the main control panel by default
        self._switch_ui(Ui_SimulatorControlPanel)
        self.menu_frame.raise_()

    def setup_main_window(self):
        self.setWindowTitle("Image Simulator Application")
        self.resize(1600, 1000)
        self.menu_frame = QtWidgets.QFrame(self)
        self.menu_frame.setGeometry(QtCore.QRect(-MENU_WIDTH, 0, MENU_WIDTH, self.height()))
        self.menu_frame.setStyleSheet("background-color: #0f1b23; border-right: 1px solid #1e293b;")
        self.menu_frame.setObjectName("SideMenuFrame")

    def setup_menu_animation(self):
        animation = QtCore.QPropertyAnimation(self.menu_frame, b"geometry")
        animation.setDuration(250)
        animation.setEasingCurve(QtCore.QEasingCurve.Type.InOutCubic)
        return animation

    def _create_menu_buttons(self):
        self.menu_layout = QtWidgets.QVBoxLayout(self.menu_frame)
        self.menu_layout.setContentsMargins(10, 50, 10, 10)
        self.menu_layout.setSpacing(10)
        self.menu_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.menu_map = {
            "Simulator Control Panel": Ui_SimulatorControlPanel,
            "Sensor and Noise Parameters": Ui_SensorAndNoise,
            "Distortion Presets and Customization": Ui_Distortion,
            "Comparison and Metrics Display": Ui_Comparison,
            "Auto-Tuning and Calibration": Ui_AutoTuning
        }
        
        menu_button_style = """
            QPushButton { color: #e5e7eb; background-color: transparent; border: none; padding: 10px; border-radius: 4px; text-align: left; font-size: 14px; }
            QPushButton:hover { background-color: #1e293b; }
            QPushButton:pressed { background-color: #0f3345; }
        """

        for option_text, ui_class in self.menu_map.items():
            button = QtWidgets.QPushButton(option_text, self.menu_frame)
            button.setStyleSheet(menu_button_style)
            button.clicked.connect(lambda checked, cls=ui_class: self.on_menu_button_clicked(cls))
            self.menu_layout.addWidget(button)

        self.menu_layout.addStretch()

    def on_menu_button_clicked(self, ui_class_to_load):
        self._switch_ui(ui_class_to_load)
        if self.menu_frame.x() == 0:
            self.toggle_menu()

    def _switch_ui(self, ui_class):
        temp_window = QtWidgets.QMainWindow()
        new_ui_instance = ui_class()
        new_ui_instance.setupUi(temp_window)

        new_central_widget = temp_window.centralWidget()
        new_central_widget.setParent(self)
        
        self.current_ui_instance = new_ui_instance

        menu_toggle_button = new_central_widget.findChild(QtWidgets.QPushButton, "Icon")
        if menu_toggle_button:
            try:
                menu_toggle_button.clicked.disconnect()
            except TypeError: pass
            menu_toggle_button.clicked.connect(self.toggle_menu)

        if hasattr(new_ui_instance, 'init_backend_connections'):
            new_ui_instance.init_backend_connections(self.params_manager)

        old_central_widget = self.centralWidget()
        if old_central_widget:
            old_central_widget.setParent(None)
            old_central_widget.deleteLater()

        self.setCentralWidget(new_central_widget)
        self.menu_frame.raise_()

    def toggle_menu(self):
        self.menu_frame.raise_()
        start_pos = self.menu_frame.geometry()
        end_pos = QtCore.QRect(0, 0, MENU_WIDTH, self.height()) if start_pos.x() < 0 else QtCore.QRect(-MENU_WIDTH, 0, MENU_WIDTH, self.height())

        self.menu_animation.setStartValue(start_pos)
        self.menu_animation.setEndValue(end_pos)
        self.menu_animation.start()

    def resizeEvent(self, event: QtGui.QResizeEvent):
        super().resizeEvent(event)
        new_height = self.height()
        current_x = self.menu_frame.x()
        self.menu_frame.setGeometry(current_x, 0, MENU_WIDTH, new_height)
        self.menu_frame.raise_()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec_())