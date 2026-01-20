from PyQt5 import QtWidgets, QtGui, QtCore
from simulator_control_panel import Ui_MainWindow as Ui_SimulatorControlPanel
import cv2
import numpy as np

class SimulatorControlPanelLogic(QtWidgets.QMainWindow):
    def __init__(self, parent=None, img=None, img_size=None):
        super().__init__(parent)
        self.ui = Ui_SimulatorControlPanel()
        self.ui.setupUi(self)
        
        self.img_path = None
        self.img_size = None
        self.map_cache = None
        self.last_geo_params = None
        self.thread = None

        self.current_sim = None

        self.connect_signals()

        self.set_current_params()

        if img:
            self.img_path = img
            self.img_size = img_size
            self.start_processing_thread(img)

    def connect_signals(self):
        self.ui.UploadButton.clicked.connect(self.upload_image)
        self.ui.UploadIcon.clicked.connect(self.upload_image)
        self.ui.ConstraintsText.clicked.connect(self.upload_image)
        self.ui.Reset.clicked.connect(self.reset)

        self.ui.ZoomSlider.valueChanged.connect(lambda v: self.ui.ZoomNumber.setText(f'{v}%'))
        self.ui.FOVSlider.valueChanged.connect(lambda v: self.ui.FOVNumber.setText(f'{v}°'))
        self.ui.DistortionSlider.valueChanged.connect(lambda v: self.ui.DistortionNumber.setText(f'{v/1000.0}'))
        self.ui.BrightnessSlider.valueChanged.connect(lambda v: self.ui.BrightnessNumber.setText(f'{v}'))
        self.ui.LDSlider.valueChanged.connect(lambda v: self.ui.LDNumber.setText(f'{v}°'))
        self.ui.ShadowsSlider.valueChanged.connect(lambda v: self.ui.ShadowsNumber.setText(f'{v}'))
        self.ui.NoiseSlider.valueChanged.connect(lambda v: self.ui.NoiseNumber.setText(f'{v}'))
        self.ui.ExposureSlider.valueChanged.connect(lambda v: self.ui.ExposureNumber.setText(f'{v}'))
        self.ui.ResolutionDropDown.currentIndexChanged.connect(self.on_resolution_changed) 

        self.ui.SimulatedDefault.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.SimulatedDefault.customContextMenuRequested.connect(self.show_context_menu)

    def on_resolution_changed(self):
        if self.img_path:
            self.start_processing_thread(self.img_path)

    def set_current_params(self):
        parent_params = None
        if self.parent() and hasattr(self.parent(), 'current_params'):
            parent_params = self.parent().current_params

        if not parent_params:
            return

        self.ui.ZoomSlider.setValue(parent_params.get('zoom', 0))
        self.ui.FOVSlider.setValue(parent_params.get('fov', 60))
        self.ui.DistortionSlider.setValue(parent_params.get('distortion', 0))
        self.ui.BrightnessSlider.setValue(parent_params.get('brightness', 0))
        self.ui.LDSlider.setValue(parent_params.get('ld', 45))
        self.ui.ShadowsSlider.setValue(parent_params.get('shadows', 0))
        self.ui.NoiseSlider.setValue(parent_params.get('noise', 0))
        self.ui.ExposureSlider.setValue(parent_params.get('exposure', 50))

    def upload_image(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Source", "", "Media (*.png *.jpg *.jpeg *.mp4 *.avi)", options=options)
        if file_name:
            self.img_path = file_name
            
            if self.parent():
                self.parent().img = file_name

            if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                pixmap = QtGui.QPixmap(file_name)
                label_size = self.ui.OriginalDefault.size()
                pixmap = pixmap.scaled(label_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                self.ui.OriginalDefault.setPixmap(pixmap)
                
                if self.parent():
                    self.parent().img_display_size = pixmap.size()

            self.start_processing_thread(file_name)

    def start_processing_thread(self, source):
        if self.thread is not None:
            self.thread.stop()
        
        self.thread = ProcessingThread(source, self)
        self.thread.frame_ready.connect(self.update_display_slot)
        self.thread.start()

    def update_display_slot(self, original_frame, simulated_frame):
        self.current_sim = simulated_frame
        h, w, ch = simulated_frame.shape
        bytes_per_line = ch * w
        q_sim = QtGui.QImage(simulated_frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap_sim = QtGui.QPixmap.fromImage(q_sim)
        
        label_size = self.ui.SimulatedDefault.size()
        pixmap_sim = pixmap_sim.scaled(label_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        self.ui.SimulatedDefault.setPixmap(pixmap_sim)
        
        if self.parent() and not self.parent().img_display_size:
            self.parent().img_display_size = self.ui.SimulatedDefault.size()

        h_o, w_o, ch_o = original_frame.shape
        bytes_per_line_o = ch_o * w_o
        q_orig = QtGui.QImage(original_frame.data, w_o, h_o, bytes_per_line_o, QtGui.QImage.Format_RGB888)
        pixmap_orig = QtGui.QPixmap.fromImage(q_orig)
        
        label_size = self.ui.OriginalDefault.size()
        pixmap_orig = pixmap_orig.scaled(label_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.FastTransformation)
        self.ui.OriginalDefault.setPixmap(pixmap_orig)

    def get_current_params_dict(self):
        try:
            if not self.ui.ZoomSlider: 
                return None
            
            return {
                'zoom': self.ui.ZoomSlider.value(),
                'fov': self.ui.FOVSlider.value(),
                'distortion': self.ui.DistortionSlider.value(),
                'brightness': self.ui.BrightnessSlider.value(),
                'ld': self.ui.LDSlider.value(),
                'shadows': self.ui.ShadowsSlider.value(),
                'noise': self.ui.NoiseSlider.value(),
                'exposure': self.ui.ExposureSlider.value(),
                'res_text': self.ui.ResolutionDropDown.currentText()
            }
        except (RuntimeError, AttributeError):
            return None

    def process_pipeline(self, frame, params):
        h, w = frame.shape[:2]
        
        target_w = 1280 
        
        if w > target_w:
            display_w = target_w
            display_h = int(h * (display_w / w))
            frame = cv2.resize(frame, (display_w, display_h), interpolation=cv2.INTER_AREA)
        
        original_preview = frame.copy()

        frame = self.apply_zoom(frame, params['zoom'])
        
        current_geo_key = (params['fov'], params['distortion'], frame.shape[:2])
        if self.map_cache is None or self.last_geo_params != current_geo_key:
            self.map_cache = self.compute_geometry_maps(frame, params)
            self.last_geo_params = current_geo_key

        frame = cv2.remap(frame, self.map_cache[0], self.map_cache[1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

        frame = self.apply_brightness(frame, params['brightness'])
        frame = self.apply_ld(frame, params['ld'])
        frame = self.apply_shadows(frame, params['shadows'])
        frame = self.apply_exposure(frame, params['exposure'])
        frame = self.apply_noise(frame, params['noise'])
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        original_rgb = cv2.cvtColor(original_preview, cv2.COLOR_BGR2RGB)
        
        return original_rgb, frame_rgb

    def compute_geometry_maps(self, img, params):
        h, w = img.shape[:2]
        
        fov_degrees = params['fov']
        default_fov = 60
        default_focal = (w / 2.0) / np.tan(np.radians(default_fov / 2.0))
        
        if fov_degrees == 60:
            new_focal = default_focal
        else:
            new_focal = (w / 2.0) / np.tan(np.radians(fov_degrees / 2.0))

        K_default = np.array([[default_focal, 0, w/2], [0, default_focal, h/2], [0, 0, 1]])
        K_new = np.array([[new_focal, 0, w/2], [0, new_focal, h/2], [0, 0, 1]])

        k1 = params['distortion'] / 1000.0
        
        map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))

        pts = np.stack([map_x.ravel(), map_y.ravel(), np.ones(w*h)], axis=0)
        pts_normalized = np.linalg.inv(K_new) @ pts
        
        if k1 != 0:
            x_norm = pts_normalized[0, :]
            y_norm = pts_normalized[1, :]
            r_sq = x_norm**2 + y_norm**2
            radial = 1 + k1 * r_sq
            pts_normalized[0, :] = x_norm * radial
            pts_normalized[1, :] = y_norm * radial
            
        pts_transformed = K_default @ pts_normalized
        
        map_x_final = pts_transformed[0, :].reshape(h, w).astype(np.float32)
        map_y_final = pts_transformed[1, :].reshape(h, w).astype(np.float32)
        
        return map_x_final, map_y_final

    def apply_zoom(self, img, zoom_percent):
        if zoom_percent == 0: return img
        h, w = img.shape[:2]
        scale = 1.0 + (zoom_percent / 100.0) if zoom_percent > 0 else 1.0 + (zoom_percent / 200.0)
        
        cx, cy = w/2, h/2
        M = cv2.getRotationMatrix2D((cx, cy), 0, scale)
        return cv2.warpAffine(img, M, (w, h))

    def apply_brightness(self, img, val):
        if val == 0: return img
        return cv2.convertScaleAbs(img, alpha=1, beta=val*2.55)

    def apply_ld(self, img, azimuth):
        if azimuth == 45: return img
        h, w = img.shape[:2]
        azimuth_rad = np.radians(azimuth)
        Y, X = np.ogrid[:h, :w]
        X = (X - w/2) / (w/2)
        Y = (Y - h/2) / (h/2)
        
        light_mask = X * np.cos(azimuth_rad) + Y * np.sin(azimuth_rad)
        light_mask = (light_mask + 1) / 2 # 0 to 1
        light_mask = 0.7 + (0.3 * light_mask) # Intensity range
        
        img = img.astype(np.float32) * light_mask[:, :, np.newaxis]
        return np.clip(img, 0, 255).astype(np.uint8)

    def apply_shadows(self, img, intensity):
        if intensity == 0: return img
        h, w = img.shape[:2]
        Y, X = np.ogrid[:h, :w]
        center_x, center_y = w/2, h/2
        dist_sq = (X - center_x)**2 + (Y - center_y)**2
        max_dist_sq = (w/2)**2 + (h/2)**2
        
        mask = 1 - (dist_sq / max_dist_sq) * (intensity/100.0)
        mask = np.clip(mask, 0, 1)
        
        img = img.astype(np.float32) * mask[:, :, np.newaxis]
        return np.clip(img, 0, 255).astype(np.uint8)

    def apply_exposure(self, img, val):
        if val == 50: return img
        factor = 2 ** ((val - 50) / 25.0)
        return cv2.convertScaleAbs(img, alpha=factor, beta=0)

    def apply_noise(self, img, level):
        if level == 0: return img
        row, col, ch = img.shape
        gauss = np.random.normal(0, level, (row, col, ch))
        noisy = img.astype(np.float32) + gauss
        return np.clip(noisy, 0, 255).astype(np.uint8)
    
    def reset(self):
        self.ui.ZoomSlider.setValue(0)
        self.ui.FOVSlider.setValue(60)
        self.ui.DistortionSlider.setValue(0)
        self.ui.BrightnessSlider.setValue(0)
        self.ui.LDSlider.setValue(45)
        self.ui.ShadowsSlider.setValue(0)
        self.ui.NoiseSlider.setValue(0)
        self.ui.ExposureSlider.setValue(50)

    def show_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        
        save_action = QtWidgets.QAction("Download", self)
        save_action.triggered.connect(self.save_simulated_image)
        menu.addAction(save_action)
        
        menu.exec_(self.ui.SimulatedDefault.mapToGlobal(pos))

    def save_simulated_image(self):
        if not self.img_path:
            QtWidgets.QMessageBox.warning(self, "Error", "No source media loaded!")
            return

        is_video = self.img_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))

        if is_video:
            self.render_video_output()
        else:
            if self.current_sim is None: 
                return
            
            options = QtWidgets.QFileDialog.Options()
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Save Image", "simulated_output.jpg", "Images (*.jpg *.png);;All Files (*)", options=options
            )
            
            if file_path:
                save_img = cv2.cvtColor(self.current_sim, cv2.COLOR_RGB2BGR)
                cv2.imwrite(file_path, save_img)
                QtWidgets.QMessageBox.information(self, "Success", "Image saved successfully!")

    def render_video_output(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Video", "simulated_video.mp4", "Video (*.mp4);;All Files (*)", options=options)

        if not file_path:
            return

        if self.thread:
            self.thread.stop()

        progress = QtWidgets.QProgressDialog("Rendering video", "Cancel", 0, 100, self)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        progress.show()

        try:
            cap = cv2.VideoCapture(self.img_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            if fps <= 0: fps = 30
            
            ret, sample_frame = cap.read()
            if not ret: raise Exception("Could not read source video")
            
            params = self.get_current_params_dict()
            
            _, sample_processed = self.process_pipeline(sample_frame, params)
            h, w = sample_processed.shape[:2]
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

            fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
            writer = cv2.VideoWriter(file_path, fourcc, fps, (w, h))

            frame_idx = 0
            while True:
                if progress.wasCanceled():
                    break
                    
                ret, frame = cap.read()
                if not ret:
                    break
                
                _, processed_rgb = self.process_pipeline(frame, params)
                
                processed_bgr = cv2.cvtColor(processed_rgb, cv2.COLOR_RGB2BGR)
                
                writer.write(processed_bgr)

                frame_idx += 1
                progress.setValue(int((frame_idx / total_frames) * 100))
                QtWidgets.QApplication.processEvents()

            cap.release()
            writer.release()
            QtWidgets.QMessageBox.information(self, "Success", "Video rendering complete!")

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to render video: {str(e)}")
        
        finally:
            self.start_processing_thread(self.img_path)

    def closeEvent(self, event):
        if self.thread:
            self.thread.stop()
        event.accept()

class ProcessingThread(QtCore.QThread):
    frame_ready = QtCore.pyqtSignal(np.ndarray, np.ndarray)

    def __init__(self, source, logic_ref):
        super().__init__()
        self.source = source
        self.logic = logic_ref
        self._run_flag = True
        self.is_video = source.lower().endswith(('.mp4', '.avi', '.mov', '.mkv'))

    def run(self):
        if self.is_video:
            cap = cv2.VideoCapture(self.source)
            while self._run_flag:
                ret, frame = cap.read()
                if not ret:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                params = self.logic.get_current_params_dict()
                if params is None: 
                    break
                
                original, processed = self.logic.process_pipeline(frame, params)
                self.frame_ready.emit(original, processed)
                
                self.msleep(30) 
            cap.release()
        else:
            frame = cv2.imread(self.source)
            if frame is not None:
                while self._run_flag:
                    params = self.logic.get_current_params_dict()
                    if params is None: 
                        break

                    original, processed = self.logic.process_pipeline(frame, params)
                    self.frame_ready.emit(original, processed)
                    self.msleep(30)

    def stop(self):
        self._run_flag = False
        self.wait()