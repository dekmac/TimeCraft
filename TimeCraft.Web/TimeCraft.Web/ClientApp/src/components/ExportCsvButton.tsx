import React, { useState } from 'react';
import { Download, Calendar, Filter, Clock } from 'lucide-react';

interface ExportCsvButtonProps {
  datasetId: string;
  datasetName?: string;
  availableTags?: string[];
  className?: string;
}

interface ExportOptions {
  useRelativeTimestamps: boolean;
  startTime?: string;
  endTime?: string;
  referenceTime?: string;
  tagFilter?: string[];
}

const ExportCsvButton: React.FC<ExportCsvButtonProps> = ({
  datasetId,
  datasetName = 'Dataset',
  availableTags = [],
  className = ''
}) => {
  const [isExporting, setIsExporting] = useState(false);
  const [showOptions, setShowOptions] = useState(false);
  const [options, setOptions] = useState<ExportOptions>({
    useRelativeTimestamps: true,
    tagFilter: []
  });

  const handleExport = async () => {
    try {
      setIsExporting(true);
      
      const params = new URLSearchParams();
      
      if (options.useRelativeTimestamps !== undefined) {
        params.append('useRelativeTimestamps', String(options.useRelativeTimestamps));
      }
      if (options.startTime) {
        params.append('startTime', new Date(options.startTime).toISOString());
      }
      if (options.endTime) {
        params.append('endTime', new Date(options.endTime).toISOString());
      }
      if (options.referenceTime) {
        params.append('referenceTime', new Date(options.referenceTime).toISOString());
      }
      if (options.tagFilter && options.tagFilter.length > 0) {
        options.tagFilter.forEach(tag => params.append('tagFilter', tag));
      }

      const url = `/api/publishing/datasets/${datasetId}/export-csv?${params.toString()}`;
      
      // Create a temporary link to download the file
      const link = document.createElement('a');
      link.href = url;
      link.download = ''; // Let the server determine the filename
      link.style.display = 'none';
      
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Reset state after a delay
      setTimeout(() => {
        setIsExporting(false);
      }, 2000);
      
    } catch (error) {
      console.error('Export failed:', error);
      setIsExporting(false);
      alert('Export failed. Please try again.');
    }
  };

  const handleTagToggle = (tag: string) => {
    const currentTags = options.tagFilter || [];
    const newTags = currentTags.includes(tag)
      ? currentTags.filter(t => t !== tag)
      : [...currentTags, tag];
    
    setOptions({ ...options, tagFilter: newTags });
  };

  return (
    <div className={`relative ${className}`}>
      {/* Main Export Button */}
      <div className="flex gap-2">
        <button
          onClick={handleExport}
          disabled={isExporting}
          className={`
            flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all
            ${isExporting 
              ? 'bg-gray-400 cursor-not-allowed' 
              : 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800'
            }
            text-white shadow-sm
          `}
        >
          <Download size={16} />
          {isExporting ? 'Exporting...' : 'Export OPC UA CSV'}
        </button>
        
        {/* Options Toggle */}
        <button
          onClick={() => setShowOptions(!showOptions)}
          className="px-3 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          title="Export Options"
        >
          <Filter size={16} />
        </button>
      </div>

      {/* Export Options Panel */}
      {showOptions && (
        <div className="absolute top-full left-0 mt-2 w-96 bg-white border border-gray-200 rounded-lg shadow-lg p-4 z-50">
          <h3 className="font-semibold text-gray-900 mb-3">Export Options</h3>
          
          {/* Timestamp Type */}
          <div className="mb-4">
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Clock size={16} />
              Timestamp Format
            </label>
            <div className="space-y-2">
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  checked={options.useRelativeTimestamps}
                  onChange={() => setOptions({ ...options, useRelativeTimestamps: true })}
                  className="text-blue-600"
                />
                <span className="text-sm">Relative timestamps (seconds from reference)</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  checked={!options.useRelativeTimestamps}
                  onChange={() => setOptions({ ...options, useRelativeTimestamps: false })}
                  className="text-blue-600"
                />
                <span className="text-sm">Absolute timestamps</span>
              </label>
            </div>
          </div>

          {/* Reference Time (only show if relative timestamps enabled) */}
          {options.useRelativeTimestamps && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Reference Time (optional)
              </label>
              <input
                type="datetime-local"
                value={options.referenceTime || ''}
                onChange={(e) => setOptions({ ...options, referenceTime: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                placeholder="Leave empty for current time"
              />
            </div>
          )}

          {/* Time Range */}
          <div className="mb-4">
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Calendar size={16} />
              Time Range (optional)
            </label>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="block text-xs text-gray-500 mb-1">Start Time</label>
                <input
                  type="datetime-local"
                  value={options.startTime || ''}
                  onChange={(e) => setOptions({ ...options, startTime: e.target.value })}
                  className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-500 mb-1">End Time</label>
                <input
                  type="datetime-local"
                  value={options.endTime || ''}
                  onChange={(e) => setOptions({ ...options, endTime: e.target.value })}
                  className="w-full px-2 py-1 border border-gray-300 rounded text-sm"
                />
              </div>
            </div>
          </div>

          {/* Tag Filter */}
          {availableTags.length > 0 && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter Tags (select specific tags to export)
              </label>
              <div className="max-h-32 overflow-y-auto space-y-1">
                {availableTags.map((tag) => (
                  <label key={tag} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={options.tagFilter?.includes(tag) || false}
                      onChange={() => handleTagToggle(tag)}
                      className="text-blue-600"
                    />
                    <span className="text-sm">{tag}</span>
                  </label>
                ))}
              </div>
              {options.tagFilter && options.tagFilter.length > 0 && (
                <div className="mt-2 text-xs text-gray-500">
                  Selected: {options.tagFilter.length} tag{options.tagFilter.length !== 1 ? 's' : ''}
                </div>
              )}
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end gap-2 pt-3 border-t border-gray-200">
            <button
              onClick={() => setShowOptions(false)}
              className="px-3 py-1 text-sm text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                handleExport();
                setShowOptions(false);
              }}
              disabled={isExporting}
              className="px-4 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 disabled:bg-gray-400"
            >
              Export
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExportCsvButton;