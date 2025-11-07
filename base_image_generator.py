import numpy as np
import cv2

class CameraSimulator:
    def __init__(self, width=800, height=600, pattern_size=(7, 7)):
        self.width = width
        self.height = height
        # This now correctly accepts a (rows, cols) tuple
        self.pattern_size = pattern_size 
        self.square_size_world = 25.0
        self.world_points_3d = self._create_world_grid_points()

    def _create_world_grid_points(self):
        rows, cols = self.pattern_size
        objp = np.zeros((rows * cols, 3), np.float32)
        objp[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2) * self.square_size_world
        objp[:, 0] -= (cols - 1) * self.square_size_world / 2
        objp[:, 1] -= (rows - 1) * self.square_size_world / 2
        objp[:, 2] = 1000.0
        return objp

    def generate_simulated_image(self, focal_length, sensor_width, sensor_height, dist_coeffs, noise):
        fx = focal_length * (self.width / sensor_width)
        fy = focal_length * (self.height / sensor_height)
        cx = self.width / 2
        cy = self.height / 2
        K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float32)
        rvec = np.zeros(3, dtype=np.float32)
        tvec = np.zeros(3, dtype=np.float32)
        projected_points_2d, _ = cv2.projectPoints(
            self.world_points_3d, rvec, tvec, K, dist_coeffs
        )
        
        if np.isnan(projected_points_2d).any():
            return self.create_blank_image(self.height, self.width)

        base_img = self.create_blank_image(self.height, self.width)
        
        for p in projected_points_2d:
            x, y = int(p[0][0]), int(p[0][1])
            if 0 <= x < self.width and 0 <= y < self.height:
                cv2.circle(base_img, (x, y), 10, (0, 0, 0), -1)

        # Apply noise if any
        if noise > 0:
            noise_val = noise * 25.5 # Scale noise
            gauss = np.random.normal(0, noise_val, base_img.shape)
            noisy_img = np.clip(base_img.astype(np.float32) + gauss, 0, 255)
            base_img = noisy_img.astype(np.uint8)

        return base_img

    def create_blank_image(self, height, width):
        return np.ones((height, width, 3), dtype=np.uint8) * 255