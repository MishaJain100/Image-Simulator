import cv2
import numpy as np
import requests
from io import BytesIO
import os
import sys

# Step 1: Download a free CC0 grayscale landscape (Unsplash example: B&W mountain scene)
url = "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80"  # Direct high-res JPEG link (CC0, natural B&W landscape)

# Try downloading the image, but validate the response. If download fails or is empty,
# fall back to a local resource image in resources/images/uploaded_default.png.
try:
	response = requests.get(url, timeout=10)
	if not response.ok or not response.content:
		raise RuntimeError(f"Bad response: status={getattr(response, 'status_code', None)} size={len(getattr(response, 'content', b''))}")
	img_array = np.frombuffer(response.content, dtype=np.uint8)
	base_color = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
	if base_color is None:
		raise RuntimeError("cv2.imdecode returned None (corrupt or unsupported image data)")
	base_gray = cv2.cvtColor(base_color, cv2.COLOR_BGR2GRAY)
	base = cv2.resize(base_gray, (800, 400), interpolation=cv2.INTER_LINEAR)
	cv2.imwrite('base_natural.png', base)
	print(f"Base saved: base_natural.png ({base.shape[1]}x{base.shape[0]}, grayscale) [downloaded]")
except Exception as e:
	# Attempt local fallback
	script_dir = os.path.dirname(os.path.abspath(__file__))
	fallback = os.path.join(script_dir, 'resources', 'images', 'uploaded_default.png')
	print(f"Warning: failed to download or decode image ({e}). Trying local fallback: {fallback}")
	if os.path.exists(fallback):
		base_color = cv2.imread(fallback, cv2.IMREAD_COLOR)
		if base_color is None:
			print(f"Fallback found but failed to read with OpenCV: {fallback}")
			sys.exit(1)
		base_gray = cv2.cvtColor(base_color, cv2.COLOR_BGR2GRAY)
		base = cv2.resize(base_gray, (800, 400), interpolation=cv2.INTER_LINEAR)
		cv2.imwrite('base_natural.png', base)
		print(f"Base saved: base_natural.png ({base.shape[1]}x{base.shape[0]}, grayscale) [fallback]")
	else:
		print("No fallback image available. Exiting.")
		sys.exit(1)

# Step 2: Apply synthetic distortion to create target (radial k1=0.05, slight barrel)
h, w = base.shape
cx, cy = w / 2, h / 2
K = np.array([[600, 0, cx], [0, 600, cy], [0, 0, 1]], dtype=np.float32)  # Assumed focal ~600px
D = np.array([0.05, 0, 0, 0], dtype=np.float32)  # k1=0.05, k2=p1=p2=0

# Compute distortion map (forward distort)
map_x, map_y = cv2.initUndistortRectifyMap(K, D, None, K, (w, h), cv2.CV_32FC1)
target = cv2.remap(base, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
cv2.imwrite('target_natural.png', target)
print(f"Target saved: target_natural.png (distorted with k1=0.05)")

# Optional: Visualize
cv2.imshow('Base (Clean)', base)
cv2.imshow('Target (Distorted)', target)
cv2.waitKey(0)
cv2.destroyAllWindows()