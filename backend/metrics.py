# backend/metrics.py
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr_func

def compute_ssim_psnr(img1: np.ndarray, img2: np.ndarray) -> tuple:
    if img1.shape != img2.shape:
        img1 = cv2.resize(img1, (img2.shape[1], img2.shape[0]))
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    s = ssim(gray1, gray2, data_range=gray2.max() - gray2.min())
    p = psnr_func(gray1, gray2, data_range=gray2.max() - gray2.min())
    return s, p

def compute_difference_map(img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
    if img1.shape != img2.shape:
        img1 = cv2.resize(img1, (img2.shape[1], img2.shape[0]))
    diff = cv2.absdiff(cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY), cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY))
    norm = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    diff_map = cv2.applyColorMap(norm, cv2.COLORMAP_JET)
    return diff_map