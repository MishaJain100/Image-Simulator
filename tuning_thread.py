# tuning_thread.py
import numpy as np
from PyQt5.QtCore import pyqtSignal, QThread
import cv2
from scipy.optimize import minimize
import traceback

class TuningThread(QThread):
    """
    Finds distortion parameters by matching features (e.g., AKAZE) between
    a clean base image and a distorted target image, then optimizing
    the parameters (f, k1, cx, cy) to minimize the reprojection error.
    """
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal(dict)

    def __init__(self, base_image_gray, target_image_gray, locks, defaults):
        super().__init__()
        
        self.base_image = base_image_gray
        self.target_image = target_image_gray

        # === NEW RESIZING LOGIC ===
        # Check if image shapes are different
        if self.base_image.shape != self.target_image.shape:
            print(f"Image shapes differ: Base={self.base_image.shape}, Target={self.target_image.shape}")
            print(f"Resizing target image to match base image dimensions for analysis...")
            
            # Get dimensions of the base image (h, w)
            base_h, base_w = self.base_image.shape
            
            # Resize target image to match base dimensions
            self.target_image = cv2.resize(self.target_image, (base_w, base_h), interpolation=cv2.INTER_LINEAR)
            
            print(f"Target image resized to {self.target_image.shape}")
        # === END NEW RESIZING LOGIC ===
        
        # Now, self.base_image and self.target_image are guaranteed to be the same size
        
        self.locks = locks
        self.defaults = defaults
        self.iteration = 0
        self.max_iterations = 50  # Optimizer iterations

    def _unflatten_params(self, x_flat):
        """Convert flat vector [f, k1, cx, cy] -> readable dict."""
        f, k1, cx, cy = x_flat
        return {'focal_length': f, 'k1': k1, 'cx': cx, 'cy': cy}

    @staticmethod
    def _find_and_match_features(img1, img2):
        """
        Detects and matches AKAZE features between two images.
        """
        try:
            # 1. Initialize AKAZE detector
            # (AKAZE is robust, fast, and license-free)
            detector = cv2.AKAZE_create()

            # 2. Find keypoints and descriptors
            print("Finding features in base image...")
            k_base, d_base = detector.detectAndCompute(img1, None)
            print(f"Found {len(k_base)} base features.")
            
            print("Finding features in target image (post-resize)...")
            k_target, d_target = detector.detectAndCompute(img2, None)
            print(f"Found {len(k_target)} target features.")

            if d_base is None or d_target is None:
                raise Exception("No descriptors found in one or both images.")

            # 3. Match descriptors using Brute-Force Matcher
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(d_base, d_target)

            # 4. Sort matches by distance (best matches first)
            matches = sorted(matches, key=lambda x: x.distance)
            
            # 5. Keep only the top 100 matches
            # This filters out noise and speeds up optimization
            N_MATCHES = 100
            good_matches = matches[:N_MATCHES]
            if len(good_matches) < 20: # Need a minimum number to optimize
                 raise Exception(f"Not enough good matches found ({len(good_matches)}).")
            print(f"Using top {len(good_matches)} matches.")

            # 6. Extract (x,y) coordinates for the matched points
            base_points = np.float32([k_base[m.queryIdx].pt for m in good_matches]).reshape(-1, 2)
            target_points = np.float32([k_target[m.trainIdx].pt for m in good_matches]).reshape(-1, 2)
            
            return base_points, target_points

        except cv2.error as e:
            print(f"OpenCV Error during feature matching: {e}")
            return None, None
        except Exception as e:
            print(f"Error during feature matching: {e}")
            return None, None

    @staticmethod
    def _objective_function(params, base_points, target_points):
        """
        The error function for the optimizer.
        It calculates the distance between where the target points *should*
        be (given the 'params') and where they *actually* are.
        """
        fx, k1, cx, cy = params
        fy = fx  # Assume square pixels

        # 1. Normalize base points (pixel coords -> normalized coords)
        # x_n = (u - cx) / fx
        x_n = (base_points[:, 0] - cx) / fx
        y_n = (base_points[:, 1] - cy) / fy

        # 2. Apply radial distortion (k1 only)
        # r^2 = x_n^2 + y_n^2
        r2 = x_n * x_n + y_n * y_n
        radial = 1.0 + k1 * r2
        
        # x_d = x_n * (1 + k1*r^2)
        x_d = x_n * radial
        y_d = y_n * radial

        # 3. Un-normalize (normalized coords -> projected pixel coords)
        # u_proj = x_d * fx + cx
        u_proj = x_d * fx + cx
        v_proj = y_d * fy + cy

        # 4. Create the array of projected points
        projected_points = np.stack((u_proj, v_proj), axis=1)

        # 5. Calculate the error (L2 norm)
        # This is the sum of distances between each projected point
        # and its corresponding actual target point.
        error = np.sum(np.linalg.norm(projected_points - target_points, axis=1))
        
        return error

    def run(self):
        try:
            # ---------- 1. Find Features ----------
            # self.base_image and self.target_image are now guaranteed to be the same size
            base_pts, target_pts = self._find_and_match_features(self.base_image, self.target_image)
            
            if base_pts is None:
                # Error already printed in the function
                raise Exception("Feature matching failed.")
            
            self.progress_updated.emit(10) # 10% for feature matching

            # ---------- 2. Set up Optimization ----------
            h, w = self.base_image.shape
            
            # Initial guess from the defaults
            initial_guess = np.array([
                self.defaults['focal_length'],
                self.defaults['k1'],
                self.defaults['cx'],
                self.defaults['cy']
            ])
            
            # Parameter bounds
            bounds = [
                (0.2 * w, 2.0 * w),  # focal length (fx)
                (-0.5, 0.5),         # k1 (radial distortion)
                (0.25 * w, 0.75 * w),# cx (principal point x)
                (0.25 * h, 0.75 * h) # cy (principal point y)
            ]
            
            # Apply locks from UI
            if self.locks.get('focal_length'):
                f_lock = self.defaults['focal_length']
                bounds[0] = (f_lock, f_lock)
                initial_guess[0] = f_lock
                
            if self.locks.get('distortion'):
                k1_lock = self.defaults['k1']
                bounds[1] = (k1_lock, k1_lock)
                initial_guess[1] = k1_lock

            print("Starting optimization...")
            self.iteration = 0 # Reset iteration count for callback
            
            # ---------- 3. Run Optimizer ----------
            res = minimize(
                self._objective_function,
                initial_guess,
                args=(base_pts, target_pts),
                method='L-BFGS-B',
                bounds=bounds,
                callback=self.callback,
                options={'maxiter': self.max_iterations, 'ftol': 1e-7, 'gtol': 1e-6}
            )

            if res.success:
                print("Optimization successful.")
                params = self._unflatten_params(res.x)
                self.finished.emit(params)
            else:
                print(f"Optimization failed: {res.message}")
                raise Exception("Optimization failed to converge.")

        except Exception as e:
            print("\n!!!!!!!!!! TUNING THREAD CRASHED !!!!!!!!!!")
            traceback.print_exc()
            # Emit default parameters on failure
            self.finished.emit(self.defaults)

    def callback(self, xk):
        """
        Callback function for the optimizer to update progress.
        'xk' is the current parameter vector [f, k1, cx, cy].
        """
        self.iteration += 1
        
        # Calculate progress (10% base + 90% for iterations)
        prog = 10 + int((self.iteration / self.max_iterations) * 90)
        self.progress_updated.emit(min(prog, 99)) # Cap at 99% until finished
        
        f, k1, cx, cy = xk
        print(f"Iter {self.iteration:02d} | f {f:6.1f} | k1 {k1:+.4f} | cx,cy ({cx:.1f}, {cy:.1f})")