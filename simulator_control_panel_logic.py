from PyQt5 import QtWidgets, QtGui
from simulator_control_panel import Ui_MainWindow as Ui_SimulatorControlPanel 

class SimulatorControlPanelLogic(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_SimulatorControlPanel()
        self.ui.setupUi(self)
        self.connect_signals()

    def connect_signals(self):
        self.ui.UploadButton.clicked.connect(self.upload_image)
        self.ui.UploadIcon.clicked.connect(self.upload_image)
        self.ui.ConstraintsText.clicked.connect(self.upload_image)

    def upload_image(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select an Image", "", "Images (*.png *.jpg *.jpeg *.svg)", options=options)
        if file_name:
            print(f"Selected file: {file_name}")
            pixmap = QtGui.QPixmap(file_name)
            self.ui.OriginalDefault.setPixmap(pixmap)
            self.ui.SimulatedDefault.setPixmap(pixmap)
            self.ui.OriginalDefault.setScaledContents(True)
        else:
            print("No file selected.")