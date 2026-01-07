import React, { useState, useRef, useEffect } from 'react';
import { Moon, Sun, RotateCcw, Send, Mic, Globe, TrendingUp, DollarSign, Users, BarChart3, Sparkles, History, LogOut, LineChart, MessageSquare } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import ChatHistoryOptimized from './ChatHistoryOptimized';
import Insights from './Insights';
import Auth from './Auth';
import api from './api';
import { translations } from './translations';

export default function PrometheusApp() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [language, setLanguage] = useState('en');
  const [theme, setTheme] = useState('dark');
  const [showLanguageMenu, setShowLanguageMenu] = useState(false);
  const [activeTab, setActiveTab] = useState('chat');
  const [isLoading, setIsLoading] = useState(false);
  
  // Auth state
  const [authToken, setAuthToken] = useState(null);
  const [username, setUsername] = useState('');
  const [showAuthModal, setShowAuthModal] = useState(true);
  
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);

  const languages = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'hi', name: 'हिन्दी', flag: '🇮🇳' },
    { code: 'ta', name: 'தமிழ்', flag: '🇮🇳' },
    { code: 'te', name: 'తెలుగు', flag: '🇮🇳' },
    { code: 'kn', name: 'ಕನ್ನಡ', flag: '🇮🇳' },
    { code: 'mr', name: 'मराठी', flag: '🇮🇳' },
    { code: 'gu', name: 'ગુજરાતી', flag: '🇮🇳' },
    { code: 'bn', name: 'বাংলা', flag: '🇮🇳' }
  ];

  const suggestedQuestions = [
    { icon: TrendingUp, textKey: 'question1', color: 'from-cyan-500 to-teal-500' },
    { icon: DollarSign, textKey: 'question2', color: 'from-teal-500 to-cyan-600' },
    { icon: Users, textKey: 'question3', color: 'from-cyan-600 to-teal-600' },
    { icon: BarChart3, textKey: 'question4', color: 'from-teal-600 to-cyan-500' }
  ];

  const t = translations[language];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check for saved auth token
  useEffect(() => {
    const savedToken = localStorage.getItem('authToken');
    const savedUsername = localStorage.getItem('username');
    if (savedToken && savedUsername) {
      setAuthToken(savedToken);
      setUsername(savedUsername);
      setShowAuthModal(false);
    }
  }, []);

  useEffect(() => {
    // Speech recognition language mapping for all supported languages
    const speechLangMap = {
      en: 'en-US',
      hi: 'hi-IN',
      ta: 'ta-IN',
      te: 'te-IN',
      kn: 'kn-IN',
      mr: 'mr-IN',
      gu: 'gu-IN',
      bn: 'bn-IN'
    };

    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = speechLangMap[language] || 'en-US';

      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
        setIsRecording(false);
      };

      recognitionRef.current.onerror = () => {
        setIsRecording(false);
      };

      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };
    }
  }, [language]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await api.post('/api/rag', {
        query: input,
        lang: language
      });

      const aiResponse = { 
        role: 'assistant', 
        content: response.data.answer || response.data.response 
      };
      setMessages(prev => [...prev, aiResponse]);

      // Auto-save to history if logged in
      if (authToken) {
        try {
          await api.post('/api/save-chat', {
            query: input,
            lang: language,
            response: aiResponse.content
          }, {
            headers: { Authorization: `Bearer ${authToken}` }
          });
        } catch (err) {
          // Silently fail - chat history is not critical
        }
      }
    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: t.error
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }

    setInput('');
  };

  const handleSuggestedQuestion = (question) => {
    setInput(question);
    setTimeout(() => handleSend(), 100);
  };

  const toggleRecording = () => {
    if (!recognitionRef.current) return;

    if (isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    } else {
      recognitionRef.current.start();
      setIsRecording(true);
    }
  };

  const resetChat = () => {
    setMessages([]);
  };

  const handleLogout = () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('username');
    setAuthToken(null);
    setUsername('');
    setShowAuthModal(true);
    setMessages([]);
    setActiveTab('chat');
  };

  const handleAuthSuccess = (data) => {
    setAuthToken(data.token);
    setUsername(data.username);
    setShowAuthModal(false);
    localStorage.setItem('authToken', data.token);
    localStorage.setItem('username', data.username);
  };

  const currentLang = languages.find(l => l.code === language);

  const bgClass = theme === 'dark' 
    ? 'bg-gradient-to-br from-slate-900 via-slate-800 to-teal-950'
    : 'bg-gradient-to-br from-gray-50 via-white to-cyan-50';

  const cardBg = theme === 'dark'
    ? 'bg-slate-800/50 border-slate-700/50'
    : 'bg-white/80 border-gray-200/50';

  const textPrimary = theme === 'dark' ? 'text-white' : 'text-gray-900';
  const textSecondary = theme === 'dark' ? 'text-gray-300' : 'text-gray-600';

  // Show auth modal if not logged in
  if (showAuthModal) {
    return (
      <div className={`min-h-screen ${bgClass} flex items-center justify-center p-6`}>
        <style>{`
          .gradient-teal {
            background: linear-gradient(135deg, #077b92 0%, #0096a3 50%, #18c2dc 100%);
          }
          .text-gradient {
            background: linear-gradient(135deg, #18c2dc 0%, #4dd3e0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
          }
        `}</style>
        <Auth onAuthSuccess={handleAuthSuccess} />
      </div>
    );
  }

  // Dynamic theme classes
  const glassCard = theme === 'dark' 
    ? 'bg-white/5 backdrop-blur-xl border border-white/10' 
    : 'bg-white/80 backdrop-blur-xl border border-gray-200 shadow-lg';
  
  const textMain = theme === 'dark' ? 'text-white' : 'text-gray-900';
  const textMuted = theme === 'dark' ? 'text-gray-400' : 'text-gray-600';
  const textSubtle = theme === 'dark' ? 'text-gray-300' : 'text-gray-700';
  const inputBg = theme === 'dark' ? 'bg-transparent text-white placeholder-gray-400' : 'bg-transparent text-gray-900 placeholder-gray-500';
  const menuHover = theme === 'dark' ? 'hover:bg-cyan-500/20' : 'hover:bg-cyan-100';
  const menuActive = theme === 'dark' ? 'bg-cyan-500/30' : 'bg-cyan-200';

  return (
    <div className={`min-h-screen transition-colors duration-500 overflow-hidden ${
      theme === 'dark' 
        ? 'bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900' 
        : 'bg-gradient-to-br from-gray-50 via-white to-cyan-50'
    }`}>
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className={`absolute top-1/4 left-1/4 w-96 h-96 rounded-full blur-3xl animate-pulse ${theme === 'dark' ? 'bg-purple-500/20' : 'bg-purple-300/20'}`}></div>
        <div className={`absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full blur-3xl animate-pulse ${theme === 'dark' ? 'bg-blue-500/20' : 'bg-blue-300/20'}`} style={{animationDelay: '1s'}}></div>
        <div className={`absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full blur-3xl animate-pulse ${theme === 'dark' ? 'bg-cyan-500/10' : 'bg-cyan-300/20'}`} style={{animationDelay: '2s'}}></div>
      </div>

      <style>{`
        .gradient-teal {
          background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
        }
        .text-gradient {
          background: linear-gradient(135deg, #22d3ee 0%, #a78bfa 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .text-gradient-light {
          background: linear-gradient(135deg, #0891b2 0%, #7c3aed 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
        }
        .glow-effect {
          box-shadow: 0 0 20px rgba(34, 211, 238, 0.4);
        }
        @keyframes pulse-glow {
          0%, 100% { box-shadow: 0 0 15px rgba(34, 211, 238, 0.5); }
          50% { box-shadow: 0 0 30px rgba(34, 211, 238, 0.8); }
        }
        .recording-pulse {
          animation: pulse-glow 1.5s ease-in-out infinite;
        }
      `}</style>

      {/* Header */}
      <motion.header 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className={`${glassCard} border-b ${theme === 'dark' ? 'border-white/10' : 'border-gray-200'} px-6 py-4 sticky top-0 z-50 relative`}
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          {/* Logo and Title */}
          <motion.div 
            className="flex items-center gap-4"
            whileHover={{ scale: 1.02 }}
          >
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center shadow-lg shadow-cyan-500/50">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className={`text-2xl font-bold ${theme === 'dark' ? 'text-gradient' : 'text-gradient-light'}`}>{t.appName}</h1>
              <p className={`text-sm ${textMuted}`}>{t.appSubtitle}</p>
            </div>
          </motion.div>

          {/* Controls */}
          <div className="flex items-center gap-3">
            {/* User Info */}
            <div className={`px-4 py-2 rounded-xl ${glassCard}`}>
              <span className={`text-sm ${textMain} font-medium`}>👤 {username}</span>
            </div>

            {/* Language Selector */}
            <div className="relative">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowLanguageMenu(!showLanguageMenu)}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl ${glassCard} ${textMain} hover:border-cyan-500/50 transition-all`}
              >
                <Globe className="w-4 h-4" />
                <span className="text-lg">{currentLang.flag}</span>
                <span className="text-sm font-medium hidden sm:inline">{currentLang.name}</span>
              </motion.button>

              {showLanguageMenu && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`absolute top-full mt-2 right-0 ${glassCard} rounded-xl shadow-2xl min-w-[180px] z-50 overflow-hidden`}
                >
                  {languages.map((lang) => (
                    <button
                      key={lang.code}
                      onClick={() => {
                        setLanguage(lang.code);
                        setShowLanguageMenu(false);
                      }}
                      className={`w-full flex items-center gap-3 px-4 py-3 ${menuHover} transition-colors ${
                        lang.code === language ? menuActive : ''
                      }`}
                    >
                      <span className="text-xl">{lang.flag}</span>
                      <span className={`text-sm ${textMain}`}>{lang.name}</span>
                    </button>
                  ))}
                </motion.div>
              )}
            </div>

            {/* Reset Button */}
            <motion.button
              whileHover={{ scale: 1.1, rotate: 180 }}
              whileTap={{ scale: 0.9 }}
              onClick={resetChat}
              className={`p-2 rounded-xl ${glassCard} ${textMain} hover:border-cyan-500/50 transition-all`}
              title="Reset Chat"
            >
              <RotateCcw className="w-5 h-5" />
            </motion.button>

            {/* Theme Toggle */}
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              className={`p-2 rounded-xl ${glassCard} ${textMain} hover:border-cyan-500/50 transition-all`}
            >
              {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </motion.button>

            {/* Logout Button */}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleLogout}
              className={`px-4 py-2 rounded-xl ${glassCard} ${theme === 'dark' ? 'text-red-300' : 'text-red-600'} hover:bg-red-500/20 hover:border-red-500/50 transition-all flex items-center gap-2`}
            >
              <LogOut className="w-4 h-4" />
              {t.logout}
            </motion.button>
          </div>
        </div>
      </motion.header>

      {/* Tab Navigation */}
      <div className="max-w-7xl mx-auto px-6 pt-6 relative z-10">
        <div className={`flex gap-2 ${glassCard} rounded-xl p-2`}>
          <TabButton 
            active={activeTab === 'chat'} 
            onClick={() => setActiveTab('chat')}
            icon={MessageSquare}
            label={t.chat}
            theme={theme}
          />
          <TabButton 
            active={activeTab === 'history'} 
            onClick={() => setActiveTab('history')}
            icon={History}
            label={t.history}
            theme={theme}
          />
          <TabButton 
            active={activeTab === 'insights'} 
            onClick={() => setActiveTab('insights')}
            icon={LineChart}
            label={t.insights}
            theme={theme}
          />
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-6 py-8 relative z-10">
        {activeTab === 'chat' && (
          <>
            {messages.length === 0 ? (
              /* Welcome Screen */
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="text-center space-y-8"
              >
                <motion.h2 
                  className={`text-5xl md:text-6xl font-bold text-gradient`}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  {t.welcomeTitle}
                </motion.h2>
                
                <motion.p 
                  className={`text-xl ${textSubtle} max-w-3xl mx-auto`}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.4 }}
                >
                  {t.welcomeSubtitle}
                </motion.p>

                {/* Suggested Questions */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                  className="space-y-6 mt-12"
                >
                  <h3 className={`text-lg font-semibold ${textMuted}`}>{t.suggestedQuestions}</h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {suggestedQuestions.map((q, idx) => (
                      <motion.button
                        key={idx}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.7 + idx * 0.1 }}
                        whileHover={{ scale: 1.02, y: -2 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => handleSuggestedQuestion(t[q.textKey])}
                        className={`${glassCard} rounded-xl p-6 text-left hover:border-cyan-500/50 transition-all group`}
                      >
                        <div className="flex items-start gap-4">
                          <div className={`p-3 rounded-xl bg-gradient-to-br ${q.color} group-hover:scale-110 transition-transform shadow-lg`}>
                            <q.icon className="w-6 h-6 text-white" />
                          </div>
                          <p className={`text-base ${textMain} flex-1`}>{t[q.textKey]}</p>
                        </div>
                      </motion.button>
                    ))}
                  </div>
                </motion.div>
              </motion.div>
            ) : (
              /* Chat Messages */
              <div className="space-y-6 mb-32">
                <AnimatePresence>
                  {messages.map((msg, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-3xl px-6 py-4 rounded-2xl ${
                          msg.role === 'user'
                            ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/50'
                            : `${glassCard} ${textMain}`
                        } shadow-lg`}
                      >
                        {msg.role === 'assistant' && (
                          <div className="flex items-center gap-2 mb-2">
                            <div className="w-6 h-6 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center shadow-lg shadow-cyan-500/50">
                              <Sparkles className="w-3 h-3 text-white" />
                            </div>
                            <span className="text-sm font-semibold text-cyan-400">Prometheus</span>
                          </div>
                        )}
                        <div className="prose prose-sm max-w-none dark:prose-invert">
                          <ReactMarkdown
                            components={{
                              p: ({children}) => <p className="mb-2 leading-relaxed">{children}</p>,
                              strong: ({children}) => <strong className="font-bold text-cyan-600 dark:text-cyan-400">{children}</strong>,
                              ul: ({children}) => <ul className="list-disc list-inside space-y-1">{children}</ul>,
                              ol: ({children}) => <ol className="list-decimal list-inside space-y-1">{children}</ol>,
                            }}
                          >
                            {msg.content}
                          </ReactMarkdown>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
                {isLoading && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex justify-start"
                  >
                    <div className={`${glassCard} px-6 py-4 rounded-2xl`}>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                        <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                      </div>
                    </div>
                  </motion.div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </>
        )}

        {activeTab === 'history' && (
          <ChatHistoryOptimized token={authToken} />
        )}

        {activeTab === 'insights' && (
          <Insights theme={theme} />
        )}
      </main>

      {/* Input Area - Only show on chat tab */}
      {activeTab === 'chat' && (
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3 }}
          className={`fixed bottom-0 left-0 right-0 p-6 backdrop-blur-sm z-50 ${theme === 'dark' ? 'bg-gradient-to-t from-slate-900/95 to-transparent' : 'bg-gradient-to-t from-white/95 to-transparent'}`}
        >
          <div className="max-w-4xl mx-auto">
            <div className={`${glassCard} rounded-2xl shadow-2xl overflow-hidden`}>
              <div className="flex items-center gap-3 p-4">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSend()}
                  placeholder={t.placeholder}
                  className={`flex-1 bg-transparent outline-none text-base ${inputBg}`}
                  disabled={isLoading}
                />
                
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={toggleRecording}
                  className={`p-3 rounded-xl ${isRecording ? 'bg-red-500 recording-pulse shadow-lg shadow-red-500/50' : `${glassCard} ${theme === 'dark' ? 'hover:bg-white/10' : 'hover:bg-gray-100'}`} transition-all`}
                  disabled={isLoading}
                >
                  <Mic className={`w-5 h-5 ${isRecording ? 'text-white' : textMuted}`} />
                </motion.button>

                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  className={`p-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 ${
                    !input.trim() || isLoading ? 'opacity-50 cursor-not-allowed' : 'glow-effect shadow-lg shadow-cyan-500/50'
                  } transition-all`}
                >
                  <Send className="w-5 h-5 text-white" />
                </motion.button>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}

// Tab Button Component
function TabButton({ active, onClick, icon: Icon, label, theme }) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`flex items-center gap-2 px-6 py-3 rounded-xl transition-all ${
        active 
          ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/50' 
          : `bg-transparent ${theme === 'dark' ? 'text-gray-400 hover:bg-white/5' : 'text-gray-600 hover:bg-gray-100'}`
      }`}
    >
      <Icon className="w-4 h-4" />
      <span className="font-medium">{label}</span>
    </motion.button>
  );
}
