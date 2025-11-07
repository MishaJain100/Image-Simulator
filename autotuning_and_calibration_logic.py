from PyQt5 import QtWidgets, QtCore
from autotuning_and_calibration import Ui_MainWindow as Ui_AutotuningAndCalibration
import cv2
import numpy as np
from tuning_thread import TuningThread
import os

class AutotuningAndCalibrationLogic(QtWidgets.QMainWindow):
    # --- FIXED CONSTRUCTOR ---
    # It now correctly receives img and img_size from main.py
    def __init__(self, parent=None, img=None, img_size=None):
        super().__init__(parent)
        self.ui = Ui_AutotuningAndCalibration()
        self.ui.setupUi(self)
        
        # Base image is now uploaded independently (fallback to parent if needed, but prioritize upload)
        self.base_image_path = None
        self.base_image = None
        
        self.target_image_path = None
        self.target_image = None
        
        self.tuning_thread = None
        self.is_tuning_running = False

        self.reset()
        self.connect_signals()

    def reset(self):
        _translate = QtCore.QCoreApplication.translate
        
        # Reset the base image upload button
        self.ui.BaseUploadButton.setText(_translate("MainWindow", "Click to upload Base Image..."))
        self.ui.BaseConstraintsText.setText(_translate("MainWindow", "SVG, PNG, JPG or GIF (max. 800x400px)"))
        
        # Reset the target image upload button
        self.ui.UploadButton.setText(_translate("MainWindow", "Click to upload Target Image..."))
        self.ui.ConstraintsText.setText(_translate("MainWindow", "SVG, PNG, JPG or GIF (max. 800x400px)"))
        
        self.base_image_path = None
        self.base_image = None
        self.target_image_path = None
        self.target_image = None

        self.tuning_thread = None
        self.ui.StartTuning.setText(_translate("MainWindow", "Start Tuning"))
        self.ui.StartTuning.setEnabled(True)
        self.ui.ProgressBar.setValue(0)
        self.ui.ProgressPercent.setText("0%")
        self.estimated_params = None
        
        # Reset labels
        self.ui.DistortionNumber.setText(f"0.00")
        self.ui.FLNumber.setText(f"0")
        self.ui.SSNumber.setText(f"0 x 0")
        
        self.is_tuning_running = False
        self.ui.AutoTuningProgress.setText(_translate("MainWindow", "Auto-Tuning Progress"))

    def connect_signals(self):
        # Connect the base image upload buttons
        self.ui.BaseUploadButton.clicked.connect(self.upload_base_image)
        self.ui.BaseUploadIcon.clicked.connect(self.upload_base_image)
        self.ui.BaseConstraintsText.clicked.connect(self.upload_base_image)
        
        # Connect the target image upload buttons
        self.ui.UploadButton.clicked.connect(self.upload_target_image)
        self.ui.UploadIcon.clicked.connect(self.upload_target_image)
        self.ui.ConstraintsText.clicked.connect(self.upload_target_image)
        
        self.ui.StartTuning.clicked.connect(self.start_tuning)
        # self.ui.ApplyParameters.clicked.connect(self.apply_parameters)

    def upload_base_image(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Base Image (Clean/Undistorted)", "", "Images (*.png *.jpg *.jpeg)", options=options)
        if file_name:
            self.base_image_path = file_name
            self.base_image = cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)
            self.ui.BaseUploadButton.setText(os.path.basename(file_name))
            self.ui.BaseConstraintsText.setText("Base image loaded.")
            print(f"Base image loaded: {file_name}")
        else:
            print("No base image selected.")

    def upload_target_image(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Target Image (Distorted)", "", "Images (*.png *.jpg *.jpeg)", options=options)
        if file_name:
            self.target_image_path = file_name
            self.target_image = cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)
            self.ui.UploadButton.setText(os.path.basename(file_name))
            self.ui.ConstraintsText.setText("Target image loaded.")
            print(f"Target image loaded: {file_name}")
        else:
            print("No target image selected.")

    def start_tuning(self):
        if self.tuning_thread and self.tuning_thread.isRunning(): 
            return

        # --- Load Base Image (prioritize uploaded, fallback to parent) ---
        if self.base_image is None:
            # Fallback to parent
            self.base_image_path = self.parent().img
            if self.base_image_path is None:
                self.ui.AutoTuningProgress.setText("Error: No base image uploaded or available in main app.")
                return
            
            try:
                self.base_image = cv2.imread(self.base_image_path, cv2.IMREAD_GRAYSCALE)
                if self.base_image is None:
                    raise Exception("Base image could not be read.")
            except Exception as e:
                self.ui.AutoTuningProgress.setText(f"Error: {e}")
                return
        # --- End Base Image Load ---
        
        if self.target_image is None:
            self.ui.AutoTuningProgress.setText("Error: Target image not uploaded.")
            return

        # === MODIFICATION ===
        # Removed the resolution check. This will now be handled by the thread.
        # if self.base_image.shape != self.target_image.shape:
        #     self.ui.AutoTuningProgress.setText("Error: Images must have same resolution.")
        #     return
        # === END MODIFICATION ===

        print("Starting tuning...")

        locks = {
            'distortion': self.ui.DistortionPLCB.isChecked(),
            'focal_length': self.ui.FLPLCB.isChecked()
        }

        h, w = self.base_image.shape
        defaults = {
            'focal_length': w * 0.8, 
            'k1': 0.0,
            'cx': w / 2,
            'cy': h / 2
        }
        
        self.is_tuning_running = True
        self.ui.StartTuning.setEnabled(False)
        self.ui.StartTuning.setText("Tuning...")
        self.ui.ProgressBar.setValue(0)
        self.ui.ProgressPercent.setText("0%")
        
        self.tuning_thread = TuningThread(
            self.base_image, 
            self.target_image, 
            locks, 
            defaults
        )
        self.tuning_thread.progress_updated.connect(self.on_tuning_progress)
        self.tuning_thread.finished.connect(self.on_tuning_finished)
        self.tuning_thread.start()

    def on_tuning_progress(self, value):
        self.ui.ProgressBar.setValue(value)
        self.ui.ProgressPercent.setText(f"{value}%") 

    def on_tuning_finished(self, estimated_params):
        print ("Thread finished")
        self.is_tuning_running = False
        self.ui.StartTuning.setEnabled(True)
        self.ui.StartTuning.setText("Start Tuning")
        self.ui.AutoTuningProgress.setText("Auto-Tuning Complete")
        self.ui.ProgressBar.setValue(100)
        self.ui.ProgressPercent.setText("100%") 
        
        self.estimated_params = estimated_params
        
        fl = self.estimated_params['focal_length']
        k1 = self.estimated_params['k1']
        cx = self.estimated_params['cx']
        cy = self.estimated_params['cy']

        # Update the UI labels with the new, correct parameter names
        self.ui.DistortionNumber.setText(f"{k1:.4f}")
        self.ui.FLNumber.setText(f"{fl:.1f}")
        self.ui.SSNumber.setText(f"{int(cx)} x {int(cy)}")
        
    def apply_parameters(self):
        if not self.estimated_params: 
            return
        
        print("Applying parameters (not implemented):", self.estimated_params)