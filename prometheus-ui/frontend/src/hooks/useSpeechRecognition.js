/**
 * Custom hook for Web Speech Recognition
 * Handles voice input with proper error handling and state management
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { SPEECH_LANG_MAP } from '../constants/languages';

export function useSpeechRecognition(lang) {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState('');
  const recognitionRef = useRef(null);
  const shouldRestartRef = useRef(false);  // Track if we should auto-restart
  const manualStopRef = useRef(false);      // Track if user manually stopped
  const restartTimeoutRef = useRef(null);   // Track restart timeout
  const langRef = useRef(lang);             // Track current language

  // Update lang ref when prop changes
  useEffect(() => {
    langRef.current = lang;
    // Update recognition language if it exists
    if (recognitionRef.current) {
      recognitionRef.current.lang = SPEECH_LANG_MAP[lang] || 'hi-IN';
    }
  }, [lang]);

  // Initialize speech recognition once on mount
  useEffect(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setError('Speech recognition not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    // Configure recognition
    recognition.lang = SPEECH_LANG_MAP[langRef.current] || 'hi-IN';
    recognition.continuous = true;         // Keep listening
    recognition.interimResults = true;      // Show partial results
    recognition.maxAlternatives = 1;

    // Event handlers
    recognition.onstart = () => {
      console.log('Speech recognition started');
      setError('');
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      let finalTranscript = '';
      let interimTranscript = '';
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalTranscript += result[0].transcript;
        } else {
          interimTranscript += result[0].transcript;
        }
      }
      
      // Use final transcript if available, otherwise interim
      const text = finalTranscript || interimTranscript;
      if (text) {
        console.log('Transcribed:', text, finalTranscript ? '(final)' : '(interim)');
        setTranscript(text);
      }
    };

    // Helper function to safely restart recognition
    const safeRestart = () => {
      // Clear any pending restart
      if (restartTimeoutRef.current) {
        clearTimeout(restartTimeoutRef.current);
      }
      
      // Only restart if we should and user didn't manually stop
      if (shouldRestartRef.current && !manualStopRef.current) {
        restartTimeoutRef.current = setTimeout(() => {
          if (shouldRestartRef.current && !manualStopRef.current) {
            try {
              console.log('Auto-restarting speech recognition...');
              recognition.start();
            } catch (e) {
              console.log('Restart failed:', e.message);
              // If already started error, we're good
              if (!e.message?.includes('already started')) {
                setIsListening(false);
                shouldRestartRef.current = false;
              }
            }
          }
        }, 300);  // Slightly longer delay for stability
      }
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      
      switch(event.error) {
        case 'no-speech':
          // Don't show error for no-speech, just restart if still listening
          console.log('No speech detected, will auto-restart if listening');
          safeRestart();
          return;  // Don't set error for no-speech
          
        case 'aborted':
          // User or system aborted - restart if we should still be listening
          console.log('Recognition aborted, checking if should restart');
          safeRestart();
          return;
          
        case 'audio-capture':
          setError('No microphone found. Please check your microphone connection.');
          break;
          
        case 'not-allowed':
          setError('Microphone permission denied. Click the 🔒 icon in the address bar to allow access.');
          break;
          
        case 'network':
          setError('Voice input requires an internet connection. Web Speech API uses Google servers.');
          break;
          
        default:
          setError(`Microphone error: ${event.error}`);
      }
      
      // For real errors, stop listening
      setIsListening(false);
      shouldRestartRef.current = false;
    };

    recognition.onend = () => {
      console.log('Speech recognition ended, shouldRestart:', shouldRestartRef.current, 'manualStop:', manualStopRef.current);
      
      // Auto-restart if user didn't manually stop
      if (shouldRestartRef.current && !manualStopRef.current) {
        safeRestart();
      } else {
        setIsListening(false);
        shouldRestartRef.current = false;
      }
    };

    recognitionRef.current = recognition;

    // Cleanup on unmount
    return () => {
      manualStopRef.current = true;
      shouldRestartRef.current = false;
      if (restartTimeoutRef.current) {
        clearTimeout(restartTimeoutRef.current);
      }
      try {
        recognition.stop();
      } catch (e) {
        // Ignore errors on cleanup
      }
    };
  }, []);  // Empty deps - initialize once

  const startListening = useCallback(() => {
    if (!recognitionRef.current) {
      setError('Speech recognition not available. Please use Chrome or Edge browser.');
      return;
    }
    
    // Don't start if already listening
    if (isListening) {
      console.log('Already listening, skipping start');
      return;
    }
    
    // Clear any pending restart timeouts
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current);
    }
    
    setTranscript('');
    setError('');
    manualStopRef.current = false;
    shouldRestartRef.current = true;
    
    // Update language before starting
    recognitionRef.current.lang = SPEECH_LANG_MAP[langRef.current] || 'hi-IN';
    
    try {
      recognitionRef.current.start();
      console.log('Starting speech recognition with lang:', recognitionRef.current.lang);
    } catch (err) {
      console.error('Failed to start recognition:', err);
      if (err.message && err.message.includes('already started')) {
        // Already running, just ensure state is correct
        setIsListening(true);
      } else {
        setError('Failed to start microphone. Please refresh the page and try again.');
        setIsListening(false);
        shouldRestartRef.current = false;
      }
    }
  }, [isListening]);

  const stopListening = useCallback(() => {
    console.log('Manually stopping speech recognition');
    manualStopRef.current = true;
    shouldRestartRef.current = false;
    
    // Clear any pending restart timeouts
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current);
      restartTimeoutRef.current = null;
    }
    
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (err) {
        console.error('Failed to stop recognition:', err);
      }
    }
    setIsListening(false);
  }, []);

  const clearError = useCallback(() => setError(''), []);

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
