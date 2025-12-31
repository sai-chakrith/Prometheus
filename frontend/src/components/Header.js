import React from 'react';
import { HiMenuAlt3 } from 'react-icons/hi';
import './Header.css';

const Header = ({ onMenuClick }) => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-title">
          <h1 className="gradient-text">PROMETHEUS</h1>
          <p className="header-subtitle">
            AI-Powered Startup Funding Analytics | Illuminating Investment Intelligence
          </p>
        </div>
        
        <button className="menu-button" onClick={onMenuClick} aria-label="Toggle menu">
          <HiMenuAlt3 />
        </button>
      </div>
    </header>
  );
};

export default Header;
