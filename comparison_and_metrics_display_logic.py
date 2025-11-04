from PyQt5 import QtWidgets, QtGui, QtCore
from comparison_and_metrics_display import Ui_MainWindow as Ui_ComparisonAndMetricsDisplay
import cv2
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr

class ComparisonAndMetricsDisplayLogic(QtWidgets.QMainWindow):
    def __init__(self, parent=None, sim=None, img_size=None):
        super().__init__(parent)
        self.ui = Ui_ComparisonAndMetricsDisplay()
        self.ui.setupUi(self)
        self.connect_signals()

        self.set_img(sim, img_size)

    def set_img(self, sim, img_size):
        self.sim = sim
        self.img_size = img_size
        if self.sim is not None:
            h, w, ch = sim.shape          
            bytes_per_line = ch * w
            qt_image = QtGui.QImage(sim.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qt_image)
            if self.img_size:
                label_size = self.img_size
            else:
                label_size = self.ui.SimulatedImageImage.size() 
            
            pixmap = pixmap.scaled(label_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.ui.SimulatedImageImage.setScaledContents(False)
            self.ui.SimulatedImageImage.setPixmap(pixmap)

    def connect_signals(self):
        self.ui.UploadButton.clicked.connect(self.upload_image)
        self.ui.UploadIcon.clicked.connect(self.upload_image)
        self.ui.BrowseFiles.clicked.connect(self.upload_image)
        self.ui.ConstraintsText.clicked.connect(self.upload_image)

    def upload_image(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select an Image", "", "Images (*.png *.jpg *.jpeg *.svg)", options=options)
        if file_name:
            print(f"Selected file: {file_name}")
            self.real_img_cv = cv2.imread(file_name)
            self.ui.UploadButton.setText(file_name.split('/')[-1])
            self.ui.ConstraintsText.setText('File Uploaded')
            self.run_comparison()
        else:
            print("No file selected.")

    def run_comparison(self):
        if self.real_img_cv is None or self.sim is None:
            return
        h, w = self.sim.shape[:2]
        real_resized_bgr = cv2.resize(self.real_img_cv, (w, h), interpolation=cv2.INTER_AREA)
        real_gray = cv2.cvtColor(real_resized_bgr, cv2.COLOR_BGR2GRAY)
        sim_gray = cv2.cvtColor(self.sim, cv2.COLOR_RGB2GRAY)
        try:
            data_range = sim_gray.max() - sim_gray.min()
            ssim_score = ssim(real_gray, sim_gray, data_range=data_range)
            self.ui.SSIMValue.setText(f"{ssim_score:.4f}")
        except Exception as e:
            print(f"Error calculating SSIM: {e}")
            self.ui.SSIMValue.setText("Error")
        try:
            psnr_score = psnr(real_gray, sim_gray, data_range=data_range)
            if psnr_score == float('inf'):
                self.ui.PSNRValue.setText("Perfect")
            else:
                self.ui.PSNRValue.setText(f"{psnr_score:.2f} dB")
        except Exception as e:
            print(f"Error calculating PSNR: {e}")
            self.ui.PSNRValue.setText("Error")
        try:
            diff_img = cv2.absdiff(real_gray, sim_gray)
            diff_colormap = cv2.applyColorMap(diff_img, cv2.COLORMAP_HOT)
            self.display_image(diff_colormap, self.ui.MapImage, self.ui.MapImage.size())
        except Exception as e:
            print(f"Error creating difference map: {e}")
        try:
            real_hist = cv2.calcHist([real_gray], [0], None, [256], [0, 256])
            self.ui.RealHistogram.setData(real_hist.flatten().astype(float))
            sim_hist = cv2.calcHist([sim_gray], [0], None, [256], [0, 256])
            self.ui.SimulatedHistogram.setData(sim_hist.flatten().astype(float))
        except Exception as e:
            print(f"Error generating histograms: {e}")

    def display_image(self, img_cv, label_widget, target_size=None):
        if img_cv is None:
            return
        if len(img_cv.shape) == 3:
            if img_cv.shape[2] == 3:
                if label_widget is self.ui.SimulatedImageImage:
                    img_rgb = img_cv
                    qt_image_format = QtGui.QImage.Format_RGB888
                else:
                    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
                    qt_image_format = QtGui.QImage.Format_RGB888
                
                h, w, ch = img_rgb.shape
                bytes_per_line = ch * w
            else:
                print("Error: Unsupported image format.")
                return
        else:
            img_rgb = img_cv
            h, w = img_rgb.shape
            bytes_per_line = w
            qt_image_format = QtGui.QImage.Format_Grayscale8
        
        qt_image = QtGui.QImage(img_rgb.data, w, h, bytes_per_line, qt_image_format)
        pixmap = QtGui.QPixmap.fromImage(qt_image)
        
        if target_size:
            label_size = target_size
        else:
            label_size = label_widget.size()
            if label_size.width() == 0 or label_size.height() == 0:
                print("Warning: Label size is zero, cannot scale image.")
                return

        pixmap = pixmap.scaled(label_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        
        label_widget.setScaledContents(False)
        label_widget.setPixmap(pixmap)