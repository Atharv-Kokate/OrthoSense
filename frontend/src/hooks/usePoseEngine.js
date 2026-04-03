import { useEffect, useRef } from 'react';

const Pose = window.Pose;
const Camera = window.Camera;

const calculateAngle = (a, b, c) => {
  const radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
  let angle = Math.abs((radians * 180.0) / Math.PI);
  if (angle > 180.0) angle = 360 - angle;
  return angle;
};

export function usePoseEngine(webcamRef, canvasRef, onTelemetryData) {
  // Use ref to avoid re-triggering the huge MediaPipe useEffect 
  // every time the parent component re-renders and creates a new callback reference.
  const telemetryCallbackRef = useRef(onTelemetryData);
  
  useEffect(() => {
    telemetryCallbackRef.current = onTelemetryData;
  }, [onTelemetryData]);

  useEffect(() => {
    if (!Pose || !Camera) {
      console.warn("MediaPipe variables not found on window object.");
      return;
    }

    const pose = new Pose({
      locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`,
    });

    pose.setOptions({
      modelComplexity: 1,
      smoothLandmarks: true,
      enableSegmentation: false,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5,
    });

    let camera = null;

    const onResults = (results) => {
      if (!canvasRef.current) return;
      const canvasCtx = canvasRef.current.getContext('2d');
      canvasCtx.save();
      canvasCtx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
      
      // Simplistic drawing for performance
      if (results.poseLandmarks) {
        for (const landmark of results.poseLandmarks) {
          canvasCtx.beginPath();
          canvasCtx.arc(landmark.x * 640, landmark.y * 480, 2, 0, 2 * Math.PI);
          canvasCtx.fillStyle = '#00FF00';
          canvasCtx.fill();
        }

        // Calculate angles
        const landmarks = results.poseLandmarks;
        
        const leftHip = landmarks[23];
        const leftKnee = landmarks[25];
        const leftAnkle = landmarks[27];
        const lKneeAngle = calculateAngle(leftHip, leftKnee, leftAnkle);

        const rightHip = landmarks[24];
        const rightKnee = landmarks[26];
        const rightAnkle = landmarks[28];
        const rKneeAngle = calculateAngle(rightHip, rightKnee, rightAnkle);

        const leftShoulder = landmarks[11];
        const backAngle = calculateAngle(leftShoulder, leftHip, leftKnee);
        const symmetry = Math.abs(lKneeAngle - rKneeAngle);

        const POSE_NAMES = [
          'nose', 'left_eye_inner', 'left_eye', 'left_eye_outer', 'right_eye_inner', 'right_eye', 'right_eye_outer',
          'left_ear', 'right_ear', 'mouth_left', 'mouth_right', 'left_shoulder', 'right_shoulder', 'left_elbow',
          'right_elbow', 'left_wrist', 'right_wrist', 'left_pinky', 'right_pinky', 'left_index', 'right_index',
          'left_thumb', 'right_thumb', 'left_hip', 'right_hip', 'left_knee', 'right_knee', 'left_ankle', 'right_ankle',
          'left_heel', 'right_heel', 'left_foot_index', 'right_foot_index'
        ];
        
        let raw_dict = {};
        landmarks.forEach((lm, idx) => {
            raw_dict[POSE_NAMES[idx]] = lm;
        });

        // Bubble data up to whoever wants to send it to the backend
        if (telemetryCallbackRef.current) {
          telemetryCallbackRef.current({
            raw_landmarks: raw_dict,
            left_knee_angle: lKneeAngle,
            right_knee_angle: rKneeAngle,
            back_angle: backAngle,
            symmetry_score: symmetry
          });
        }
      }
      canvasCtx.restore();
    };

    pose.onResults(onResults);

    if (
      typeof window !== 'undefined' &&
      webcamRef.current &&
      webcamRef.current.video
    ) {
      camera = new Camera(webcamRef.current.video, {
        onFrame: async () => {
          if (webcamRef.current && webcamRef.current.video) {
            await pose.send({ image: webcamRef.current.video });
          }
        },
        width: 640,
        height: 480,
      });
      camera.start();
    }

    return () => {
      if (camera) camera.stop();
      pose.close();
    };
  }, [webcamRef, canvasRef]); // we exclude the callback intentionally by tracking via ref

}