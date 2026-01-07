/**
 * Chat messages list component
 */

import { useRef, useEffect } from 'react';
import { MessageBubble, TypingIndicator, LoadingIndicator } from './MessageBubble';

export function MessageList({
  messages,
  typingEffect,
  isLoading,
  playingIndex,
  onPlayAudio,
  onStopAudio,
}) {
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, typingEffect]);

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-4">
      {messages.map((msg, idx) => (
        <MessageBubble
          key={idx}
          message={msg}
          index={idx}
          isPlaying={playingIndex === idx}
          onPlayAudio={onPlayAudio}
          onStopAudio={onStopAudio}
        />
      ))}
      
      {/* Typing indicator */}
      {typingEffect && <TypingIndicator text={typingEffect} />}
      
      {/* Loading indicator */}
      {isLoading && !typingEffect && <LoadingIndicator />}
      
      {/* Scroll anchor */}
      <div ref={messagesEndRef} />
    </div>
  );
}

export default MessageList;
