import React from 'react';
import './ExampleQueries.css';

const ExampleQueries = ({ onExampleClick }) => {
  const examples = [
    "कर्नाटक में फिनटेक फंडिंग?",
    "How many healthtech startups got funding in 2020?",
    "Top investors in e-commerce sector",
    "Total funding in Bangalore fintech 2019"
  ];

  return (
    <div className="example-queries">
      <h3 className="example-title">Try These Example Queries</h3>
      <div className="example-grid">
        {examples.map((example, index) => (
          <button
            key={index}
            className="example-card"
            onClick={() => onExampleClick(example)}
          >
            <span className="example-text">{example}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default ExampleQueries;
