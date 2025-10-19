# backend/lighting.py
import cv2
import numpy as np

def apply_lighting(img: np.ndarray, params: dict) -> np.ndarray:
    if img is None: return img
    img = img.astype(np.float32) / 255.0
    h, w, _ = img.shape
    if h == 0 or w == 0: return np.clip(img * 255, 0, 255).astype(np.uint8)

    brightness = (params.get('brightness', 50) - 50) / 50.0
    img *= (1 + brightness)

    direction = np.radians(params.get('light_direction', 0))
    light_vec = np.array([np.cos(direction), np.sin(direction)])
    
    x, y = np.meshgrid(np.arange(w), np.arange(h))
    dx = (x - w/2) / w
    dy = (y - h/2) / h
    
    normals = np.dstack([dx, dy])
    dot_nl = np.sum(normals * light_vec, axis=2)
    illum = np.clip(dot_nl + 0.7, 0, 1) # Ambient 0.7
    img *= illum[:,:,np.newaxis]

    shadows = params.get('shadows', 0.0)
    if shadows > 0:
        shadow_mask = np.clip(1 - (1 - illum) * (1.0 + shadows), 0.1, 1)
        img *= shadow_mask[:,:,np.newaxis]

    specular = params.get('specular', 0.0)
    if specular > 0:
        view_dir = np.array([0, -1.0])
        reflect_dir = 2 * dot_nl[:, :, np.newaxis] * normals - light_vec
        dot_rv = np.sum(reflect_dir * view_dir, axis=2)
        spec = np.clip(np.power(dot_rv, 32), 0, 1) * specular
        img += spec[:,:,np.newaxis]

    return np.clip(img * 255, 0, 255).astype(np.uint8)