import React, { useState, useRef, useEffect } from 'react';

interface RegenerateSplitButtonProps {
  onRegenerateSimple: () => void;
  onRegenerateWithInstructions: (instructions: string) => void;
  disabled?: boolean;
  loading?: boolean;
}

export const RegenerateSplitButton: React.FC<RegenerateSplitButtonProps> = ({
  onRegenerateSimple,
  onRegenerateWithInstructions,
  disabled = false,
  loading = false
}) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [showInstructionsModal, setShowInstructionsModal] = useState(false);
  const [instructions, setInstructions] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleSimpleRegenerate = () => {
    setShowDropdown(false);
    onRegenerateSimple();
  };

  const handleInstructionsRegenerate = () => {
    setShowDropdown(false);
    setShowInstructionsModal(true);
  };

  const handleSubmitInstructions = () => {
    if (instructions.trim()) {
      onRegenerateWithInstructions(instructions.trim());
      setInstructions('');
      setShowInstructionsModal(false);
    }
  };

  const handleCancelInstructions = () => {
    setInstructions('');
    setShowInstructionsModal(false);
  };

  return (
    <>
      <div className="relative inline-flex" ref={dropdownRef}>
        {/* Main button */}
        <button
          onClick={handleSimpleRegenerate}
          disabled={disabled || loading}
          className="px-3 py-2 bg-orange-600 hover:bg-orange-700 text-white text-sm rounded-l transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Regenerating...
            </>
          ) : (
            <>
              🔄 Regenerate
            </>
          )}
        </button>

        {/* Dropdown arrow button */}
        <button
          onClick={() => setShowDropdown(!showDropdown)}
          disabled={disabled || loading}
          className="px-2 py-2 bg-orange-600 hover:bg-orange-700 text-white text-sm rounded-r border-l border-orange-500 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          title="More regenerate options"
          aria-label="More regenerate options"
        >
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>

        {/* Dropdown menu */}
        {showDropdown && (
          <div className="absolute top-full left-0 mt-1 w-64 bg-white border border-gray-200 rounded-md shadow-lg z-10">
            <div className="py-1">
              <button
                onClick={handleSimpleRegenerate}
                className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center"
              >
                <span className="mr-2">🔄</span>
                Simple Regenerate
              </button>
              <button
                onClick={handleInstructionsRegenerate}
                className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center"
              >
                <span className="mr-2">📝</span>
                Regenerate with Instructions
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Instructions Modal */}
      {showInstructionsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Add Instructions for Regeneration</h3>
                <button
                  onClick={handleCancelInstructions}
                  className="text-gray-400 hover:text-gray-600"
                  title="Close dialog"
                  aria-label="Close dialog"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Special Instructions
                </label>
                <textarea
                  value={instructions}
                  onChange={(e) => setInstructions(e.target.value)}
                  placeholder="Enter specific instructions for how the data should be regenerated (e.g., 'Make the values more variable', 'Add seasonal patterns', 'Reduce noise')"
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-orange-500 focus:border-orange-500 resize-none"
                  rows={4}
                />
              </div>

              <div className="flex justify-end space-x-3">
                <button
                  onClick={handleCancelInstructions}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors duration-200"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmitInstructions}
                  disabled={!instructions.trim()}
                  className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                >
                  Regenerate with Instructions
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};