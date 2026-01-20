import numpy as np
from PyQt5.QtCore import pyqtSignal, QThread
import cv2
from scipy.optimize import minimize

class TuningThread(QThread):
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal(dict)

    def __init__(self, source_path, target_path, locks, defaults):
        super().__init__()
        self.source_path = source_path
        self.target_path = target_path
        self.locks = locks
        self.defaults = defaults
        self.iteration = 0
        self.max_iterations = 100

    def run(self):
        try:
            self.source_img = self._load_frame(self.source_path)
            self.target_img = self._load_frame(self.target_path)

            if self.source_img is None or self.target_img is None:
                raise ValueError("Could not load Source or Target media.")

            h_t, w_t = self.target_img.shape[:2]
            self.source_img = cv2.resize(self.source_img, (w_t, h_t))

            self.target_gray = self._to_normalized_gray(self.target_img)
            self.source_gray_base = self._to_normalized_gray(self.source_img)

            self.target_std = np.std(self.target_gray)

            self.optim_w, self.optim_h = 160, 120
            self.target_small = cv2.resize(self.target_gray, (self.optim_w, self.optim_h))

            initial_guess = np.array([24.0, 0.0, 0.0]) 
            
            bounds = [(10.0, 150.0), (-0.5, 0.5), (0.0, 50.0)]

            print("Starting Distortion Matching...")
            
            res = minimize(
                self.objective,
                initial_guess,
                method='Nelder-Mead', 
                bounds=bounds,
                callback=self.callback,
                options={'maxiter': self.max_iterations, 'xatol': 0.1, 'fatol': 0.001}
            )

            final_focal = float(res.x[0])
            final_k1 = float(res.x[1])
            final_noise = float(res.x[2])

            full_dist = np.zeros(5)
            full_dist[0] = final_k1

            result = {
                'focal_length': abs(final_focal),
                'sensor_width': 36.0,
                'sensor_height': 24.0,
                'distortion': full_dist,
                'noise': abs(final_noise),
                'final_loss': res.fun
            }
            
            self.finished.emit(result)

        except Exception as e:
            print(f"Tuning Thread Crash: {e}")
            import traceback
            traceback.print_exc()
            self.finished.emit({'error': str(e)})

    def objective(self, x):
        focal_val = abs(x[0])
        k1_val = x[1]
        noise_val = abs(x[2])

        h, w = self.source_img.shape[:2]
        
        map_x, map_y = self.compute_geometry_maps(w, h, focal_val, k1_val)
        
        sim_img = cv2.remap(self.source_img, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
        
        if noise_val > 0.5:
            noise_layer = np.random.normal(0, noise_val, sim_img.shape).astype(np.float32)
            sim_img = np.clip(sim_img.astype(np.float32) + noise_layer, 0, 255).astype(np.uint8)

        sim_small_gray = cv2.resize(self._to_normalized_gray(sim_img), (self.optim_w, self.optim_h))
        
        diff = np.mean(np.abs(self.target_small - sim_small_gray))
        
        sim_std = np.std(sim_small_gray)
        noise_loss = abs(self.target_std - sim_std)
        
        return diff + (noise_loss * 0.5)

    def compute_geometry_maps(self, w, h, focal_length_mm, k1):
        sensor_w = 36.0
        sensor_h = 24.0

        fx = focal_length_mm * (w / sensor_w)
        fy = focal_length_mm * (h / sensor_h)

        K = np.array([
            [fx, 0, w/2], 
            [0, fy, h/2], 
            [0, 0, 1]
        ])

        map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))

        pts = np.stack([map_x.ravel(), map_y.ravel(), np.ones(w*h)], axis=0)

        pts_norm = np.linalg.inv(K) @ pts
        x_n = pts_norm[0, :]
        y_n = pts_norm[1, :]

        r2 = x_n**2 + y_n**2

        radial = 1 + k1 * r2 
        
        x_dist = x_n * radial
        y_dist = y_n * radial

        pts_dist = K @ np.stack([x_dist, y_dist, np.ones_like(x_dist)], axis=0)
        
        map_x = pts_dist[0, :].reshape(h, w).astype(np.float32)
        map_y = pts_dist[1, :].reshape(h, w).astype(np.float32)
        
        return map_x, map_y

    def _load_frame(self, path):
        if path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            cap = cv2.VideoCapture(path)
            if not cap.isOpened(): return None
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.set(cv2.CAP_PROP_POS_FRAMES, total // 2)
            ret, frame = cap.read()
            cap.release()
            return frame
        else:
            return cv2.imread(path)

    def _to_normalized_gray(self, img):
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32)
        else:
            gray = img.astype(np.float32)
        return cv2.normalize(gray, None, 0, 1, cv2.NORM_MINMAX)

    def callback(self, xk):
        self.iteration += 1
        progress = int((self.iteration / self.max_iterations) * 100)
        self.progress_updated.emit(min(progress, 100))
        print(f"Iter {self.iteration}: F={xk[0]:.2f}mm, Noise={xk[2]:.2f}")