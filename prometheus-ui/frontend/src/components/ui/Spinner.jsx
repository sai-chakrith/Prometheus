/**
 * Loading spinner component
 */

import { Loader2 } from 'lucide-react';
import { cn } from '../../utils';

export function Spinner({ size = 'md', className = '' }) {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12',
  };
  
  return (
    <Loader2 className={cn(
      'animate-spin text-green-400',
      sizes[size],
      className
    )} />
  );
}

export function LoadingDots({ className = '' }) {
  return (
    <div className={cn('flex items-center gap-1', className)}>
      <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '0ms' }} />
      <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '150ms' }} />
      <div className="w-2 h-2 rounded-full bg-gray-400 animate-bounce" style={{ animationDelay: '300ms' }} />
    </div>
  );
}

export default Spinner;
