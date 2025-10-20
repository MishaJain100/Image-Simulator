from PyQt5 import QtWidgets
from comparison_and_metrics_display import Ui_MainWindow as Ui_ComparisonAndMetricsDisplay

class ComparisonAndMetricsDisplayLogic(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ComparisonAndMetricsDisplay()
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