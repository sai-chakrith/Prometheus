/**
 * Chat Component - Voice + Text Input with RAG Integration
 * Refactored for better code organization and lazy loading
 */

import { useState, useEffect } from 'react';
import { useRagMutation } from '../api';
import { useSpeechRecognition, useAudioPlayer } from '../hooks';
import { MessageList, ChatInput } from '../components/chat';
import { WELCOME_MESSAGES } from '../constants/languages';

export default function Chat({ lang = 'hi' }) {
  // Initialize messages with welcome message
  const [messages, setMessages] = useState([
    {
      type: 'ai',
      text: WELCOME_MESSAGES[lang] || WELCOME_MESSAGES.en,
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [typingEffect, setTypingEffect] = useState(null);
  
  // Custom hooks
  const { 
    isListening, 
    transcript, 
    error: speechError, 
    startListening, 
    stopListening 
  } = useSpeechRecognition(lang);
  
  const { 
    playingIndex, 
    playAudio, 
    stopAudio 
  } = useAudioPlayer();
  
  // API mutation
  const ragMutation = useRagMutation();

  // Update input when speech recognition provides transcript
  useEffect(() => {
    if (transcript) {
      setInput(transcript);
    }
  }, [transcript]);

  // Update welcome message when language changes
  useEffect(() => {
    setMessages(prev => {
      if (prev.length === 1 && prev[0].type === 'ai') {
        return [{
          type: 'ai',
          text: WELCOME_MESSAGES[lang] || WELCOME_MESSAGES.en,
          timestamp: new Date(),
        }];
      }
      return prev;
    });
  }, [lang]);

  const handleSend = async () => {
    if (!input.trim() || ragMutation.isPending) return;

    const userMessage = {
      type: 'user',
      text: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      const result = await ragMutation.mutateAsync({ query: input, lang });
      
      // Typing effect simulation
      await simulateTypingEffect(result.answer);
      
      // Add AI message after typing effect
      const aiMessage = {
        type: 'ai',
        text: result.answer,
        sources: result.sources,
        audioBase64: result.audio_base64,
        timestamp: new Date(),
      };

      setTypingEffect(null);
      setMessages(prev => [...prev, aiMessage]);
      
      // Auto-play audio if available
      if (result.audio_base64) {
        playAudio(result.audio_base64, messages.length);
      }
      
    } catch (error) {
      const errorMessage = {
        type: 'error',
        text: `Error: ${error.message}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const simulateTypingEffect = async (text) => {
    const words = text.split(' ');
    let currentText = '';
    
    for (let i = 0; i < words.length; i++) {
      currentText += (i > 0 ? ' ' : '') + words[i];
      setTypingEffect(currentText);
      await new Promise(resolve => setTimeout(resolve, 50));
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <MessageList
        messages={messages}
        typingEffect={typingEffect}
        isLoading={ragMutation.isPending}
        playingIndex={playingIndex}
        onPlayAudio={playAudio}
        onStopAudio={stopAudio}
      />

      {/* Input Area */}
      <ChatInput
        lang={lang}
        value={input}
        onChange={setInput}
        onSend={handleSend}
        isListening={isListening}
        onStartListening={startListening}
        onStopListening={stopListening}
        speechError={speechError}
        disabled={ragMutation.isPending}
      />
    </div>
  );
}
