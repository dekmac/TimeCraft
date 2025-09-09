import React from 'react';

interface InputFormProps {
  description: string;
  setDescription: (value: string) => void;
  dataLength: number;
  setDataLength: (value: number) => void;
  isLoading: boolean;
  onGenerate: () => void;
  onClearAll?: () => void;
  hasExistingData?: boolean;
}

export const InputForm: React.FC<InputFormProps> = ({
  description,
  setDescription,
  dataLength,
  setDataLength,
  isLoading,
  onGenerate,
  onClearAll,
  hasExistingData = false
}) => {
  return (
    <div className="glass-effect p-6 mb-6">
      <div className="space-y-4">
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
            Scenario Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Describe the time series you want to generate (e.g., 'Daily stock prices for a tech company during a market crash')"
            className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          />
        </div>

        <div className="flex items-center space-x-4">
          <div>
            <label htmlFor="dataLength" className="block text-sm font-medium text-gray-700 mb-1">
              Data Length
            </label>
            <select
              id="dataLength"
              value={dataLength}
              onChange={(e) => setDataLength(Number(e.target.value))}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value={50}>50 points</option>
              <option value={100}>100 points</option>
              <option value={200}>200 points</option>
              <option value={500}>500 points</option>
            </select>
          </div>

          <div className="flex-1">
                      <div className="flex flex-col space-y-3">
            <button
              type="button"
              onClick={onGenerate}
              disabled={isLoading}
              className={`w-full text-white px-6 py-3 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 ${
                hasExistingData 
                  ? 'bg-gradient-to-r from-green-500 to-teal-600 hover:from-green-600 hover:to-teal-700'
                  : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700'
              }`}
            >
              {isLoading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {hasExistingData ? 'Adding Tags...' : 'Generating...'}
                </span>
              ) : (
                hasExistingData ? '+ Add More Tags' : 'Generate Time Series'
              )}
            </button>
            
            {hasExistingData && onClearAll && (
              <button
                type="button"
                onClick={onClearAll}
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-red-500 to-red-600 text-white px-4 py-2 rounded-lg font-medium hover:from-red-600 hover:to-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 text-sm"
              >
                🗑️ Clear All & Start Over
              </button>
            )}
          </div>
          </div>
        </div>
      </div>
    </div>
  );
};
