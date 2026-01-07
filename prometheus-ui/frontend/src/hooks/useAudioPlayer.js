/**
 * Custom hook for audio playback
 * Handles base64 audio conversion and playback state
 */

import { useState, useRef, useCallback } from 'react';

/**
 * Convert base64 string to Blob
 */
function base64ToBlob(base64, mimeType) {
  const byteCharacters = atob(base64);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  return new Blob([byteArray], { type: mimeType });
}

export function useAudioPlayer() {
  const [playingIndex, setPlayingIndex] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef(null);

  const playAudio = useCallback((audioBase64, messageIdx) => {
    try {
      // Stop any currently playing audio
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      
      // Create audio from base64
      const audioBlob = base64ToBlob(audioBase64, 'audio/wav');
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      
      audioRef.current = audio;
      setPlayingIndex(messageIdx);
      setIsPlaying(true);
      
      audio.onended = () => {
        setPlayingIndex(null);
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
        audioRef.current = null;
      };
      
      audio.onerror = () => {
        console.error('Audio playback error');
        setPlayingIndex(null);
        setIsPlaying(false);
        audioRef.current = null;
      };
      
      audio.play();
    } catch (error) {
      console.error('Audio playback error:', error);
      setPlayingIndex(null);
      setIsPlaying(false);
    }
  }, []);

  const stopAudio = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setPlayingIndex(null);
      setIsPlaying(false);
    }
  }, []);

  const toggleAudio = useCallback((audioBase64, messageIdx) => {
    if (playingIndex === messageIdx && isPlaying) {
      stopAudio();
    } else {
      playAudio(audioBase64, messageIdx);
    }
  }, [playingIndex, isPlaying, playAudio, stopAudio]);

  return {
    playingIndex,
    isPlaying,
    playAudio,
    stopAudio,
    toggleAudio,
  };
}

export default useAudioPlayer;
