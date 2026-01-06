/**
 * Chat input area with voice and text support
 */

import { useState } from 'react';
import { Mic, MicOff, Send, AlertCircle } from 'lucide-react';
import { cn } from '../../utils';
import { Button } from '../ui/Button';
import { Alert } from '../ui/Alert';
import { INPUT_PLACEHOLDERS } from '../../constants/languages';

export function ChatInput({
  lang = 'en',
  value,
  onChange,
  onSend,
  isListening,
  onStartListening,
  onStopListening,
  speechError,
  disabled = false,
}) {
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  const placeholder = INPUT_PLACEHOLDERS[lang] || INPUT_PLACEHOLDERS.en;

  return (
    <div className="p-4 bg-gray-800/50 backdrop-blur border-t border-gray-700">
      {/* Speech Error Alert */}
      {speechError && (
        <SpeechErrorAlert error={speechError} />
      )}
      
      {/* Listening Indicator */}
      {isListening && !speechError && (
        <ListeningIndicator />
      )}
      
      <div className="flex gap-3 items-end max-w-4xl mx-auto">
        {/* Voice Button */}
        <VoiceButton
          isListening={isListening}
          onStartListening={onStartListening}
          onStopListening={onStopListening}
        />

        {/* Text Input */}
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          className="flex-1 bg-gray-700/50 backdrop-blur border border-gray-600 rounded-xl px-4 py-3 text-white placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={2}
          disabled={disabled}
        />

        {/* Send Button */}
        <Button
          onClick={onSend}
          disabled={!value.trim() || disabled}
          variant="primary"
          title="Send message"
        >
          <Send className="w-6 h-6" />
        </Button>
      </div>
      
      {isListening && (
        <p className="text-center text-sm text-purple-400 mt-2 animate-pulse">
          🎤 Listening...
        </p>
      )}
    </div>
  );
}

export function VoiceButton({ isListening, onStartListening, onStopListening }) {
  return (
    <button
      onClick={isListening ? onStopListening : onStartListening}
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
  );
}

export function ListeningIndicator() {
  return (
    <div className="mb-3 p-3 bg-green-500/20 border border-green-500 rounded-lg text-green-200 text-sm flex items-center gap-2">
      <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
      <p>🎤 Listening... Speak now!</p>
    </div>
  );
}

export function SpeechErrorAlert({ error }) {
  return (
    <Alert type="error" title="Microphone Error" className="mb-3">
      <p>{error}</p>
      <p className="mt-1 text-xs">
        • Make sure you're using Chrome or Edge browser<br />
        • Click the 🔒 icon in the address bar to allow microphone access<br />
        • Speak clearly when the mic is active (red pulsing button)
      </p>
    </Alert>
  );
}

export default ChatInput;
