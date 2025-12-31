import React from 'react';
import './Footer.css';

function Footer() {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-section">
          <h3 className="footer-logo">PROMETHEUS</h3>
          <p className="footer-tagline">Illuminating Investment Intelligence</p>
        </div>
        
        <div className="footer-section">
          <h4>About</h4>
          <p className="footer-description">
            Advanced RAG-powered analytics platform for Indian startup funding insights.
          </p>
        </div>
        
        <div className="footer-section">
          <h4>Data Coverage</h4>
          <p className="footer-info">2015 - 2021</p>
          <p className="footer-info">5,302+ Funding Records</p>
        </div>
        
        <div className="footer-section">
          <h4>Technology</h4>
          <p className="footer-info">FastAPI • React</p>
          <p className="footer-info">FAISS Vector Search</p>
        </div>
      </div>
      
      <div className="footer-divider"></div>
      
      <div className="footer-bottom">
        <p className="copyright">
          © {currentYear} PROMETHEUS. All rights reserved.
        </p>
        <p className="footer-credits">
          Built with precision for data-driven insights
        </p>
      </div>
    </footer>
  );
}

export default Footer;
