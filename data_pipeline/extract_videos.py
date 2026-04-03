import cv2
import pandas as pd
import os
import sys
import glob

# Allow importing from parent directory while inside data_pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pose.pose_estimator import PoseEstimator
from features.feature_extractor import FeatureExtractor

def process_video_dataset(dataset_path, label_name, output_csv="data_pipeline/lunge_dataset.csv"):
    print("="*50)
    print(f"ðŸ“¹ OrthoSense Video Dataset Extractor")
    print(f"Processing folder: {dataset_path}")
    print(f"Target Label: {label_name}")
    print("="*50)

    # Find all video files (.avi, .mp4)
    video_files = glob.glob(os.path.join(dataset_path, "**", "*.avi"), recursive=True)
    video_files.extend(glob.glob(os.path.join(dataset_path, "**", "*.mp4"), recursive=True))

    if not video_files:
        print(f"âŒ No video files found in {dataset_path}")
        return

    print(f"Found {len(video_files)} videos. Initializing AI Vision Models...")

    pose_estimator = PoseEstimator()
    feature_extractor = FeatureExtractor()

    all_data_rows = []
    total_frames = 0
    videos_processed = 0

    for idx, video_path in enumerate(video_files):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"[Warning] Could not open video: {video_path}")
            continue

        print(f"[{idx+1}/{len(video_files)}] Processing {os.path.basename(video_path)}...", end="", flush=True)
        frames_this_video = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Resize slightly to mimic inference feed
            frame = cv2.resize(frame, (640, 480))

            # Run Neural Perception
            keypoints = pose_estimator.process(frame)
            features = feature_extractor.extract(keypoints)

            if features:
                row = {
                    "left_knee_angle": features.get("left_knee_angle", 0),
                    "right_knee_angle": features.get("right_knee_angle", 0),
                    "back_angle": features.get("back_angle", 0),
                    "symmetry_score": features.get("symmetry_score", 0),
                    "label": label_name
                }
                all_data_rows.append(row)
                frames_this_video += 1

        total_frames += frames_this_video
        videos_processed += 1
        print(f" ({frames_this_video} frames)")
        
        cap.release()

    print("\n" + "="*50)
    print("âœ… BATCH EXTRACTION COMPLETE")
    print(f"Videos Processed: {videos_processed}")
    print(f"Total Frames Converted: {total_frames}")
    
    if all_data_rows:
        df = pd.DataFrame(all_data_rows)
        file_exists = os.path.isfile(output_csv)
        df.to_csv(output_csv, mode='a', header=not file_exists, index=False)
        print(f"Dataset successfully appended to: {output_csv}")
    else:
        print("No human subjects detected in any frames.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Batch convert video dataset to CSV features.")
    parser.add_argument("--dir", type=str, required=True, help="Path to video directory")
    parser.add_argument("--label", type=str, required=True, help="Label for these videos (e.g. perfect_lunge)")
    parser.add_argument("--out", type=str, default="data_pipeline/lunge_dataset.csv", help="Output CSV path")
    args = parser.parse_args()

    process_video_dataset(args.dir, args.label, args.out)