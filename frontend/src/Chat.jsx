/**
 * Chat Component - Voice + Text Input with RAG Integration
 */

import { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Send, Loader2, AlertCircle } from 'lucide-react';
import { useRagMutation } from './api';
import { cn } from './utils';

const useSpeechRecognition = (lang) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState('');
  const recognitionRef = useRef(null);
  const hasStartedRef = useRef(false);

  useEffect(() => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setError('Speech recognition not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();
    
    const langMap = {
      hi: 'hi-IN',
      mr: 'mr-IN',
      gu: 'gu-IN',
      en: 'en-US',
    };

    recognitionRef.current.lang = langMap[lang] || 'hi-IN';
    recognitionRef.current.continuous = false;
    recognitionRef.current.interimResults = true;
    recognitionRef.current.maxAlternatives = 1;

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

  return { isListening, transcript, error, startListening, stopListening };
};

export default function Chat({ lang = 'hi' }) {
  const [messages, setMessages] = useState([
    {
      type: 'ai',
      text: lang === 'hi' 
        ? '🎤 नमस्ते! स्टार्टअप फंडिंग के बारे में पूछें या माइक बटन दबाएं।'
        : '🎤 Hello! Ask about startup funding or press the mic button!',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [typingEffect, setTypingEffect] = useState(null);
  
  const { isListening, transcript, error: speechError, startListening, stopListening } = useSpeechRecognition(lang);
  const ragMutation = useRagMutation();
  const messagesEndRef = useRef(null);

  // Update input when speech recognition provides transcript
  useEffect(() => {
    if (transcript) {
      setInput(transcript);
    }
  }, [transcript]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, typingEffect]);

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
      
      // Typing effect
      const aiMessage = {
        type: 'ai',
        text: result.answer,
        sources: result.sources,
        audioBase64: result.audio_base64,  // Store audio data
        timestamp: new Date(),
      };

      // Simulate typing effect
      let currentText = '';
      const words = result.answer.split(' ');
      
      for (let i = 0; i < words.length; i++) {
        currentText += (i > 0 ? ' ' : '') + words[i];
        setTypingEffect(currentText);
        await new Promise(resolve => setTimeout(resolve, 50));
      }
      
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

  const playAudio = (audioBase64, messageIdx) => {
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
      setPlayingAudio(messageIdx);
      
      audio.onended = () => {
        setPlayingAudio(null);
        URL.revokeObjectURL(audioUrl);
        audioRef.current = null;
      };
      
      audio.play();
    } catch (error) {
      console.error('Audio playback error:', error);
      setPlayingAudio(null);
    }
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      setPlayingAudio(null);
    }
  };

  const base64ToBlob = (base64, mimeType) => {
    const byteCharacters = atob(base64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mimeType });
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={cn(
              'flex',
              msg.type === 'user' ? 'justify-end' : 'justify-start'
            )}
          >
            <div
              className={cn(
                'max-w-[80%] rounded-2xl px-5 py-3 shadow-lg',
                msg.type === 'user' && 'bg-gradient-to-br from-blue-500 to-blue-600 text-white',
                msg.type === 'ai' && 'bg-gradient-to-br from-green-500 to-emerald-600 text-white',
                msg.type === 'error' && 'bg-red-500/20 border border-red-500 text-red-200'
              )}
            >
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.text}</p>
              {msg.sources && (
                <div className="mt-2 pt-2 border-t border-white/20 text-xs opacity-80">
                  <p className="font-semibold">Top Sources:</p>
                  {msg.sources.slice(0, 5).map((src, i) => (
                    <p key={i} className="mt-1">
                      {i + 1}. {src.company} - {src.amount} - {src.city} [Row {src.row}]
                    </p>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        
        {/* Typing indicator */}
        {typingEffect && (
          <div className="flex justify-start">
            <div className="max-w-[80%] rounded-2xl px-5 py-3 bg-gradient-to-br from-green-500 to-emerald-600 text-white shadow-lg">
              <p className="text-sm leading-relaxed">{typingEffect}</p>
            </div>
          </div>
        )}
        
        {/* Loading indicator */}
        {ragMutation.isPending && !typingEffect && (
          <div className="flex justify-start">
            <div className="rounded-2xl px-5 py-3 bg-gray-700/50 backdrop-blur">
              <Loader2 className="w-5 h-5 animate-spin text-green-400" />
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-gray-800/50 backdrop-blur border-t border-gray-700">
        {/* Speech Error Alert */}
        {speechError && (
          <div className="mb-3 p-3 bg-red-500/20 border border-red-500 rounded-lg text-red-200 text-sm flex items-start gap-2">
            <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Microphone Error</p>
              <p>{speechError}</p>
              <p className="mt-1 text-xs">
                • Make sure you're using Chrome or Edge browser<br />
                • Click the 🔒 icon in the address bar to allow microphone access<br />
                • Speak clearly when the mic is active (red pulsing button)
              </p>
            </div>
          </div>
        )}
        
        {/* Listening Indicator */}
        {isListening && !speechError && (
          <div className="mb-3 p-3 bg-green-500/20 border border-green-500 rounded-lg text-green-200 text-sm flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
            <p>🎤 Listening... Speak now!</p>
          </div>
        )}
        
        <div className="flex gap-3 items-end max-w-4xl mx-auto">
          {/* Voice Button */}
          <button
            onClick={isListening ? stopListening : startListening}
            className={cn(
              'p-4 rounded-xl transition-all duration-300 flex-shrink-0',
              isListening 
                ? 'bg-red-500 hover:bg-red-600 animate-pulse shadow-lg shadow-red-500/50' 
                : 'bg-gradient-to-br from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 shadow-lg'
            )}
            title={isListening ? 'Stop recording' : 'Start voice input'}
          >
            {isListening ? (
              <MicOff className="w-6 h-6 text-white" />
            ) : (
              <Mic className="w-6 h-6 text-white" />
            )}
          </button>

          {/* Text Input */}
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={lang === 'hi' ? 'अपना सवाल लिखें...' : 'Type your query...'}
            className="flex-1 bg-gray-700/50 backdrop-blur border border-gray-600 rounded-xl px-4 py-3 text-white placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={2}
            disabled={ragMutation.isPending}
          />

          {/* Send Button */}
          <button
            onClick={handleSend}
            disabled={!input.trim() || ragMutation.isPending}
            className="p-4 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg flex-shrink-0"
            title="Send message"
          >
            <Send className="w-6 h-6 text-white" />
          </button>
        </div>
        
        {isListening && (
          <p className="text-center text-sm text-purple-400 mt-2 animate-pulse">
            🎤 Listening...
          </p>
        )}
      </div>
    </div>
  );
}
