import React from 'react';

export const Header: React.FC = () => {
  return (
    <div className="text-center mb-8">
      <h1 className="text-4xl font-bold text-white mb-2">
        🕰️ TimeCraft
      </h1>
      <p className="text-white/80 text-lg">
        AI-Powered Time Series Generation from Natural Language
      </p>
    </div>
  );
};
