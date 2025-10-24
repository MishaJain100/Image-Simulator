import numpy as np
from PyQt5.QtCore import pyqtSignal, QThread
import cv2
from scipy.optimize import minimize

class TuningThread(QThread):
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal(dict)

    def __init__(self, ground_truth_points_2d, world_points_3d, locks, defaults):
        super().__init__()
        self.ground_truth_points_2d = ground_truth_points_2d
        self.world_points_3d = world_points_3d
        self.locks = locks
        self.iteration = 0
        self.max_iterations = 100
        self.defaults = {
            'focal_length': 35.0,
            'sensor_width': 36.0,
            'sensor_height': 24.0,
            'distortion': np.zeros(5, dtype=np.float32),
        }

    def _unflatten_params(self, x_flat):
        return {
            'focal_length': x_flat[0],
            'sensor_width': x_flat[1],
            'sensor_height': x_flat[2],
            'distortion': x_flat[3:8],
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
            ])
            bounds = [
                (self.defaults['focal_length'], self.defaults['focal_length']) if self.locks.get('focal_length') else (10.0, 200.0),
                (self.defaults['sensor_width'], self.defaults['sensor_width']) if self.locks.get('sensor_width') else (self.defaults['sensor_width'], self.defaults['sensor_width']),
                (self.defaults['sensor_height'], self.defaults['sensor_height']) if self.locks.get('sensor_height') else (self.defaults['sensor_height'], self.defaults['sensor_height']),
                *[(val, val) if self.locks.get('distortion') else (-0.5, 0.5) for val in self.defaults['distortion']],
            ]
            res = minimize(
                self.objective,
                initial_guess_flat,
                method='L-BFGS-B',
                bounds=bounds,
                callback=self.callback,
                options={'maxiter': self.max_iterations, 'iprint': 99, 'ftol': 1e-9, 'eps': 1e-5}
            )
            estimated_params = self._unflatten_params(res.x)
            estimated_params['noise'] = 3.0
            self.finished.emit(estimated_params)

        except Exception as e:
            print(f"\n!!!!!!!!!! TUNING THREAD CRASHED !!!!!!!!!!")
            import traceback
            traceback.print_exc()
            error_params = self.defaults.copy()
            error_params['noise'] = 3.0
            self.finished.emit(error_params)


    def objective(self, x_flat):
        print(f"Objective called with: {x_flat}")
        params = self._unflatten_params(x_flat)

        width, height = 800, 600
        fx = params['focal_length'] * (width / params['sensor_width'])
        fy = params['focal_length'] * (height / params['sensor_height'])
        cx = width / 2
        cy = height / 2
        K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float32)

        rvec = np.zeros(3, dtype=np.float32)
        tvec = np.zeros(3, dtype=np.float32)
        
        simulated_points_2d, _ = cv2.projectPoints(
            self.world_points_3d, rvec, tvec, K, params['distortion']
        )
        
        if np.isnan(simulated_points_2d).any():
            print(f"    Focal: {params['focal_length']:.2f}, SensorW: {params['sensor_width']:.2f}, SensorH: {params['sensor_height']:.2f}")
            print(f"    Dist: {params['distortion']}")
            print(f"    Camera Matrix K: \n{K}")
            return 1e99 

        loss = np.mean((self.ground_truth_points_2d - simulated_points_2d)**2)
        
        print(f"    -> Loss: {loss:.6f}")
        
        return loss
    
    def callback(self, xk):
        self.iteration += 1
        loss = self.objective(xk)
        progress = int((self.iteration / self.max_iterations) * 100)
        self.progress_updated.emit(min(progress, 100))
        print(f"Iteration {self.iteration}, Loss: {loss:.6f}")