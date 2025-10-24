import numpy as np
from PyQt5.QtCore import pyqtSignal, QThread
import cv2
from scipy.optimize import minimize
from base_image_generator import CameraSimulator 

class TuningThread(QThread):
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal(dict)

    def __init__(self, imgs, locks):
        super().__init__()
        self.imgs = imgs
        self.locks = locks
        print (self.locks)
        self.iteration = 0
        self.max_iterations = 20
        
        self.defaults = {
            'focal_length': 35.0,
            'sensor_width': 36.0,
            'sensor_height': 24.0,
            'distortion': np.zeros(5, dtype=np.float32),
            'noise': 0.0
        }

    def _unflatten_params(self, x_flat):
        return {
            'focal_length': x_flat[0],
            'sensor_width': x_flat[1],
            'sensor_height': x_flat[2],
            'distortion': x_flat[3:8],
            'noise': x_flat[8]
        }

    def run(self):
        try:
            initial_guess_flat = np.concatenate([
                np.array([
                    self.defaults['focal_length'],
                    self.defaults['sensor_width'],
                    self.defaults['sensor_height']
                ]),
                self.defaults['distortion'],
                np.array([self.defaults['noise']])
            ])

            bounds = [
                (self.defaults['focal_length'], self.defaults['focal_length']) if self.locks.get('focal_length') else (10.0, 200.0),
                (self.defaults['sensor_width'], self.defaults['sensor_width']) if self.locks.get('sensor_width') else (5.0, 50.0),
                (self.defaults['sensor_height'], self.defaults['sensor_height']) if self.locks.get('sensor_height') else (5.0, 50.0),
                *[(val, val) if self.locks.get('distortion') else (-0.5, 0.5) for val in self.defaults['distortion']],
                (self.defaults['noise'], self.defaults['noise']) if self.locks.get('noise') else (0.0, 50.0)
            ]

            res = minimize(
                self.objective, 
                initial_guess_flat, 
                method='L-BFGS-B',
                bounds=bounds,
                callback=self.callback, 
                options={'maxiter': self.max_iterations, 'disp': True}
            )
            
            estimated_params = self._unflatten_params(res.x)
            self.progress_updated.emit(100)
            self.finished.emit(estimated_params)
        except Exception as e:
            print(f"\n!!!!!!!!!! TUNING THREAD CRASHED !!!!!!!!!!")
            print(f"Exception type: {type(e)}")
            print(f"Error message: {e}")
            import traceback
            traceback.print_exc()
            self.finished.emit({})

    def objective(self, x_flat):
        params = self._unflatten_params(x_flat)

        simulator = CameraSimulator(width=800, height=600)
        sim_img = simulator.generate_simulated_image(
            params['focal_length'], 
            params['sensor_width'], 
            params['sensor_height'], 
            params['distortion'], 
            params['noise']
        )

        loss = 0
        for img_path in self.imgs:
            print ('Inside for loop')
            target_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if target_img is None:
                print(f"Warning: Could not read image {img_path}")
                continue
            sim_resized = cv2.resize(sim_img, (target_img.shape[1], target_img.shape[0]))
            loss += np.mean((sim_resized.astype(np.float32) - target_img.astype(np.float32)) ** 2)
            
        return loss / len(self.imgs) if self.imgs else 0
    
    def callback(self, xk):
        print ("Callback")
        self.iteration += 1
        progress = int((self.iteration / self.max_iterations) * 100)
        self.progress_updated.emit(progress)
        print(f"Iteration {self.iteration}, Loss: {self.objective(xk)}")