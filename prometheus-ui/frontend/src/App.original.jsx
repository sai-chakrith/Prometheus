/**
 * PROMETHEUS - Main App Layout
 * Multilingual RAG UI with Voice Support
 */

import { useState } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { MessageSquare, BarChart3, Flame, Globe, Mic } from 'lucide-react';
import Chat from './Chat';
import Metrics from './Metrics';
import { queryClient } from './api';
import { cn } from './utils';
import '@fontsource/noto-sans-devanagari';

const LANGUAGES = [
  { code: 'hi', name: 'हिन्दी', flag: '🇮🇳' },
  { code: 'mr', name: 'मराठी', flag: '🇮🇳' },
  { code: 'gu', name: 'ગુજરાતી', flag: '🇮🇳' },
  { code: 'en', name: 'English', flag: '🇺🇸' },
];

function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [selectedLang, setSelectedLang] = useState('hi');

  return (
    <QueryClientProvider client={queryClient}>
      <div className="h-screen w-screen overflow-hidden bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
        {/* Main Layout */}
        <div className="h-full flex flex-col">
          {/* Header */}
          <header className="bg-gray-800/50 backdrop-blur border-b border-gray-700 px-6 py-4">
            <div className="flex items-center justify-between">
              {/* Logo */}
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-br from-orange-500 to-red-500 rounded-lg">
                  <Flame className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold bg-gradient-to-r from-orange-400 to-red-400 bg-clip-text text-transparent">
                    PROMETHEUS
                  </h1>
                  <p className="text-xs text-gray-400">Multilingual Startup Funding RAG</p>
                </div>
              </div>

              {/* Language Selector */}
              <div className="flex items-center gap-3">
                <Globe className="w-5 h-5 text-gray-400" />
                <select
                  value={selectedLang}
                  onChange={(e) => setSelectedLang(e.target.value)}
                  className="bg-gray-700/50 border border-gray-600 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {LANGUAGES.map((lang) => (
                    <option key={lang.code} value={lang.code}>
                      {lang.flag} {lang.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </header>

          {/* Main Content Area */}
          <div className="flex-1 flex overflow-hidden">
            {/* Sidebar */}
            <aside className="w-20 bg-gray-800/30 backdrop-blur border-r border-gray-700 flex flex-col items-center py-6 gap-4">
              <button
                onClick={() => setActiveTab('chat')}
                className={cn(
                  'p-4 rounded-xl transition-all',
                  activeTab === 'chat'
                    ? 'bg-gradient-to-br from-blue-500 to-cyan-500 shadow-lg shadow-blue-500/50'
                    : 'bg-gray-700/50 hover:bg-gray-600/50'
                )}
                title="Chat"
              >
                <MessageSquare className="w-6 h-6" />
              </button>

              <button
                onClick={() => setActiveTab('metrics')}
                className={cn(
                  'p-4 rounded-xl transition-all',
                  activeTab === 'metrics'
                    ? 'bg-gradient-to-br from-purple-500 to-pink-500 shadow-lg shadow-purple-500/50'
                    : 'bg-gray-700/50 hover:bg-gray-600/50'
                )}
                title="Metrics"
              >
                <BarChart3 className="w-6 h-6" />
              </button>

              <div className="mt-auto p-4 rounded-xl bg-green-500/20 border border-green-500/30">
                <Mic className="w-6 h-6 text-green-400" />
              </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-hidden">
              <div className="h-full bg-gray-800/20 backdrop-blur">
                {activeTab === 'chat' && <Chat lang={selectedLang} />}
                {activeTab === 'metrics' && <Metrics />}
              </div>
            </main>
          </div>

          {/* Footer */}
          <footer className="bg-gray-800/50 backdrop-blur border-t border-gray-700 px-6 py-3">
            <div className="flex items-center justify-between text-xs text-gray-400">
              <p>5-Day Hackathon MVP • Voice-Enabled Multilingual RAG</p>
              <p className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                Backend: 127.0.0.1:8000
              </p>
            </div>
          </footer>
        </div>
      </div>
    </QueryClientProvider>
  );
}

export default App;
