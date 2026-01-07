import { useState, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import api from './api';

export default function ChatHistoryOptimized({ token }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedId, setExpandedId] = useState(null);
  
  // Pagination state
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  
  // Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  
  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      setPage(1); // Reset to first page on new search
    }, 500);
    return () => clearTimeout(timer);
  }, [searchQuery]);
  
  const fetchHistory = useCallback(async () => {
    if (!token) {
      setLoading(false);
      return;
    }
    
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '20'
      });
      
      if (selectedLanguage) params.append('language', selectedLanguage);
      if (debouncedSearch) params.append('search', debouncedSearch);
      
      const response = await api.get(`/api/chat-history?${params}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setHistory(response.data.history || []);
      
      if (response.data.pagination) {
        setPage(response.data.pagination.page);
        setTotalPages(response.data.pagination.total_pages);
        setTotal(response.data.pagination.total);
        setHasMore(response.data.pagination.has_more);
      }
      
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load chat history');
    } finally {
      setLoading(false);
    }
  }, [token, page, selectedLanguage, debouncedSearch]);
  
  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);
  
  const deleteChat = async (chatId, e) => {
    e.stopPropagation();
    
    if (!confirm('Delete this chat?')) return;
    
    try {
      await api.delete(`/api/chat-history/${chatId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Refresh history
      fetchHistory();
    } catch (err) {
      console.error('Error deleting chat:', err);
      alert('Failed to delete chat');
    }
  };
  
  const clearAllHistory = async () => {
    if (!confirm('Clear all chat history? This cannot be undone.')) return;
    
    try {
      await api.delete('/api/chat-history', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setHistory([]);
      setPage(1);
      setTotal(0);
    } catch (err) {
      console.error('Error clearing history:', err);
      alert('Failed to clear history');
    }
  };
  
  const exportHistory = () => {
    const exportData = history.map(chat => ({
      timestamp: chat.timestamp,
      language: chat.language,
      query: chat.query,
      response: chat.response
    }));
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-history-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };
  
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
    });
  };
  
  const getLanguageName = (code) => {
    const languages = {
      en: 'English', hi: 'हिंदी', te: 'తెలుగు', ta: 'தமிழ்',
      kn: 'ಕನ್ನಡ', mr: 'मराठी', gu: 'ગુજરાતી', bn: 'বাংলা'
    };
    return languages[code] || code;
  };
  
  const groupByDate = (chats) => {
    const groups = { Today: [], Yesterday: [], 'This Week': [], 'This Month': [], Older: [] };
    const now = new Date();
    
    chats.forEach(chat => {
      const date = new Date(chat.timestamp);
      const diffDays = Math.floor((now - date) / 86400000);
      
      if (diffDays === 0) groups.Today.push(chat);
      else if (diffDays === 1) groups.Yesterday.push(chat);
      else if (diffDays < 7) groups['This Week'].push(chat);
      else if (diffDays < 30) groups['This Month'].push(chat);
      else groups.Older.push(chat);
    });
    
    return Object.entries(groups).filter(([_, chats]) => chats.length > 0);
  };
  
  if (!token) {
    return (
      <div className="max-w-4xl mx-auto p-6 text-center">
        <p className="text-gray-600">Please login to view chat history</p>
      </div>
    );
  }
  
  if (loading && history.length === 0) {
    return (
      <div className="max-w-4xl mx-auto p-6 text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading history...</p>
      </div>
    );
  }
  
  if (error && history.length === 0) {
    return (
      <div className="max-w-4xl mx-auto p-6 text-center">
        <p className="text-red-600">{error}</p>
        <button
          onClick={fetchHistory}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }
  
  const groupedHistory = groupByDate(history);
  
  return (
    <div className="max-w-5xl mx-auto p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-800">Chat History</h2>
          <div className="flex gap-2">
            {total > 0 && (
              <>
                <button
                  onClick={exportHistory}
                  className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition"
                  title="Export as JSON"
                >
                  📥 Export
                </button>
                <button
                  onClick={clearAllHistory}
                  className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
                >
                  🗑️ Clear All
                </button>
              </>
            )}
          </div>
        </div>
        
        {/* Search and Filters */}
        <div className="flex gap-3 mb-4">
          <input
            type="text"
            placeholder="🔍 Search chats..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <select
            value={selectedLanguage}
            onChange={(e) => {
              setSelectedLanguage(e.target.value);
              setPage(1);
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Languages</option>
            <option value="en">English</option>
            <option value="hi">हिंदी</option>
            <option value="te">తెలుగు</option>
            <option value="ta">தமிழ்</option>
            <option value="kn">ಕನ್ನಡ</option>
            <option value="mr">मराठी</option>
            <option value="gu">ગુજરાતી</option>
            <option value="bn">বাংলা</option>
          </select>
        </div>
        
        {/* Results info */}
        <div className="text-sm text-gray-600 mb-2">
          {total > 0 ? (
            <>
              Showing {(page - 1) * 20 + 1}-{Math.min(page * 20, total)} of {total} chat{total !== 1 ? 's' : ''}
              {(searchQuery || selectedLanguage) && ' (filtered)'}
            </>
          ) : (
            'No chat history yet'
          )}
        </div>
      </div>
      
      {/* Chat History */}
      {groupedHistory.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg">No chats found</p>
          {(searchQuery || selectedLanguage) && (
            <button
              onClick={() => {
                setSearchQuery('');
                setSelectedLanguage('');
                setPage(1);
              }}
              className="mt-4 px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
            >
              Clear filters
            </button>
          )}
        </div>
      ) : (
        <>
          {groupedHistory.map(([dateGroup, chats]) => (
            <div key={dateGroup} className="mb-6">
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3 sticky top-0 bg-white py-2">
                {dateGroup}
              </h3>
              
              <div className="space-y-3">
                {chats.map((chat) => (
                  <div
                    key={chat.id}
                    className="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow"
                  >
                    <div
                      className="p-4 cursor-pointer"
                      onClick={() => setExpandedId(expandedId === chat.id ? null : chat.id)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
                              {getLanguageName(chat.language)}
                            </span>
                            <span className="text-xs text-gray-500">{formatTimestamp(chat.timestamp)}</span>
                          </div>
                          <p className="font-medium text-gray-800 line-clamp-1">{chat.query}</p>
                          {expandedId !== chat.id && chat.response_preview && (
                            <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                              {chat.response_preview}
                            </p>
                          )}
                        </div>
                        <div className="flex items-center gap-2 ml-4">
                          <button
                            onClick={(e) => deleteChat(chat.id, e)}
                            className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded transition"
                            title="Delete chat"
                          >
                            🗑️
                          </button>
                          <span className="text-gray-400">
                            {expandedId === chat.id ? '▲' : '▼'}
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    {expandedId === chat.id && (
                      <div className="border-t border-gray-200 p-4 bg-gray-50">
                        <div className="prose prose-sm max-w-none">
                          <ReactMarkdown>{chat.response}</ReactMarkdown>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
          
          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                ← Previous
              </button>
              
              <span className="px-4 py-2 text-gray-700">
                Page {page} of {totalPages}
              </span>
              
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={!hasMore}
                className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
