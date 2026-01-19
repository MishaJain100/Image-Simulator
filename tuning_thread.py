import numpy as np
from PyQt5.QtCore import pyqtSignal, QThread
import cv2
from scipy.optimize import minimize
from base_image_generator import CameraSimulator 

class TuningThread(QThread):
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal(dict)

    def __init__(self, target_img_path, locks, defaults):
        super().__init__()
        self.target_img_path = target_img_path
        self.locks = locks
        self.defaults = defaults
        self.iteration = 0
        self.max_iterations = 100
        self.simulator = None 

    def run(self):
        try:
            self.target_img = cv2.imread(self.target_img_path)

            self.optim_h, self.optim_w = 64, 85
            self.target_small = cv2.resize(self.target_img, (self.optim_w, self.optim_h))
            
            if len(self.target_small.shape) == 3:
                self.target_gray = cv2.cvtColor(self.target_small, cv2.COLOR_BGR2GRAY).astype(np.float32)
            else:
                self.target_gray = self.target_small.astype(np.float32)

            self.target_blurred = cv2.GaussianBlur(self.target_gray, (21, 21), 0)
            self.target_std = np.std(self.target_gray)

            h_orig, w_orig = self.target_img.shape[:2]
            self.simulator = CameraSimulator(width=w_orig, height=h_orig)
            
            self.sensor_width = self.defaults.get('sensor_width', 36.0)
            self.sensor_height = self.defaults.get('sensor_height', 24.0)

            test_focals = [16.0, 24.0, 35.0, 50.0, 85.0, 105.0]
            best_loss = float('inf')
            best_start_focal = 50.0
            
            for f in test_focals:
                loss = self.objective([f, 0.0, 10.0])
                if loss < best_loss:
                    best_loss = loss
                    best_start_focal = f
            
            print(f"Best Start Focal: {best_start_focal}mm")

            initial_guess = np.array([best_start_focal, 0.0, 10.0])
            
            bounds = [(10.0, 150.0), (-0.5, 0.5), (0.0, 50.0)]

            res = minimize(self.objective, initial_guess, method='Nelder-Mead', bounds=bounds, callback=self.callback, options={'maxiter': self.max_iterations, 'xatol': 0.1, 'fatol': 0.1})

            final_focal = float(res.x[0])
            final_k1 = float(res.x[1])
            final_noise = float(res.x[2])

            full_dist = np.zeros(5)
            full_dist[0] = final_k1

            result = {
                'focal_length': abs(final_focal),
                'sensor_width': self.sensor_width,
                'sensor_height': self.sensor_height,
                'distortion': full_dist,
                'noise': abs(final_noise),
                'final_loss': res.fun
            }
            
            self.finished.emit(result)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.finished.emit({'error': str(e)})

    def objective(self, x):
        focal_val = abs(x[0])
        k1_val = x[1]
        noise_val = abs(x[2])

        dist_array = np.zeros(5)
        dist_array[0] = k1_val
        
        sim_frame = self.simulator.generate_simulated_image(focal_val, self.sensor_width, self.sensor_height, dist_array, noise_val)
        
        sim_small = cv2.resize(sim_frame, (self.optim_w, self.optim_h))
        
        if len(sim_small.shape) == 2 or sim_small.shape[2] == 1:
            sim_gray = sim_small.astype(np.float32)
        else:
            sim_gray = cv2.cvtColor(sim_small, cv2.COLOR_BGR2GRAY).astype(np.float32)

        sim_blurred = cv2.GaussianBlur(sim_gray, (21, 21), 0)
        structure_loss = np.mean(np.abs(self.target_blurred - sim_blurred))
        
        sim_std = np.std(sim_gray)
        noise_loss = abs(self.target_std - sim_std) * 2.0 
        
        return structure_loss + noise_loss

    def callback(self, xk):
        self.iteration += 1
        progress = int((self.iteration / self.max_iterations) * 100)
        self.progress_updated.emit(min(progress, 100))
        print(f"Iter {self.iteration}: F={xk[0]:.2f}, Noise={xk[2]:.2f}")