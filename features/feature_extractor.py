from utils.geometry import calculate_angle

class FeatureExtractor:
    def extract(self, keypoints):
        """
        Computes biomechanical features (angles, symmetry) from raw keypoints.
        Returns a dictionary of calculated features.
        """
        if not keypoints:
            return None
            
        try:
            # Vectors are natively 3D (X, Y, Z) now
            l_hip = keypoints["left_hip"]
            l_knee = keypoints["left_knee"]
            l_ankle = keypoints["left_ankle"]
            left_knee_angle = calculate_angle(l_hip, l_knee, l_ankle)
            
            r_hip = keypoints["right_hip"]
            r_knee = keypoints["right_knee"]
            r_ankle = keypoints["right_ankle"]
            right_knee_angle = calculate_angle(r_hip, r_knee, r_ankle)
            
            l_shoulder = keypoints["left_shoulder"]
            # Back angle uses full 3D bio-metric coordinates
            back_angle = calculate_angle(l_shoulder, l_hip, l_knee)
            
            symmetry_score = abs(left_knee_angle - right_knee_angle)
            
            return {
                "left_knee_angle": left_knee_angle,
                "right_knee_angle": right_knee_angle,
                "back_angle": back_angle,
                "symmetry_score": symmetry_score
            }
        except KeyError as e:
            print(f"Missing keypoint for feature extraction: {e}")
            return None
