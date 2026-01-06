/**
 * Reusable Button component with variants
 */

import { cn } from '../../utils';

export function Button({ 
  children, 
  variant = 'primary', 
  size = 'md',
  disabled = false,
  loading = false,
  className = '',
  ...props 
}) {
  const baseStyles = 'rounded-xl font-semibold transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2';
  
  const variants = {
    primary: 'bg-gradient-to-br from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600 text-white',
    secondary: 'bg-gray-700/50 hover:bg-gray-600/50 text-white',
    success: 'bg-gradient-to-br from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white',
    danger: 'bg-red-500 hover:bg-red-600 text-white',
    purple: 'bg-gradient-to-br from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white',
    ghost: 'bg-transparent hover:bg-gray-700/50 text-white',
  };
  
  const sizes = {
    sm: 'p-2 text-sm',
    md: 'p-4 text-base',
    lg: 'px-6 py-4 text-lg',
  };

  return (
    <button
      className={cn(
        baseStyles,
        variants[variant],
        sizes[size],
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {children}
    </button>
  );
}

export default Button;
