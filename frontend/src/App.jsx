/**
 * PROMETHEUS - Main App Layout (Refactored)
 * Multilingual RAG UI with Voice Support
 * 
 * This version uses lazy loading for better performance
 * and separates concerns into reusable components.
 */

import { useState, Suspense, lazy } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './api';
import { Header, Sidebar, Footer } from './components/layout';
import { Spinner } from './components/ui';
import '@fontsource/noto-sans-devanagari';

// Lazy load pages for better initial load time
const Chat = lazy(() => import('./pages/Chat'));
const Metrics = lazy(() => import('./pages/Metrics'));

// Loading fallback component
function PageLoader() {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <Spinner size="xl" />
        <p className="mt-4 text-gray-400">Loading...</p>
      </div>
    </div>
  );
}

function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [selectedLang, setSelectedLang] = useState('hi');

  return (
    <QueryClientProvider client={queryClient}>
      <div className="h-screen w-screen overflow-hidden bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white">
        {/* Main Layout */}
        <div className="h-full flex flex-col">
          {/* Header */}
          <Header 
            selectedLang={selectedLang} 
            onLangChange={setSelectedLang} 
          />

          {/* Main Content Area */}
          <div className="flex-1 flex overflow-hidden">
            {/* Sidebar */}
            <Sidebar 
              activeTab={activeTab} 
              onTabChange={setActiveTab} 
            />

            {/* Main Content with Lazy Loading */}
            <main className="flex-1 overflow-hidden">
              <div className="h-full bg-gray-800/20 backdrop-blur">
                <Suspense fallback={<PageLoader />}>
                  {activeTab === 'chat' && <Chat lang={selectedLang} />}
                  {activeTab === 'metrics' && <Metrics />}
                </Suspense>
              </div>
            </main>
          </div>

          {/* Footer */}
          <Footer />
        </div>
      </div>
    </QueryClientProvider>
  );
}

export default App;
