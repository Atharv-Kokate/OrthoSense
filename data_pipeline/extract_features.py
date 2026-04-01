import cv2
import pandas as pd
import os
import sys

# Hack to allow importing from parent directory while inside data_pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pose.pose_estimator import PoseEstimator
from features.feature_extractor import FeatureExtractor

def record_dataset():
    print("="*50)
    print("OrthoSense Clinical Dataset Extractor")
    print("="*50)
    
    label = input("Enter the class label you are about to perform (e.g., 'perfect_squat', 'knee_caving_error', 'forward_lean_error'): ").strip()
    if not label:
        print("Label cannot be empty. Exiting.")
        return

    # Initialize Ortho Engine modules
    pose_estimator = PoseEstimator()
    feature_extractor = FeatureExtractor()
    
    # Dataset Tracking
    data_rows = []
    csv_filename = "data_pipeline/clinical_dataset.csv"
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
        
    print(f"\n[RECORDING] Action: '{label}'")
    print("Press 'q' when you are finished recording this action to save and exit.")
    
    frames_recorded = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.resize(frame, (640, 480))
        
        # 1. Pose Perception (returns true 3D sequences)
        keypoints = pose_estimator.process(frame)
        
        # 2. Extract 3D Biomechanical features
        features = feature_extractor.extract(keypoints)
        
        if features:
            # We only extract the fundamental biomechanical scalars the LSTM needs
            # The features dictionary output looks like {"left_knee_angle": 178.5, ...}
            row = {
                "left_knee_angle": features.get("left_knee_angle", 0),
                "right_knee_angle": features.get("right_knee_angle", 0),
                "back_angle": features.get("back_angle", 0),
                "symmetry_score": features.get("symmetry_score", 0),
                "label": label # TARGET CLASS FOR LSTM
            }
            data_rows.append(row)
            frames_recorded += 1
            
            # Draw visual feedback
            cv2.putText(frame, f"Recording: {label}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, f"Rows Extracted: {frames_recorded}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Print core angles to mirror what the system tracks
            cv2.putText(frame, f"L Knee: {features.get('left_knee_angle', 0):.0f}", (10, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            cv2.putText(frame, f"R Knee: {features.get('right_knee_angle', 0):.0f}", (10, 425), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            cv2.putText(frame, f"Back: {features.get('back_angle', 0):.0f}", (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        cv2.imshow("Dataset Extraction Mode (Press 'q' to Stop)", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()
    
    # --- SAVE TO CSV APPEND MODE ---
    if data_rows:
        df = pd.DataFrame(data_rows)
        # If the file exists, append without headers. If it's new, write headers.
        file_exists = os.path.isfile(csv_filename)
        df.to_csv(csv_filename, mode='a', header=not file_exists, index=False)
        print(f"\nSUCCESS: Appended {frames_recorded} rows to {csv_filename}!")
        print("Run this script again for your next action class (e.g. 'knee_caving_error').")
    else:
        print("\nSkipped saving: No frames were detected containing a human.")

if __name__ == "__main__":
    record_dataset()
