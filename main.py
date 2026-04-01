import cv2
import sys
from pose.pose_estimator import PoseEstimator
from features.feature_extractor import FeatureExtractor
from memory.temporal_buffer import TemporalBuffer
from diagnosis import rules_engine
from diagnosis.lstm_engine import LSTMEngine
from agents.decision_agent import DecisionAgent
from agents.feedback_agent import generate as generate_feedback
from voice.speech_engine import SpeechEngine
from config.calibration_manager import CalibrationManager

def main():
    print("=" * 45)
    print(" OrthoSense AI Phase 3: 3D Tracking & DTW")
    print("=" * 45)
    print("Available models: squat, lunge")
    exercise = input("Select exercise > ").strip().lower()
    
    if exercise not in ["squat", "lunge"]:
        print(f"Error: Exercise '{exercise}' is not supported yet. Exiting.")
        sys.exit(1)
        
    print(f"\nInitializing 3D {exercise.capitalize()} Tracker...")
    
    # Initialize all modules
    pose_estimator = PoseEstimator()
    feature_extractor = FeatureExtractor()
    temporal_buffer = TemporalBuffer(maxlen=30)
    lstm_engine = LSTMEngine(exercise=exercise)
    decision_agent = DecisionAgent(cooldown=3.0)
    speech_engine = SpeechEngine()
    calibration_manager = CalibrationManager()
    
    # 1. Load Calibration
    golden_rep = calibration_manager.load_golden_rep(exercise)
    calibration_mode = False
    calibration_buffer = []  # Holds the sequence during calibration
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
        
    print("\n--- System Ready ---")
    if golden_rep:
        print(f"SUCCESS: Loaded existing Baseline Golden Rep for {exercise}!")
        print("Press 'c' to Record a New Baseline Model. Press 'q' to Quit.")
    else:
        print("WARNING: No baseline detected.")
        print("Press 'c' to start recording your 1st perfect repetition!")
    
    # State tracking for UI overlay
    active_feedback_text = "Press 'c' to Calibrate Baseline!" if not golden_rep else "Tracking Active..."
    active_feedback_level = "warning" if not golden_rep else "info"
        
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.resize(frame, (640, 480))
        
        # KEYBOARD CONTROLS
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            print(">>> STARTING NEW CALIBRATION RECORDING <<<")
            calibration_mode = True
            calibration_buffer = []
            speech_engine.speak("Calibration active. Perform one perfect repetition now.")
            active_feedback_text = "RECORDING CALIBRATION SEQUENCE"
            active_feedback_level = "warning"
        
        # 1. Pose Perception (returns true 3D sequence masks)
        keypoints = pose_estimator.process(frame)
        
        # 2. Feature Extraction (Numpy 3D mathematical dot-products)
        features = feature_extractor.extract(keypoints)
        
        if features:
            if calibration_mode:
                # Store exactly 60 metric frames (roughly 2 seconds) for the golden baseline
                calibration_buffer.append(features)
                cv2.putText(frame, f"Recording: {len(calibration_buffer)} / 60 frames", (10, 410), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                if len(calibration_buffer) >= 60:
                    calibration_manager.save_golden_rep(exercise, calibration_buffer)
                    golden_rep = calibration_buffer
                    calibration_mode = False
                    speech_engine.speak("Baseline recorded and saved safely. DTW Tracking Enagaged.")
                    active_feedback_text = "Baseline Recorded & Active!"
                    active_feedback_level = "success"
            else:
# REGULAR TRACKING MODE (PHASE 4: LSTM DEEP LEARNING ACTIVE)
                temporal_buffer.add(features)
                history = temporal_buffer.get_history()
                lstm_seq = temporal_buffer.get_lstm_sequence()

                # Neural Network takes priority over hardcoded rules
                if lstm_engine.ready and lstm_seq is not None:
                    diagnosis = lstm_engine.analyze(lstm_seq)
                else:
                    # Fallback to older diagnosis logic if buffer isn't full or model missing
                    diagnosis = rules_engine.analyze(features, history, exercise, golden_rep)

                decision = decision_agent.decide(diagnosis, history)
                
                if decision:
                    feedback = generate_feedback(decision)
                    if feedback:
                        active_feedback_text = feedback["text"]
                        active_feedback_level = feedback["level"]
                        speech_engine.speak(active_feedback_text)
                        
                elif not diagnosis.get("errors") and golden_rep:
                    active_feedback_text = "Perfect form! Sequence matches baseline."
                    active_feedback_level = "success"
            
            # -- UI Rendering --
            cv2.putText(frame, f"L Knee (3D): {features.get('left_knee_angle', 0):.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"R Knee (3D): {features.get('right_knee_angle', 0):.1f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Back (3D): {features.get('back_angle', 0):.1f}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Determine color 
            if active_feedback_level == "critical":
                color = (0, 0, 255)
            elif active_feedback_level == "warning":
                color = (0, 255, 255)
            else:
                color = (0, 255, 0)
                
            # Render Feedback string
            cv2.putText(frame, active_feedback_text, (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow(f"OrthoSense Deep Biometric Analyzer - {exercise.capitalize()}", frame)
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
