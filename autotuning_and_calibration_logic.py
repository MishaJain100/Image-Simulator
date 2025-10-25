from PyQt5 import QtWidgets, QtCore
from autotuning_and_calibration import Ui_MainWindow as Ui_AutotuningAndCalibration
import cv2
import numpy as np
from tuning_thread import TuningThread
from base_image_generator import CameraSimulator

class AutotuningAndCalibrationLogic(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_AutotuningAndCalibration()
        self.ui.setupUi(self)
        self.reset()
        self.connect_signals()

        self.imgs = None
        self.tuning_thread = None
        self.is_tuning_running = False

    def reset(self):
        _translate = QtCore.QCoreApplication.translate
        self.ui.UploadButton.setText(_translate("MainWindow", "Click to upload or drag and drop"))
        self.ui.ConstraintsText.setText(_translate("MainWindow", "SVG, PNG, JPG or GIF (max. 800x400px)"))
        self.imgs = None
        self.tuning_thread = None
        self.ui.StartTuning.setText(_translate("MainWindow", "Start Tuning"))
        self.ui.StartTuning.setEnabled(True)
        self.ui.ProgressBar.setValue(0)
        self.estimated_params = None
        self.ui.DistortionNumber.setText(f"0.00")
        self.ui.NoiseNumber.setText(f"0.00")
        self.ui.FLNumber.setText(f"0 mm")
        self.ui.SSNumber.setText(f"0 mm x 0 mm")
        self.is_tuning_running = False
        self.ui.AutoTuningProgress.setText(_translate("MainWindow", "Auto-Tuning Progress"))

    def connect_signals(self):
        self.ui.UploadButton.clicked.connect(self.upload_image)
        self.ui.UploadIcon.clicked.connect(self.upload_image)
        self.ui.ConstraintsText.clicked.connect(self.upload_image)
        self.ui.SelectImages.clicked.connect(self.load_batch_images)
        self.ui.StartTuning.clicked.connect(self.start_tuning)

    def upload_image(self):
        self.reset()
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select an Image", "", "Images (*.png *.jpg *.jpeg *.svg)", options=options)
        if file_name:
            print(f"Selected file: {file_name}")
            self.ui.UploadButton.setText(file_name.split('/')[-1])
            self.ui.ConstraintsText.setText('File Uploaded')
            self.imgs = [file_name]
        else:
            print("No file selected.")
            self.reset()

    def load_batch_images(self):
        self.reset()
        options = QtWidgets.QFileDialog.Options()
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Batch Images", "", "Images (*.png *.jpg *.jpeg *.svg)", options=options)
        if files:
            self.imgs = files
            self.ui.SelectImages.setText(f"{len(files)} images selected")
        else:
            print("No file selected.")
            self.reset()

    def start_tuning(self):
        if self.tuning_thread and self.tuning_thread.isRunning(): 
            return

        # img = cv2.imread(self.imgs[0])
        GT_FOCAL = 50.0
        GT_SENSOR_W = 36.0
        GT_SENSOR_H = 24.0
        GT_DIST = np.array([-0.25, 0.05, 0.001, 0.001, 0.0])
        GT_NOISE = 5.0

        simulator = CameraSimulator(width=800, height=600)
        world_points_3d = simulator.world_points_3d

        base_img_color = simulator.generate_simulated_image(GT_FOCAL, GT_SENSOR_W, GT_SENSOR_H, GT_DIST, GT_NOISE)

        cv2.imwrite('base_img.png', base_img_color)
        base_img_gray = cv2.imread('base_img.png', cv2.IMREAD_GRAYSCALE)

        found, ground_truth_points_2d = cv2.findCirclesGrid(
            base_img_gray,
            (7, 7), 
            flags=cv2.CALIB_CB_SYMMETRIC_GRID 
        )

        GUESS_FOCAL = 35.0 
        GUESS_DIST = np.zeros(5, dtype=np.float32)

        locks = {
            'distortion': self.ui.DistortionPLCB.isChecked(),
            'noise': self.ui.NoisePLCB.isChecked(),
            'focal_length': self.ui.FLPLCB.isChecked()
        }

        defaults = {
            'focal_length': 35.0,
            'sensor_width': 36,
            'sensor_height': 24,
            'distortion': np.zeros(5, dtype=np.float32),
            'noise': 3
        }
        
        self.is_tuning_running = True
        self.ui.StartTuning.setEnabled(False)
        self.ui.StartTuning.setText("Tuning...")
        self.ui.ProgressBar.setValue(0)
        
        self.tuning_thread = TuningThread(ground_truth_points_2d, world_points_3d, locks, defaults)
        self.tuning_thread.progress_updated.connect(self.on_tuning_progress)
        self.tuning_thread.finished.connect(self.on_tuning_finished)
        self.tuning_thread.start()

    def on_tuning_progress(self, value):
        self.ui.ProgressBar.setValue(value)

    def on_tuning_finished(self, estimated_params):
        print ("Thread finished")
        self.is_tuning_running = False
        self.ui.StartTuning.setEnabled(True)
        self.ui.StartTuning.setText("Start Tuning")
        self.ui.AutoTuningProgress.setText("Auto-Tuning Complete")
        self.ui.ProgressBar.setValue(100)
        
        self.estimated_params = estimated_params
        
        dist = self.estimated_params['distortion']
        noise = self.estimated_params.get('noise', 3.0)
        sw = self.estimated_params['sensor_width']
        sh = self.estimated_params['sensor_height']
        fl = self.estimated_params['focal_length']

        self.ui.DistortionNumber.setText(f"{list([f"{d:.2f}" for d in dist])}")
        self.ui.NoiseNumber.setText(f"{noise:.2f}")
        self.ui.FLNumber.setText(f"{fl:.2f} mm")
        self.ui.SSNumber.setText(f"{sw:.2f} mm x {sh:.2f}mm")

    def apply_parameters(self):
        if not self.estimated_params: 
            return
        # self.params_manager.update(self.estimated_params_cache)
        # self.AutoTuningProgress.setText("Parameters applied to all panels!")