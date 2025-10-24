import numpy as np
import cv2

class CameraSimulator:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.grid_size = 8
        self.circle_radius_world = 15.0
        self.grid_world_size = 500.0
        self.world_points_3d = self._create_world_points()

    def _create_world_points(self):
        points = []
        step = self.grid_world_size / self.grid_size
        offset = -self.grid_world_size / 2.0

        for i in range(self.grid_size + 1):
            points.append([offset + i * step, offset, 1000.0])
            points.append([offset + i * step, -offset, 1000.0])
            points.append([offset, offset + i * step, 1000.0])
            points.append([-offset, offset + i * step, 1000.0])

        for i in range(1, self.grid_size):
            for j in range(1, self.grid_size):
                cx = offset + i * step
                cy = offset + j * step
                points.append([cx, cy, 1000.0])
                
        return np.array(points, dtype=np.float32)

    def generate_simulated_image(self, focal_length, sensor_width, sensor_height, dist_coeffs, noise):
        fx = focal_length * (self.width / sensor_width)
        fy = focal_length * (self.height / sensor_height)
        cx = self.width / 2
        cy = self.height / 2
        
        K = np.array([
            [fx, 0, cx],
            [0, fy, cy],
            [0, 0, 1]
        ], dtype=np.float32)

        rvec = np.zeros(3, dtype=np.float32)
        tvec = np.zeros(3, dtype=np.float32)

        projected_points_2d, _ = cv2.projectPoints(
            self.world_points_3d,
            rvec,
            tvec,
            K,
            dist_coeffs
        )
        
        projected_points_2d = np.squeeze(projected_points_2d).astype(np.int32)
        
        img = np.ones((self.height, self.width), dtype=np.uint8) * 255
        
        num_line_pts = (self.grid_size + 1) * 4
        line_pts = projected_points_2d[:num_line_pts]
        for i in range(0, num_line_pts, 2):
            p1 = tuple(line_pts[i])
            p2 = tuple(line_pts[i+1])
            cv2.line(img, p1, p2, (0,), 1, lineType=cv2.LINE_AA)
            
        pixel_per_mm = (fx / focal_length + fy / focal_length) / 2
        projected_radius = int(self.circle_radius_world * (pixel_per_mm / 1000.0) * focal_length)
        
        circle_pts = projected_points_2d[num_line_pts:]
        for pt in circle_pts:
            cv2.circle(img, tuple(pt), projected_radius, (0,), -1, lineType=cv2.LINE_AA)
        img_float = img.astype(np.float32)
        noise = np.random.normal(0, noise, img_float.shape).astype(np.float32)
        img = img_float + noise
        img = np.clip(img, 0, 255).astype(np.uint8)

        return img

if __name__ == '__main__':
    simulator = CameraSimulator(width=800, height=600)

    base_focal_length = 35.0
    base_sensor_width = 36.0
    base_sensor_height = 24.0
    dist_coeffs_zero = np.zeros(5, dtype=np.float32)
    noise_zero = 0.0

    base_img = simulator.generate_simulated_image(
        base_focal_length,
        base_sensor_width,
        base_sensor_height,
        dist_coeffs_zero,
        noise_zero
    )
    cv2.imshow("base_image.png", base_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    base_focal_length = 100.
    base_sensor_width = 100.0
    base_sensor_height = 100.0
    dist_coeffs_zero = np.ones(5, dtype=np.float32)
    noise_zero = 100

    base_img = simulator.generate_simulated_image(
        base_focal_length,
        base_sensor_width,
        base_sensor_height,
        dist_coeffs_zero,
        noise_zero
    )
    cv2.imshow("base_image.png", base_img)
    cv2.imwrite("base_image.png", base_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()