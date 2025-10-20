from PyQt5 import QtWidgets
from sensor_and_noise_parameter import Ui_MainWindow as Ui_SensorAndNoiseParameter 

class SensorAndNoiseParameterLogic(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_SensorAndNoiseParameter()
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