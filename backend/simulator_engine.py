# backend/simulator_engine.py
import numpy as np
from .optics import apply_optics
from .lighting import apply_lighting
from .sensor import apply_sensor_effects

class SimulatorEngine:
    def __init__(self):
        self.current_params = {}

    def run_pipeline(self, input_img: np.ndarray, params: dict) -> np.ndarray:
        """Full pipeline: optics -> lighting -> sensor."""
        if input_img is None:
            return None
        self.current_params = params
        img = input_img.copy()
        img = apply_optics(img, params)
        img = apply_lighting(img, params)
        img = apply_sensor_effects(img, params)
        return img

    def get_current_params(self) -> dict:
        return self.current_params.copy()