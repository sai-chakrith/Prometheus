import React from 'react';
import { HiX, HiInformationCircle, HiGlobe } from 'react-icons/hi';
import './Sidebar.css';

const Sidebar = ({ isOpen, onClose }) => {
  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={onClose}></div>}
      
      <aside className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <h2 className="sidebar-title">Menu</h2>
          <button className="close-button" onClick={onClose} aria-label="Close menu">
            <HiX />
          </button>
        </div>

        <div className="sidebar-content">
          {/* About Section */}
        <div className="sidebar-section">
          <div className="section-header">
            <HiInformationCircle className="section-icon" />
            <h3>About Prometheus</h3>
          </div>
          <div className="section-content">
            <p>Prometheus brings light to startup funding intelligence, providing powerful search and analytics over Indian startup funding data using:</p>
            <ul>
              <li><strong>RAG Technology</strong> - Retrieval Augmented Generation</li>
              <li><strong>Multilingual AI</strong> - E5-Large Embeddings</li>
              <li><strong>Vector Search</strong> - FAISS-powered similarity</li>
              <li><strong>Smart Routing</strong> - Intelligent query processing</li>
            </ul>
            <p style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #e0e0e0', fontStyle: 'italic', color: '#666' }}>
              "Illuminating the path to investment intelligence"
            </p>
          </div>
        </div>          {/* Languages Section */}
          <div className="sidebar-section">
            <div className="section-header">
              <HiGlobe className="section-icon" />
              <h3>Supported Languages</h3>
            </div>
            <div className="section-content">
              <ul>
                <li>English</li>
                <li>हिंदी (Hindi)</li>
              </ul>
            </div>
          </div>

          {/* Footer */}
          <div className="sidebar-footer">
            <p className="version-info">Version 1.0.0</p>
            <p className="update-info">Last Updated: Dec 2025</p>
          </div>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
