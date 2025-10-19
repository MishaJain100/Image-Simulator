# home_panel.py
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
import cv2
from backend.utils import np_to_qt_pixmap
import resources_rc  # Loads fonts/icons
from ui_components import ScalableImageLabel

class HomeWidget(QtWidgets.QWidget):
    def __init__(self, params_manager, engine):
        super().__init__()
        self.engine = engine
        self.params_manager = params_manager
        self.space_grotesk = self._load_font()
        self.setup_ui()
        self.init_connections()

    def _load_font(self):
        try:
            font_db = QtGui.QFontDatabase()
            font_id = font_db.addApplicationFont(":/fonts/resources/fonts/SpaceGrotesk.ttf")
            families = font_db.applicationFontFamilies(font_id)
            return QtGui.QFont(families[0], 10) if families else QtGui.QFont("Arial", 10)
        except:
            return QtGui.QFont("Arial", 10)

    def setup_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Left: Controls
        control = QtWidgets.QWidget()
        control.setStyleSheet("background-color: #0f1b23;")
        control.setMaximumWidth(400)
        v_layout = QtWidgets.QVBoxLayout(control)
        v_layout.setContentsMargins(24, 24, 24, 24)
        v_layout.setSpacing(30)

        # Header
        header = QtWidgets.QWidget()
        h_layout = QtWidgets.QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)
        icon_btn = QtWidgets.QPushButton()
        icon_btn.setStyleSheet("background-color: #1193d4; color: white; padding: 6px; border: 2px solid #1193d4; border-radius: 8px;")
        icon = QtGui.QIcon(":/icons/resources/icons/photo_camera.svg")
        icon_btn.setIcon(icon)
        icon_btn.setIconSize(QtCore.QSize(28, 28))
        h_layout.addWidget(icon_btn)
        title = QtWidgets.QLabel("Image Simulator")
        title.setStyleSheet("color: white; font-weight: bold; font-size: 28px;")
        title.setFont(self.space_grotesk)
        h_layout.addWidget(title)
        h_layout.addStretch()
        v_layout.addWidget(header)

        self.load_btn = QtWidgets.QPushButton("Load Input Image...")
        self.load_btn.setStyleSheet("QPushButton { background-color: #1193d4; color: #ffffff; font-size: 14px; padding: 8px 0px; border-radius: 4px; border: none; } QPushButton:hover { background-color: #15a4e5; }")
        self.load_btn.setFont(self.space_grotesk)
        v_layout.addWidget(self.load_btn)
        v_layout.addStretch()

        layout.addWidget(control)

        # Right: Displays
        display_window = QtWidgets.QWidget()
        display_layout = QtWidgets.QHBoxLayout(display_window)
        display_layout.setContentsMargins(24, 24, 24, 24)

        self.original_widget = self._create_image_display("Original Image", ":/images/resources/images/original_default.png")
        self.simulated_widget = self._create_image_display("Simulated Image", ":/images/resources/images/simulated_default.png")
        display_layout.addWidget(self.original_widget)
        display_layout.addWidget(self.simulated_widget)

        layout.addWidget(display_window)
        layout.setStretch(0, 1)
        layout.setStretch(1, 3)

        # Find labels for updates
        self.original_image_label = self.original_widget.findChild(ScalableImageLabel)
        self.simulated_image_label = self.simulated_widget.findChild(ScalableImageLabel)

    def _create_image_display(self, title, default_path):
        widget = QtWidgets.QWidget()
        v_layout = QtWidgets.QVBoxLayout(widget)
        v_layout.setContentsMargins(15, 15, 15, 15)
        
        label = QtWidgets.QLabel(title)
        label.setStyleSheet("border: None; color: white; font-size: 18px; font-weight: 600;")
        label.setFont(self.space_grotesk)
        v_layout.addWidget(label)
        
        image_label = ScalableImageLabel()
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        image_label.setSizePolicy(size_policy)
        image_label.setStyleSheet("border: 1px solid #243447; border-radius: 8px;")
        default_pix = QtGui.QPixmap(default_path)
        image_label.setPixmap(default_pix if not default_pix.isNull() else QtGui.QPixmap())
        image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        v_layout.addWidget(image_label)
        v_layout.setStretch(1, 1)
        return widget

    def init_connections(self):
        self.load_btn.clicked.connect(self.load_input_image)
        self.params_manager.sim_updated.connect(self.update_displays)
        self.update_displays()

    def load_input_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Input Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            img = cv2.imread(file_path)
            if img is not None:
                self.params_manager.set('input_img', img)
                self.update_displays()
            else:
                print(f"Failed to load image: {file_path}")

    def update_displays(self):
        input_img = self.params_manager.get('input_img')
        if input_img is not None:
            all_params = self.params_manager.get_params()
            sim_img = self.engine.run_pipeline(input_img.copy(), all_params)
            self.params_manager.set('sim_img', sim_img)
            
            if self.original_image_label:
                self.original_image_label.setPixmap(np_to_qt_pixmap(input_img))
            if self.simulated_image_label:
                self.simulated_image_label.setPixmap(np_to_qt_pixmap(sim_img))