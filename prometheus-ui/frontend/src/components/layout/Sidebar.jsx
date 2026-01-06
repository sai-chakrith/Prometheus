/**
 * App sidebar navigation
 */

import { MessageSquare, BarChart3, Mic } from 'lucide-react';
import { cn } from '../../utils';

export function Sidebar({ activeTab, onTabChange }) {
  return (
    <aside className="w-20 bg-gray-800/30 backdrop-blur border-r border-gray-700 flex flex-col items-center py-6 gap-4">
      <NavButton
        icon={MessageSquare}
        isActive={activeTab === 'chat'}
        onClick={() => onTabChange('chat')}
        title="Chat"
        activeGradient="from-blue-500 to-cyan-500"
        activeShadow="shadow-blue-500/50"
      />

      <NavButton
        icon={BarChart3}
        isActive={activeTab === 'metrics'}
        onClick={() => onTabChange('metrics')}
        title="Metrics"
        activeGradient="from-purple-500 to-pink-500"
        activeShadow="shadow-purple-500/50"
      />

      {/* Voice indicator */}
      <div className="mt-auto p-4 rounded-xl bg-green-500/20 border border-green-500/30">
        <Mic className="w-6 h-6 text-green-400" />
      </div>
    </aside>
  );
}

export function NavButton({ 
  icon: Icon, 
  isActive, 
  onClick, 
  title,
  activeGradient = 'from-blue-500 to-cyan-500',
  activeShadow = 'shadow-blue-500/50'
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'p-4 rounded-xl transition-all',
        isActive
          ? `bg-gradient-to-br ${activeGradient} shadow-lg ${activeShadow}`
          : 'bg-gray-700/50 hover:bg-gray-600/50'
      )}
      title={title}
    >
      <Icon className="w-6 h-6" />
    </button>
  );
}

export default Sidebar;
