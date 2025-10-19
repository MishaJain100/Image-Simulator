# autotuning_and_calibration.py
from PyQt5 import QtCore, QtGui, QtWidgets
import cv2
from PyQt5.QtWidgets import QFileDialog
from backend.utils import ParamsManager
from backend.calibration import TuningThread
import resources_rc

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
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.Scrollers)
        
        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        self.Icon = QtWidgets.QPushButton()
        self.Icon.setIcon(QtGui.QIcon(":/icons/resources/icons/photo_camera.svg"))
        self.Icon.setIconSize(QtCore.QSize(28, 28))
        self.Icon.setStyleSheet("background-color: #1193d4; color: white; padding: 6px; border-radius: 8px;")
        header_layout.addWidget(self.Icon)
        title_label = QtWidgets.QLabel("Auto-Tuning & Calibration")
        title_label.setFont(self.space_grotesk)
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 28px;")
        header_layout.addWidget(title_label)
        self.verticalLayout_2.addWidget(header_widget)
        
        self.Parameters = QtWidgets.QWidget(self.Scrollers)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.Parameters)
        self.UploadButton = QtWidgets.QPushButton("Upload Reference Image")
        self.SelectImages = QtWidgets.QPushButton("Select Batch Images")
        self.StartTuning = QtWidgets.QPushButton("Start Tuning")
        self.ProgressBar = QtWidgets.QProgressBar()
        self.DistortionPLCB = QtWidgets.QCheckBox("Lock Distortion")
        self.NoisePLCB = QtWidgets.QCheckBox("Lock Noise")
        self.FLPLCB = QtWidgets.QCheckBox("Lock Focal Length/Zoom")
        self.DistortionNumber = QtWidgets.QLabel("0.00")
        self.NoiseNumber = QtWidgets.QLabel("0.00")
        self.FLNumber = QtWidgets.QLabel("0 mm")
        self.SSNumber = QtWidgets.QLabel("0 mm x 0 mm")
        self.FLLabel = QtWidgets.QLabel("Focal Length")
        self.SSLabel = QtWidgets.QLabel("Sensor Size")
        self.ApplyParameters = QtWidgets.QPushButton("Apply Parameters")
        self.AutoTuningProgress = QtWidgets.QLabel("Auto-Tuning Progress")

        self.verticalLayout_6.addWidget(self.UploadButton)
        self.verticalLayout_6.addWidget(self.SelectImages)
        self.verticalLayout_6.addWidget(self.StartTuning)
        self.verticalLayout_6.addWidget(self.ProgressBar)
        self.verticalLayout_6.addWidget(self.DistortionPLCB)
        self.verticalLayout_6.addWidget(self.NoisePLCB)
        self.verticalLayout_6.addWidget(self.FLPLCB)
        self.verticalLayout_6.addWidget(self.FLLabel)
        self.verticalLayout_6.addWidget(self.FLNumber)
        self.verticalLayout_6.addWidget(self.SSLabel)
        self.verticalLayout_6.addWidget(self.SSNumber)
        self.verticalLayout_6.addWidget(self.ApplyParameters)
        self.verticalLayout_6.addWidget(self.AutoTuningProgress)
        
        self.verticalLayout_2.addWidget(self.Parameters)
        self.horizontalLayout.addWidget(self.Scrollers)

        self.ImageWindow = QtWidgets.QWidget(self.centralwidget)
        self.ImageWindow.setStyleSheet("background-color: #0f1b23; border-left: 1px solid #2d3748;")
        self.horizontalLayout.addWidget(self.ImageWindow)

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle("Image Simulator")

    def init_backend_connections(self, params_manager: ParamsManager):
        self.params_manager = params_manager
        self.tuning_thread = None
        self.estimated_params_cache = {}

        self.parent_window = self.centralwidget.parentWidget()

        self.UploadButton.clicked.connect(self.load_calib_image)
        self.SelectImages.clicked.connect(self.load_batch_images)
        self.StartTuning.clicked.connect(self.start_tuning)
        self.ApplyParameters.clicked.connect(self.apply_parameters)

    def load_calib_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self.parent_window, "Open Reference Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            img = cv2.imread(file_path)
            if img is not None:
                self.params_manager.set('real_img', img)
                self.UploadButton.setText(file_path.split('/')[-1])
            else:
                self.UploadButton.setText("Failed to load image")

    def load_batch_images(self):
        files, _ = QFileDialog.getOpenFileNames(self.parent_window, "Open Batch Images", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if files:
            batch_imgs = [cv2.imread(f) for f in files if cv2.imread(f) is not None]
            self.params_manager.set('batch_imgs', batch_imgs)
            self.SelectImages.setText(f"{len(batch_imgs)} images selected")
            self.params_manager.set('real_img', None) 
            self.UploadButton.setText("Upload Reference Image")

    def start_tuning(self):
        if self.tuning_thread and self.tuning_thread.isRunning(): return

        input_img = self.params_manager.get('input_img')
        ref_img = self.params_manager.get('real_img')
        batch_imgs = self.params_manager.get('batch_imgs', [])

        if ref_img is None and not batch_imgs:
            self.AutoTuningProgress.setText("Load a reference image or batch first!")
            return
            
        if input_img is None:
            self.AutoTuningProgress.setText("Load an *input* image on the main panel first!")
            return

        locks = {
            'distortion_intensity': self.DistortionPLCB.isChecked(),
            'noise_level': self.NoisePLCB.isChecked(),
            'zoom': self.FLPLCB.isChecked(), 
            'fov': self.FLPLCB.isChecked(),
        }

        self.StartTuning.setEnabled(False)
        self.StartTuning.setText("Tuning...")
        self.ProgressBar.setValue(0)
        self.AutoTuningProgress.setText("Auto-Tuning Progress")
        
        effective_ref = ref_img if ref_img is not None else batch_imgs[0]

        self.tuning_thread = TuningThread(self.params_manager.engine, input_img, effective_ref, locks, batch_imgs)
        self.tuning_thread.progress_updated.connect(self.on_tuning_progress)
        self.tuning_thread.finished.connect(self.on_tuning_finished)
        self.tuning_thread.start()

    def on_tuning_progress(self, value):
        self.ProgressBar.setValue(value)

    def on_tuning_finished(self, estimated_params: dict):
        self.StartTuning.setEnabled(True)
        self.StartTuning.setText("Start Tuning")
        self.AutoTuningProgress.setText("Auto-Tuning Complete")
        self.ProgressBar.setValue(100)
        
        self.estimated_params_cache = estimated_params
        
        dist = estimated_params.get('distortion_intensity', 0.0)
        noise = estimated_params.get('noise_level', 0.0)
        zoom = estimated_params.get('zoom', 1.0)
        fov = estimated_params.get('fov', 60.0)
        
        self.DistortionNumber.setText(f"{dist:.3f}")
        self.NoiseNumber.setText(f"{noise:.3f}")
        self.FLLabel.setText("Zoom (Est.)")
        self.FLNumber.setText(f"{zoom:.2f}x")
        self.SSLabel.setText("Field of View (Est.)")
        self.SSNumber.setText(f"{fov:.1f}°")

    def apply_parameters(self):
        if not self.estimated_params_cache: return
        self.params_manager.update(self.estimated_params_cache)
        self.AutoTuningProgress.setText("Parameters applied to all panels!")