import numpy as np
import cv2

class CameraSimulator:
    def __init__(self, width=800, height=600, grid_size=7):
        self.width = width
        self.height = height
        self.pattern_size = (grid_size, grid_size) 
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
        img = np.ones((self.height, self.width), dtype=np.uint8) * 255
        for pt in projected_points_2d:
            cv2.circle(img, tuple(pt.ravel().astype(int)), 10, (0,), -1, lineType=cv2.LINE_AA)
        img_float = img.astype(np.float32)
        noise_array = np.random.normal(0, noise, img_float.shape).astype(np.float32)
        img_with_noise = img_float + noise_array
        img_final = np.clip(img_with_noise, 0, 255).astype(np.uint8)
        return img_final