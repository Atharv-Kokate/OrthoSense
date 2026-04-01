# OrthoSense: AI-Powered Biometric Fitness Coach

**OrthoSense** is an intelligent fitness application that utilizes advanced computer vision and biomechanical analysis to provide real-time posture correction and personalized fitness guidance.

## 🚀 Features

- **3D Pose Estimation**: Leverages MediaPipe to capture high-fidelity 3D coordinates of body joints.
- **Dynamic Time Warping (DTW)**: Compares live movement sequences against a pre-recorded "Golden Rep" to detect minute temporal and spatial deviations.
- **Intelligent Feedback Engine**: Uses a rule-based system combined with DTW deviation scores to generate precise, actionable voice and text feedback.
- **Calibration System**: Allows users to record and save their "perfect" repetition for personalized baseline tracking.
- **Multi-Exercise Support**: Built to scale for various exercises (Squats, Lunges, etc.).

## 🛠️ Installation

### Prerequisites
- Python 3.12+
- A working webcam

### Setup
1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd OrthoSense
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## 🏃 Usage

### Running the Application
Execute the main script to start the fitness coach:

```bash
python main.py
```

### Controls
- **Q**: Quit the application.
- **C**: **Calibrate**. Press this to record your first "Golden Rep" (perfect repetition). The system will save this baseline for future comparisons.

## 📂 Project Structure

- `main.py`: The entry point for the application.
- `pose/`: Contains the MediaPipe integration for pose detection.
- `features/`: Handles the extraction of biomechanical features (angles, symmetry).
- `diagnosis/`: Implements the DTW engine and rule-based error detection.
- `agents/`: Contains the logic for decision-making and generating feedback.
- `config/`: Stores exercise configurations and user calibration data.
