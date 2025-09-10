import React, { useState } from 'react';
import type { InjectionPoint } from '../types/api';

interface AnomalyControlsProps {
  tagIndex: number;
  tagName: string;
  tagDescription: string;
  existingTimeSeries: number[];
  selectedInjectionPoint?: InjectionPoint;
  isGeneratingAnomaly: boolean;
  anomalyTypes: Array<{ value: string; label: string; description: string }>;
  onGenerateAnomaly: (
    tagIndex: number,
    tagName: string,
    tagDescription: string,
    existingTimeSeries: number[],
    anomalyType: string,
    anomalyDescription: string,
    severity: number
  ) => Promise<void>;
  onSelectInjectionPoint: (tagIndex: number, dataIndex: number) => void;
}

export const AnomalyControls: React.FC<AnomalyControlsProps> = ({
  tagIndex,
  tagName,
  tagDescription,
  existingTimeSeries,
  selectedInjectionPoint,
  isGeneratingAnomaly,
  anomalyTypes,
  onGenerateAnomaly,
  onSelectInjectionPoint
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [selectedAnomalyType, setSelectedAnomalyType] = useState('spike');
  const [anomalyDescription, setAnomalyDescription] = useState('');
  const [severity, setSeverity] = useState(1.0);

  const handleGenerateAnomaly = async () => {
    await onGenerateAnomaly(
      tagIndex,
      tagName,
      tagDescription,
      existingTimeSeries,
      selectedAnomalyType,
      anomalyDescription || `Generate a ${selectedAnomalyType} anomaly in the ${tagName} sensor data`,
      severity
    );
    setIsExpanded(false);
  };

  const selectedAnomalyTypeInfo = anomalyTypes.find(type => type.value === selectedAnomalyType);

  if (!isExpanded) {
    return (
      <button
        onClick={() => setIsExpanded(true)}
        disabled={isGeneratingAnomaly}
        className="text-xs bg-orange-500 hover:bg-orange-600 text-white px-2 py-1 rounded transition-colors duration-200 flex items-center space-x-1"
        title="Add anomaly to this time series"
      >
        <span>⚡</span>
        <span>Add Anomaly</span>
      </button>
    );
  }

  return (
    <div className="bg-white/80 rounded-lg p-3 border border-orange-200 mt-2">
      <div className="flex items-center justify-between mb-3">
        <h5 className="text-sm font-medium text-orange-800">Add Anomaly</h5>
        <button
          onClick={() => setIsExpanded(false)}
          className="text-gray-400 hover:text-gray-600 text-sm"
        >
          ✕
        </button>
      </div>

      {!selectedInjectionPoint && (
        <div className="mb-3 p-2 bg-blue-50 rounded text-xs text-blue-700">
          💡 Click on the chart above to select where to inject the anomaly
        </div>
      )}

      {selectedInjectionPoint && (
        <div className="mb-3 p-2 bg-green-50 rounded text-xs text-green-700">
          ✅ Injection point selected at index {selectedInjectionPoint.index}
        </div>
      )}

      <div className="space-y-2">
        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Anomaly Type
          </label>
          <select
            value={selectedAnomalyType}
            onChange={(e) => setSelectedAnomalyType(e.target.value)}
            className="w-full text-xs border border-gray-300 rounded px-2 py-1 focus:ring-1 focus:ring-orange-500 focus:border-orange-500"
            title="Select anomaly type"
          >
            {anomalyTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
          {selectedAnomalyTypeInfo && (
            <p className="text-xs text-gray-500 mt-1">{selectedAnomalyTypeInfo.description}</p>
          )}
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Severity (0.1 - 3.0)
          </label>
          <input
            type="range"
            min="0.1"
            max="3.0"
            step="0.1"
            value={severity}
            onChange={(e) => setSeverity(parseFloat(e.target.value))}
            className="w-full"
            title={`Anomaly severity: ${severity.toFixed(1)}`}
          />
          <div className="flex justify-between text-xs text-gray-500">
            <span>Mild</span>
            <span className="font-medium">{severity.toFixed(1)}</span>
            <span>Severe</span>
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-700 mb-1">
            Description (Optional)
          </label>
          <textarea
            value={anomalyDescription}
            onChange={(e) => setAnomalyDescription(e.target.value)}
            placeholder={`Describe the ${selectedAnomalyType} anomaly...`}
            className="w-full text-xs border border-gray-300 rounded px-2 py-1 h-12 resize-none focus:ring-1 focus:ring-orange-500 focus:border-orange-500"
          />
        </div>

        <div className="flex space-x-2 pt-2">
          <button
            onClick={handleGenerateAnomaly}
            disabled={!selectedInjectionPoint || isGeneratingAnomaly}
            className="flex-1 text-xs bg-orange-500 hover:bg-orange-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white px-2 py-1 rounded transition-colors duration-200 flex items-center justify-center space-x-1"
          >
            {isGeneratingAnomaly ? (
              <>
                <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white"></div>
                <span>Generating...</span>
              </>
            ) : (
              <>
                <span>⚡</span>
                <span>Generate</span>
              </>
            )}
          </button>
          <button
            onClick={() => setIsExpanded(false)}
            className="text-xs border border-gray-300 hover:bg-gray-50 text-gray-700 px-2 py-1 rounded transition-colors duration-200"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};
