from PyQt5 import QtWidgets
from distortion_presets_and_customization import Ui_MainWindow as Ui_DistortionPresetsAndCustomization

class DistortionPresetsAndCustomizationLogic(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_DistortionPresetsAndCustomization()
        self.ui.setupUi(self)
        self.connect_signals()

    def connect_signals(self):
        pass
        # self.ui.UploadButton.clicked.connect(self.upload_image)
        # self.ui.UploadIcon.clicked.connect(self.upload_image)
        # self.ui.ConstraintsText.clicked.connect(self.upload_image)

    def upload_image(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select an Image", "", "Images (*.png *.jpg *.jpeg *.svg)", options=options)
        if file_name:
            print(f"Selected file: {file_name}")
        else:
            print("No file selected.")