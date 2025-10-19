# backend/sensor.py
import cv2
import numpy as np

def apply_sensor_effects(img: np.ndarray, params: dict) -> np.ndarray:
    if img is None: return img
    # Image is converted to float and normalized to the [0.0, 1.0] range
    img = img.copy().astype(np.float32) / 255.0

    noise_level = params.get('noise_level', 0.0)
    if noise_level > 0:
        std = noise_level
        if params.get('sensor_type') == 'CCD':
            std *= 0.8
            # Poisson noise is correctly scaled here
            img += np.random.poisson(img * 50.0, img.shape) / 50.0 - img
        elif params.get('sensor_type') == 'sCMOS':
            std *= 1.2
        
        # --- START FIX ---
        # The image is in the [0, 1] range, so the noise standard deviation (std)
        # should also be in that range. The division by 255 was incorrect.
        # OLD LINE: img += np.random.normal(0, std / 255.0, img.shape)
        img += np.random.normal(0, std, img.shape)
        # --- END FIX ---

    exposure = params.get('exposure', 50) / 50.0
    img *= exposure

    lower, upper = params.get('dynamic_range', (0, 255))
    img = np.clip(img, lower/255.0, upper/255.0)
    range_val = (upper - lower) / 255.0
    if range_val > 1e-6:
        img = (img - lower/255.0) / range_val

    res_str = params.get('resolution', 'Unchanged')
    if res_str != 'Unchanged':
        target_w, target_h = map(int, res_str.split(' x '))
        h, w = img.shape[:2]
        if h == 0 or w == 0: return np.zeros((target_h, target_w, 3), dtype=np.uint8)
        
        img = cv2.resize(img, (target_w, target_h), interpolation=cv2.INTER_AREA)

    if params.get('cfa', False):
        cfa_img = img.copy()
        h, w, _ = cfa_img.shape
        bayer_gray = np.zeros((h, w), dtype=np.float32)
        
        bayer_gray[::2, ::2] = cfa_img[::2, ::2, 2]     # R
        bayer_gray[::2, 1::2] = cfa_img[::2, 1::2, 1]   # G
        bayer_gray[1::2, ::2] = cfa_img[1::2, ::2, 1]   # G
        bayer_gray[1::2, 1::2] = cfa_img[1::2, 1::2, 0] # B

        bayer_uint8 = (bayer_gray * 255.0).clip(0, 255).astype('uint8')
        demosaiced = cv2.cvtColor(bayer_uint8, cv2.COLOR_BayerRG2BGR)
        img = demosaiced.astype(np.float32) / 255.0

    return np.clip(img * 255.0, 0, 255).astype(np.uint8)