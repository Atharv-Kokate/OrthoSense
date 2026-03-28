import cv2
import mediapipe as mp
import numpy as np

class PoseEstimator:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5, 
            min_tracking_confidence=0.5,
            enable_segmentation=True
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def process(self, frame):
        """
        Extracts keypoints from the frame and draws a skeleton overlay automatically.
        Returns a dictionary of specified keypoints containing (x, y, confidence).
        """
        # Convert the BGR image to RGB format required by MediaPipe
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)
        
        keypoints = {}
        
        if getattr(results, 'pose_world_landmarks', None) is not None:
            world_landmarks = results.pose_world_landmarks.landmark
            
            def get_point(landmark_name):
                landmark = world_landmarks[getattr(self.mp_pose.PoseLandmark, landmark_name).value]
                return (landmark.x, landmark.y, landmark.z)
                
            try:
                keypoints = {
                    "left_shoulder": get_point("LEFT_SHOULDER"),
                    "right_shoulder": get_point("RIGHT_SHOULDER"),
                    "left_hip": get_point("LEFT_HIP"),
                    "right_hip": get_point("RIGHT_HIP"),
                    "left_knee": get_point("LEFT_KNEE"),
                    "right_knee": get_point("RIGHT_KNEE"),
                    "left_ankle": get_point("LEFT_ANKLE"),
                    "right_ankle": get_point("RIGHT_ANKLE")
                }
            except Exception as e:
                print(f"Error extracting keypoints: {e}")
            
            # Add premium dynamic body silhouette (Glassmorphism effect)
            if getattr(results, 'segmentation_mask', None) is not None:
                # Mask where the body is (greater than 0.5 confidence)
                condition = np.stack((results.segmentation_mask,) * 3, axis=-1) > 0.5
                
                # Create a sleek blue/cyan overlay
                bg_image = np.zeros(frame.shape, dtype=np.uint8)
                bg_image[:] = (255, 120, 0) # BGR for a nice vivid blue
                
                # Blend the blue overlay with the original frame inside the silhouette
                frame[:] = np.where(condition, cv2.addWeighted(frame, 0.4, bg_image, 0.6, 0), frame)
            
            # Draw skeleton overlay directly on the frame in-place
            self.mp_drawing.draw_landmarks(
                frame, 
                results.pose_landmarks, 
                self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
            )
            
        return keypoints
