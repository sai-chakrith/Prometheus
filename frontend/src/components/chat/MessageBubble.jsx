/**
 * Chat message bubble component
 */

import { Volume2, VolumeX, Play, Pause } from 'lucide-react';
import { cn } from '../../utils';
import { Button } from '../ui/Button';

export function MessageBubble({ 
  message, 
  index,
  isPlaying = false,
  onPlayAudio,
  onStopAudio 
}) {
  const { type, text, sources, audioBase64, timestamp } = message;
  
  const bubbleStyles = {
    user: 'bg-gradient-to-br from-blue-500 to-blue-600 text-white',
    ai: 'bg-gradient-to-br from-green-500 to-emerald-600 text-white',
    error: 'bg-red-500/20 border border-red-500 text-red-200',
  };
  
  const alignment = type === 'user' ? 'justify-end' : 'justify-start';
  
  return (
    <div className={cn('flex', alignment)}>
      <div className={cn(
        'max-w-[80%] rounded-2xl px-5 py-3 shadow-lg',
        bubbleStyles[type] || bubbleStyles.ai
      )}>
        {/* Message text */}
        <p className="text-sm leading-relaxed whitespace-pre-wrap">{text}</p>
        
        {/* Audio control */}
        {audioBase64 && type === 'ai' && (
          <button
            onClick={() => isPlaying ? onStopAudio() : onPlayAudio(audioBase64, index)}
            className="mt-2 flex items-center gap-1 text-xs opacity-80 hover:opacity-100 transition-opacity"
          >
            {isPlaying ? (
              <>
                <Pause className="w-4 h-4" />
                <span>Pause</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Play Audio</span>
              </>
            )}
          </button>
        )}
        
        {/* Sources */}
        {sources && sources.length > 0 && (
          <MessageSources sources={sources} />
        )}
        
        {/* Timestamp */}
        {timestamp && (
          <p className="mt-2 text-xs opacity-60">
            {new Date(timestamp).toLocaleTimeString()}
          </p>
        )}
      </div>
    </div>
  );
}

export function MessageSources({ sources, maxSources = 5 }) {
  if (!sources || sources.length === 0) return null;
  
  return (
    <div className="mt-2 pt-2 border-t border-white/20 text-xs opacity-80">
      <p className="font-semibold mb-1">Top Sources:</p>
      {sources.slice(0, maxSources).map((src, i) => (
        <p key={i} className="mt-1">
          {i + 1}. {src.company} - {src.amount} - {src.city} 
          {src.row && <span className="opacity-60"> [Row {src.row}]</span>}
        </p>
      ))}
    </div>
  );
}

export function TypingIndicator({ text }) {
  return (
    <div className="flex justify-start">
      <div className="max-w-[80%] rounded-2xl px-5 py-3 bg-gradient-to-br from-green-500 to-emerald-600 text-white shadow-lg">
        <p className="text-sm leading-relaxed">{text}</p>
        <span className="inline-block w-1 h-4 bg-white/70 animate-pulse ml-1" />
      </div>
    </div>
  );
}

export function LoadingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="rounded-2xl px-5 py-3 bg-gray-700/50 backdrop-blur">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-bounce" style={{ animationDelay: '0ms' }} />
          <div className="w-2 h-2 rounded-full bg-green-400 animate-bounce" style={{ animationDelay: '150ms' }} />
          <div className="w-2 h-2 rounded-full bg-green-400 animate-bounce" style={{ animationDelay: '300ms' }} />
        </div>
      </div>
    </div>
  );
}

export default MessageBubble;
