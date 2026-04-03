import { useState, useEffect, useRef } from 'react';
import importedUseWebSocket, { ReadyState } from 'react-use-websocket';

const useWebSocket = importedUseWebSocket?.default || importedUseWebSocket;

export function useTelemetrySocket(patientId, exercise = 'squat', { muteVoice = false } = {}) {
  const socketUrl = `ws://localhost:8000/ws/track/${exercise}/${patientId}`;
  const [status, setStatus] = useState('connecting');
  const [isListening, setIsListening] = useState(false);
  const [telemetry, setTelemetry] = useState({
    repCount: 0,
    feedback: 'Connecting to OrthoSense AI...',
    errors: [],
  });
  
  // Track the most recently played feedback string to avoid speech overlap
  const lastSpokenFeedback = useRef('');
  const recognitionRef = useRef(null);

  const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket(socketUrl, {
    shouldReconnect: (closeEvent) => true,
    reconnectAttempts: 10,
    reconnectInterval: 3000,
  });

  // Store stable references for the speech handlers to use without re-registering
  const socketRef = useRef({ sendJsonMessage, readyState });
  useEffect(() => {
    socketRef.current = { sendJsonMessage, readyState };
  }, [sendJsonMessage, readyState]);

  // Initialize 2-Way Voice Communication Loop exactly ONCE
  useEffect(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      console.warn("Browser requires Chrome/Edge/Safari for Speech API!");
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript.trim().toLowerCase();
      console.log("🗣️ PATIENT SPOKE:", transcript);
      
      const currentSocket = socketRef.current;
      if (transcript.length > 0 && currentSocket.readyState === ReadyState.OPEN) {
        window.speechSynthesis.cancel();
        currentSocket.sendJsonMessage({ "patient_vocal_command": transcript });
      }
    };

    recognition.onerror = (event) => {
        console.error("Speech Recognition Error:", event.error);
        if (event.error === 'not-allowed') {
            alert("Microphone is blocked by the browser. Please check Edge/Chrome site permissions.");
        } else if (event.error === 'network') {
            alert("Speech recognition failed due to network error. This browser feature needs internet access.");
        }
        setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) recognitionRef.current.abort();
    };
  }, []);

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      try { 
        recognitionRef.current.start(); 
      } catch (e) {
        console.error("Failed to start listening:", e);
        alert("Failed to access microphone via Web Speech API: " + e.message);
      }
    }
  };

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
            if (!muteVoice && 'speechSynthesis' in window) {
              const utterance = new SpeechSynthesisUtterance(data.llm_feedback);
              utterance.rate = 1.0;
              utterance.pitch = 1.1; // Make it sound slightly more engaging    
              window.speechSynthesis.speak(utterance);
            }
            lastSpokenFeedback.current = data.llm_feedback;
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

  return { status, telemetry, sendJsonMessage, isListening, startListening };
}