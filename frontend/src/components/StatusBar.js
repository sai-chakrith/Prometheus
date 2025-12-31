import React from 'react';
import './StatusBar.css';

const StatusBar = ({ apiStatus }) => {
  return (
    <div className="status-bar">
      <div className={`status-indicator ${apiStatus ? 'status-success' : 'status-error'}`}>
        <span className="status-dot"></span>
        <span className="status-text">
          {apiStatus ? 'API Connected' : 'API Offline'}
        </span>
      </div>
    </div>
  );
};

export default StatusBar;
