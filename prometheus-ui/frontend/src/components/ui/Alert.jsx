/**
 * Alert component for displaying messages
 */

import { AlertCircle, CheckCircle, Info, XCircle } from 'lucide-react';
import { cn } from '../../utils';

const alertIcons = {
  error: AlertCircle,
  success: CheckCircle,
  warning: AlertCircle,
  info: Info,
};

const alertStyles = {
  error: 'bg-red-500/20 border-red-500 text-red-200',
  success: 'bg-green-500/20 border-green-500 text-green-200',
  warning: 'bg-yellow-500/20 border-yellow-500 text-yellow-200',
  info: 'bg-blue-500/20 border-blue-500 text-blue-200',
};

export function Alert({ 
  type = 'info', 
  title, 
  message, 
  children,
  className = '',
  onDismiss 
}) {
  const Icon = alertIcons[type];
  
  return (
    <div className={cn(
      'p-3 border rounded-lg text-sm flex items-start gap-2',
      alertStyles[type],
      className
    )}>
      <Icon className="w-5 h-5 flex-shrink-0 mt-0.5" />
      <div className="flex-1">
        {title && <p className="font-semibold">{title}</p>}
        {message && <p>{message}</p>}
        {children}
      </div>
      {onDismiss && (
        <button 
          onClick={onDismiss} 
          className="p-1 hover:bg-white/10 rounded"
          aria-label="Dismiss"
        >
          <XCircle className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}

export default Alert;
