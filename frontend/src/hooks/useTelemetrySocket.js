import { useState, useEffect, useRef } from 'react';
import useWebSocket, { ReadyState } from 'react-use-websocket';

export function useTelemetrySocket(patientId) {
  const socketUrl = `ws://localhost:8000/ws/track/${patientId}`;
  const [status, setStatus] = useState('connecting');
  const [telemetry, setTelemetry] = useState({
    repCount: 0,
    feedback: 'Connecting to OrthoSense AI...',
    errors: [],
  });
  
  // Track the most recently played feedback string to avoid speech overlap
  const lastSpokenFeedback = useRef('');

  const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket(socketUrl, {
    shouldReconnect: (closeEvent) => true,
    reconnectAttempts: 10,
    reconnectInterval: 3000,
  });

  // Track the raw connection state
  useEffect(() => {
    if (readyState === ReadyState.OPEN) setStatus('connected');
    else if (readyState === ReadyState.CLOSED) setStatus('disconnected');
    else if (readyState === ReadyState.CONNECTING) setStatus('connecting');
  }, [readyState]);

  // Track messages from backend AI brains
  useEffect(() => {
    if (lastJsonMessage !== null) {
      const data = lastJsonMessage;
      
      if (data.status === 'tracking') {
        setStatus('tracking');
        
        let newFeedback = prev => prev.feedback;
        if (data.llm_feedback) {
          newFeedback = data.llm_feedback;
        } else if (data.errors && data.errors.length === 0) {
          newFeedback = 'Great form!';
        }

        // Voice Feedback Trigger using built-in Text-To-Speech
        if (data.llm_feedback && data.llm_feedback !== lastSpokenFeedback.current) {
          if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(data.llm_feedback);
            utterance.rate = 1.0; 
            utterance.pitch = 1.1; // Make it sound slightly more engaging
            window.speechSynthesis.speak(utterance);
            lastSpokenFeedback.current = data.llm_feedback;
          }
        }

        setTelemetry(prev => ({
          ...prev,
          repCount: data.rep_count || prev.repCount,
          feedback: typeof newFeedback === 'string' ? newFeedback : newFeedback(prev),
          errors: data.errors || [],
        }));
      } else if (data.status === 'buffering') {
        setStatus('buffering');
        setTelemetry(prev => ({
          ...prev,
          feedback: 'Gathering baseline tracking data...',
        }));
      }
    }
  }, [lastJsonMessage]);

  return { status, telemetry, sendJsonMessage };
}
