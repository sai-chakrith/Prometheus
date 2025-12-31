import React, { useState } from 'react';
import './Results.css';

const Results = ({ results, loading }) => {
  const [showDetails, setShowDetails] = useState(false);

  if (loading) {
    return (
      <div className="results-section">
        <div className="loading-container">
          <div className="spinner"></div>
          <p className="loading-text">Processing your query...</p>
        </div>
      </div>
    );
  }

  if (!results) {
    return null;
  }

  return (
    <div className="results-section">
      <h2 className="results-title">Results</h2>
      
      <div className="results-container">
        {results.error ? (
          <div className="error-message">
            <p>{results.answer}</p>
          </div>
        ) : (
          <>
            <div className="answer-content">
              <pre className="answer-text">{results.answer}</pre>
            </div>
            
            {(results.intent || results.filters || results.sources) && (
              <div className="details-section">
                <button 
                  className="details-toggle"
                  onClick={() => setShowDetails(!showDetails)}
                >
                  {showDetails ? 'Hide' : 'Show'} Query Details
                </button>
                
                {showDetails && (
                  <div className="details-content">
                    <div className="details-grid">
                      {results.intent && (
                        <div className="detail-item">
                          <strong>Intent:</strong> {results.intent}
                        </div>
                      )}
                      
                      {results.timestamp && (
                        <div className="detail-item">
                          <strong>Timestamp:</strong> {new Date(results.timestamp).toLocaleString()}
                        </div>
                      )}
                    </div>
                    
                    {results.filters && Object.keys(results.filters).length > 0 && (
                      <div className="filters-section">
                        <strong>Filters Applied:</strong>
                        <ul className="filters-list">
                          {Object.entries(results.filters).map(([key, value]) => (
                            <li key={key}>{key}: {value}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    
                    {results.sources && results.sources.length > 0 && (
                      <div className="sources-section">
                        <strong>Sources:</strong>
                        <ul className="sources-list">
                          {results.sources.map((source, index) => (
                            <li key={index}>{source}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Results;
