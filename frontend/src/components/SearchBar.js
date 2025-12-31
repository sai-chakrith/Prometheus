import React from 'react';
import { HiMicrophone, HiSearch } from 'react-icons/hi';
import './SearchBar.css';

const SearchBar = ({ query, setQuery, onSearch, loading }) => {
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSearch();
    }
  };

  const handleVoiceInput = () => {
    alert('Voice input feature coming soon! For now, please type your query or use the example queries.');
  };

  return (
    <div className="search-section">
      <h2 className="section-title">Ask Your Question</h2>
      
      <div className="search-container">
        <div className="search-input-wrapper">
          <textarea
            className="search-input"
            placeholder="Example: कर्नाटक में फिनटेक स्टार्टअप की कुल फंडिंग कितनी है?&#10;or&#10;What is the total funding for fintech startups in Karnataka?"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            rows={4}
          />
          
          <button 
            className="voice-button"
            onClick={handleVoiceInput}
            title="Voice input"
          >
            <HiMicrophone />
          </button>
        </div>
        
        <button 
          className="search-button"
          onClick={onSearch}
          disabled={loading}
        >
          <HiSearch />
          <span>{loading ? 'Processing...' : 'Search'}</span>
        </button>
      </div>
    </div>
  );
};

export default SearchBar;
