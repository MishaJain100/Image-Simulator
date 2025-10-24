from PyQt5 import QtWidgets, QtCore
from autotuning_and_calibration import Ui_MainWindow as Ui_AutotuningAndCalibration
import cv2
from tuning_thread import TuningThread

class AutotuningAndCalibrationLogic(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_AutotuningAndCalibration()
        self.ui.setupUi(self)
        self.reset()
        self.connect_signals()

        self.imgs = None
        self.tuning_thread = None

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
        
        print ("Clicked Start tuning")

        locks = {
            'distortion': self.ui.DistortionPLCB.isChecked(),
            'noise': self.ui.NoisePLCB.isChecked(),
            'focal_length': self.ui.FLPLCB.isChecked()
        }
        
        self.ui.StartTuning.setEnabled(False)
        self.ui.StartTuning.setText("Tuning...")
        self.ui.ProgressBar.setValue(0)
        
        self.tuning_thread = TuningThread(self.imgs, locks)
        self.tuning_thread.progress_updated.connect(self.on_tuning_progress)
        self.tuning_thread.finished.connect(self.on_tuning_finished)
        self.tuning_thread.start()

    def on_tuning_progress(self, value):
        self.ui.ProgressBar.setValue(value)

    def on_tuning_finished(self, estimated_params):
        print ("Thread finished")
        self.ui.StartTuning.setEnabled(True)
        self.ui.StartTuning.setText("Start Tuning")
        self.ui.AutoTuningProgress.setText("Auto-Tuning Complete")
        self.ui.ProgressBar.setValue(100)
        
        self.estimated_params = estimated_params
        
        dist = self.estimated_params['distortion']
        noise = self.estimated_params['noise']
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