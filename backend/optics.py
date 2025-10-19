# backend/optics.py
import cv2
import numpy as np
import math
from scipy.ndimage import gaussian_filter

def apply_optics(img: np.ndarray, params: dict) -> np.ndarray:
    """Apply zoom, FOV, distortion, vignette, chromatic, defocus."""
    if img is None:
        return img
    img = img.copy()
    h, w = img.shape[:2]

    # --- START FIX: Corrected Zoom Logic ---
    zoom = params.get('zoom', 1.0)
    if zoom != 1.0:
        zoom = max(1e-6, zoom) # Prevent zero or negative zoom

        if zoom > 1.0: # Zoom In (Crop and magnify)
            crop_h, crop_w = int(h / zoom), int(w / zoom)
            start_y, start_x = (h - crop_h) // 2, (w - crop_w) // 2
            cropped = img[start_y:start_y + crop_h, start_x:start_x + crop_w]
            img = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_CUBIC)
        else: # Zoom Out (Shrink and pad)
            new_h, new_w = int(h * zoom), int(w * zoom)
            if new_h > 0 and new_w > 0:
                resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
                pad_h = (h - new_h) // 2
                pad_w = (w - new_w) // 2
                # Create a black canvas of the original size
                padded_img = np.zeros_like(img)
                # Place the resized image in the center of the canvas
                padded_img[pad_h:pad_h + new_h, pad_w:pad_w + new_w] = resized
                img = padded_img
    # --- END FIX ---

    # FOV (Field of View) - This logic remains the same
    fov = params.get('fov', 60)
    if fov != 60:
        # This part of the logic can be complex and depends on the desired simulation
        # For simplicity, we'll keep the existing implementation which simulates
        # a change in perspective by scaling and cropping.
        scale = math.tan(math.radians(fov / 2)) / math.tan(math.radians(30))
        scale = max(1e-6, scale)
        new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
        resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        
        start_y = max(0, (new_h - h) // 2)
        start_x = max(0, (new_w - w) // 2)
        
        end_y = start_y + h
        end_x = start_x + w
        
        # Ensure the crop is within the bounds of the resized image
        if end_y > new_h or end_x > new_w:
             img = cv2.resize(resized_img, (w, h), interpolation=cv2.INTER_AREA)
        else:
             img = resized_img[start_y:end_y, start_x:end_x]


    # Lens Distortion
    h, w = img.shape[:2] # Recalculate dimensions in case FOV changed them
    dist_type = params.get('distortion_type', 'None')
    intensity = params.get('distortion_intensity', 0.0)
    if dist_type != 'None' and intensity != 0.0:
        k1 = intensity if dist_type == 'Barrel' else -intensity
        map_x, map_y = np.meshgrid(np.arange(w), np.arange(h))
        cx, cy = w / 2.0, h / 2.0
        
        dx, dy = map_x - cx, map_y - cy
        r_sq = dx**2 + dy**2
        norm_denom = (w/2)**2 + (h/2)**2
        if norm_denom == 0: norm_denom = 1
        r_sq_norm = r_sq / norm_denom
        
        radial = 1 + k1 * r_sq_norm
        map_x = cx + dx * radial
        map_y = cy + dy * radial
        img = cv2.remap(img, map_x.astype(np.float32), map_y.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

    # Vignetting
    h, w = img.shape[:2]
    vignette = params.get('vignetting', 0.0)
    if vignette > 0:
        y, x = np.ogrid[:h, :w]
        center_x, center_y = w / 2, h / 2
        radius = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        max_radius = np.sqrt(center_x**2 + center_y**2)
        if max_radius == 0: max_radius = 1
        mask = 1 - vignette * (radius / max_radius)**2
        img = (img * mask[:,:,np.newaxis]).clip(0, 255).astype(np.uint8)

    # Chromatic Aberration
    cab = params.get('chromatic_aberration', 0.0)
    if cab > 0:
        shift = int(cab * 5)
        if shift > 0:
            b, g, r = cv2.split(img)
            r_shifted = np.roll(r, shift, axis=1)
            b_shifted = np.roll(b, -shift, axis=1)
            r_shifted[:, :shift] = 0
            b_shifted[:, -shift:] = 0
            img = cv2.merge([b_shifted, g, r_shifted])

    # Defocus
    defocus = params.get('defocus', 0.0)
    if defocus > 0:
        sigma = defocus * 2.5
        img = gaussian_filter(img, sigma=(sigma, sigma, 0))

    return img