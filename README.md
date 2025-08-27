# Image-Simulator
A modular, physics-based image formation simulator for industrial cameras, enabling virtual testing of optical and sensor effects with interactive parameter control.

# Modular Image Formation Simulator for Industrial Cameras

This project presents a physics-based, modular simulator for modeling the image formation pipeline of industrial cameras. The tool enables engineers and researchers to virtually analyze and optimize camera behavior under diverse optical and environmental conditions—before physical deployment—reducing costs and improving design robustness.

Unlike data-driven or black-box simulation tools, this simulator uses principles from optics and classical computer vision to provide transparent, tunable models for image degradation. With an interactive interface for real-time adjustment of parameters, users can simulate lens distortion, lighting, sensor noise, and more, while comparing outputs to real-world camera captures using quantitative metrics.

---

## Features

### Core Simulation Capabilities

- **Camera Optics Simulation**:
  - Adjustable **zoom**, **field of view**, and **resolution**
  - Simulate **lens distortions** including barrel and pincushion
  - Add **chromatic aberration**, **defocus blur**, and **vignetting**

- **Lighting and Illumination**:
  - Directional and ambient lighting models
  - Control **intensity**, **brightness**, **light direction**, and **shadow geometry**
  - Add **specular reflections** using the Phong model

- **Sensor and Capture Effects**:
  - Simulate **sensor noise**, **exposure**, **dynamic range**, and **ISO sensitivity**
  - Compare **CCD vs. CMOS** sensor characteristics
  - Emulate **color filter arrays** (e.g., Bayer pattern)

- **Image Upload and Visualization**:
  - Upload a real-world image
  - Apply simulation to visualize how an industrial camera would capture it
  - Live comparison with side-by-side simulated and original image

- **Evaluation and Analysis**:
  - Compute **SSIM** (Structural Similarity) and **PSNR** (Peak Signal-to-Noise Ratio)
  - Validate against real industrial camera captures
  - Export synthetic images for downstream use

- **Advanced Features**:
  - **Parameter Estimation**: Automatically infer camera noise or distortion from real images
  - **Multi-Camera Support**: Simulate stereo rigs or multi-view setups
  - Generate **synthetic datasets** for training vision systems without deep learning

---

## Installation

_Will be added later._
