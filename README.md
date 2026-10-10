# Autonomous Lane Detection

This project implements a computer vision pipeline designed to detect road boundaries and highlight drivable space from dashcam footage. It utilizes classical mathematical techniques to dynamically map lane lines and adapt to specific camera perspectives.

## Features

* **Classical CV Pipeline:** Utilizes Grayscale conversion, Gaussian Blur, Canny Edge Detection, and Region of Interest (ROI) masking to isolate structural road edges.
* **Mathematical Extrapolation:** Uses Hough Line Transforms and NumPy (`polyfit`) to calculate lane slopes, filter visual noise, and extrapolate stable, full-frame lane boundaries.
* **Interactive GUI:** Built with Tkinter to provide a native file-picker experience for loading variable-resolution video files.
* **Dynamic Rendering:** Features adaptive window scaling and dynamic transparent polygon overlays using OpenCV to map the drivable space.

## Tech Stack

* **Language:** Python 3.11
* **Libraries:** OpenCV (`cv2`), NumPy, Tkinter

## Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/YourUsername/Lane-Detection.git](https://github.com/YourUsername/Lane-Detection.git)
   cd Lane-Detection