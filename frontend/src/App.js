import React, { useState } from 'react';
import './App.css';
import Header from './components/Header';
import SearchBar from './components/SearchBar';
import ExampleQueries from './components/ExampleQueries';
import Results from './components/Results';
import Sidebar from './components/Sidebar';
import Footer from './components/Footer';
import axios from 'axios';

function App() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Check API health on mount
  React.useEffect(() => {
    checkApiHealth();
  }, []);

  React.useEffect(() => {
    if (!apiStatus) {
      window.alert('API is currently offline.');
    }
  }, [apiStatus]);

  const checkApiHealth = async () => {
    try {
      const response = await axios.get('http://localhost:8000/health', { timeout: 5000 });
      setApiStatus(response.status === 200);
    } catch (error) {
      setApiStatus(false);
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) {
      alert('Please enter a query before searching.');
      return;
    }

    setLoading(true);
    setResults(null);

    try {
      const response = await axios.post(
        'http://localhost:8000/ask',
        { query: query },
        { timeout: 30000 }
      );
      setResults(response.data);
    } catch (error) {
      console.error('Error:', error);
      setResults({
        error: true,
        answer: 'Failed to fetch results. Please ensure the API server is running.'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (exampleQuery) => {
    setQuery(exampleQuery);
  };

  return (
    <div className="app">
      <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
      
      <div className="app-container">
        <main className="main-content">
          <div className="content-wrapper">
            <SearchBar 
              query={query}
              setQuery={setQuery}
              onSearch={handleSearch}
              loading={loading}
            />
            
            <ExampleQueries onExampleClick={handleExampleClick} />
            
            <Results results={results} loading={loading} />
          </div>
        </main>

        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      </div>
      
      <Footer />
    </div>
  );
}

export default App;
