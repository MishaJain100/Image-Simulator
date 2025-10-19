# backend/calibration.py
import numpy as np
from scipy.optimize import minimize
from PyQt5.QtCore import pyqtSignal, QThread
from .simulator_engine import SimulatorEngine
import cv2
from typing import Optional, List

class TuningThread(QThread):
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal(dict)

    def __init__(self, engine: SimulatorEngine, input_img: np.ndarray, ref_img: np.ndarray, locks: dict, batch_imgs: Optional[List[np.ndarray]] = None):
        super().__init__()
        self.engine = engine
        self.input_img = input_img
        self.ref_img = ref_img
        self.locks = locks
        self.batch_imgs = batch_imgs or []
        
        self.param_keys = ['distortion_intensity', 'noise_level', 'zoom', 'fov']
        self.iteration = 0
        self.max_iterations = 20

    def run(self):
        def objective(x):
            params = {key: val for key, val in zip(self.param_keys, x)}
            
            full_params = self.engine.get_current_params()
            full_params.update(params)

            for k, is_locked in self.locks.items():
                if is_locked and k in full_params:
                    full_params[k] = self.engine.current_params.get(k)

            if self.batch_imgs:
                loss = 0
                for b_img in self.batch_imgs:
                    sim = self.engine.run_pipeline(self.input_img.copy(), full_params)
                    sim_resized = cv2.resize(sim, (b_img.shape[1], b_img.shape[0]))
                    loss += np.mean((sim_resized.astype(np.float32) - b_img.astype(np.float32)) ** 2)
                return loss / len(self.batch_imgs)
            else:
                sim = self.engine.run_pipeline(self.input_img.copy(), full_params)
                sim_resized = cv2.resize(sim, (self.ref_img.shape[1], self.ref_img.shape[0]))
                loss = np.mean((sim_resized.astype(np.float32) - self.ref_img.astype(np.float32)) ** 2)
                return loss

        initial_guess = [
            self.engine.current_params.get('distortion_intensity', 0.0),
            self.engine.current_params.get('noise_level', 0.0),
            self.engine.current_params.get('zoom', 1.0),
            self.engine.current_params.get('fov', 60.0)
        ]
        
        bounds = [
            (-0.5, 0.5), # distortion_intensity
            (0, 1.0),    # noise_level
            (0.5, 2.0),  # zoom
            (30, 90)     # fov
        ]
        
        def callback(xk):
            self.iteration += 1
            progress = int((self.iteration / self.max_iterations) * 100)
            self.progress_updated.emit(progress)
            print(f"Iteration {self.iteration}, Loss: {objective(xk)}")

        res = minimize(objective, initial_guess, method='L-BFGS-B', 
                       bounds=bounds, callback=callback, 
                       options={'maxiter': self.max_iterations, 'disp': True})
        
        estimated = {k: res.x[i] for i, k in enumerate(self.param_keys)}
        
        self.progress_updated.emit(100)
        self.finished.emit(estimated)