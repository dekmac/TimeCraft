import React from 'react';

interface ErrorDisplayProps {
  error: string | null;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error }) => {
  if (!error) {
    return null;
  }

  return (
    <div className="glass-effect p-4 mb-6 border-l-4 border-red-500">
      <div className="flex">
        <div className="ml-3">
          <p className="text-sm text-red-700">
            <strong>Error:</strong> {error}
          </p>
        </div>
      </div>
    </div>
  );
};
