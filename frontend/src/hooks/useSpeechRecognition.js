/**
 * Custom hook for Web Speech Recognition
 * Handles voice input with proper error handling and state management
 */

import { useState, useEffect, useRef } from 'react';
import { SPEECH_LANG_MAP } from '../constants/languages';

export function useSpeechRecognition(lang) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState('');
  const recognitionRef = useRef(null);
  const hasStartedRef = useRef(false);

  useEffect(() => {
    // Check for browser support
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setError('Speech recognition not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();

    // Configure recognition
    recognitionRef.current.lang = SPEECH_LANG_MAP[lang] || 'hi-IN';
    recognitionRef.current.continuous = false;
    recognitionRef.current.interimResults = true;
    recognitionRef.current.maxAlternatives = 1;

    // Event handlers
    recognitionRef.current.onstart = () => {
      console.log('Speech recognition started');
      hasStartedRef.current = true;
      setError('');
      setIsListening(true);
    };

    recognitionRef.current.onresult = (event) => {
      const text = event.results[0][0].transcript;
      console.log('Transcribed:', text);
      setTranscript(text);
    };

    recognitionRef.current.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      let errorMsg = '';
      
      switch(event.error) {
        case 'no-speech':
          errorMsg = 'No speech detected. Please speak clearly and try again.';
          break;
        case 'audio-capture':
          errorMsg = 'No microphone found. Please check your microphone connection.';
          break;
        case 'not-allowed':
          errorMsg = 'Microphone permission denied. Click the 🔒 icon in the address bar to allow access.';
          break;
        case 'network':
          errorMsg = 'Voice input requires an internet connection. Web Speech API uses Google servers. Please check your connection or use text input instead.';
          break;
        case 'aborted':
          // Ignore aborted errors (user stopped)
          return;
        default:
          errorMsg = `Microphone error: ${event.error}`;
      }
      
      setError(errorMsg);
      setIsListening(false);
      hasStartedRef.current = false;
    };

    recognitionRef.current.onend = () => {
      console.log('Speech recognition ended');
      setIsListening(false);
      hasStartedRef.current = false;
    };

    // Cleanup
    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop();
        } catch (e) {
          // Ignore errors on cleanup
        }
      }
    };
  }, [lang]);

  const startListening = () => {
    if (recognitionRef.current && !isListening && !hasStartedRef.current) {
      setTranscript('');
      setError('');
      try {
        recognitionRef.current.start();
        console.log('Attempting to start speech recognition...');
      } catch (err) {
        console.error('Failed to start recognition:', err);
        if (err.message.includes('already started')) {
          setError('Microphone is already active. Please wait a moment and try again.');
        } else {
          setError('Failed to start microphone. Please refresh the page and try again.');
        }
        setIsListening(false);
        hasStartedRef.current = false;
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && (isListening || hasStartedRef.current)) {
      try {
        recognitionRef.current.stop();
      } catch (err) {
        console.error('Failed to stop recognition:', err);
      }
      setIsListening(false);
      hasStartedRef.current = false;
    }
  };

  const clearError = () => setError('');

  return { 
    isListening, 
    transcript, 
    error, 
    startListening, 
    stopListening,
    clearError
  };
}

export default useSpeechRecognition;
