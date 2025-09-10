import { useState } from 'react';
import type { 
  GenerateAnomalyRequest, 
  GenerateAnomalyResponse, 
  AnomalyInfo, 
  InjectionPoint 
} from '../types/api';
import { timeCraftApi } from '../services/timeCraftApi';

export const useAnomaly = () => {
  const [isGeneratingAnomaly, setIsGeneratingAnomaly] = useState(false);
  const [anomalyError, setAnomalyError] = useState<string | null>(null);
  const [selectedInjectionPoints, setSelectedInjectionPoints] = useState<Map<number, InjectionPoint>>(new Map());

  const selectInjectionPoint = (tagIndex: number, dataIndex: number) => {
    setSelectedInjectionPoints(prev => {
      const newMap = new Map(prev);
      const existing = newMap.get(tagIndex);
      
      if (existing && existing.index === dataIndex) {
        // Deselect if clicking the same point
        newMap.delete(tagIndex);
      } else {
        // Select new point
        newMap.set(tagIndex, { index: dataIndex, selected: true });
      }
      
      return newMap;
    });
  };

  const clearInjectionPoint = (tagIndex: number) => {
    setSelectedInjectionPoints(prev => {
      const newMap = new Map(prev);
      newMap.delete(tagIndex);
      return newMap;
    });
  };

  const generateAnomaly = async (
    tagIndex: number,
    tagName: string,
    tagDescription: string,
    existingTimeSeries: number[],
    anomalyType: string,
    anomalyDescription: string,
    severity: number = 1.0
  ): Promise<GenerateAnomalyResponse | null> => {
    const injectionPoint = selectedInjectionPoints.get(tagIndex);
    
    if (!injectionPoint) {
      setAnomalyError('Please select an injection point on the chart first');
      return null;
    }

    setIsGeneratingAnomaly(true);
    setAnomalyError(null);

    try {
      // For now, create a small anomaly window around the selected point
      const windowSize = Math.min(10, Math.floor(existingTimeSeries.length * 0.1)); // 10% of series or max 10 points
      const startIndex = Math.max(0, injectionPoint.index - Math.floor(windowSize / 2));
      const endIndex = Math.min(existingTimeSeries.length - 1, startIndex + windowSize);

      const request: GenerateAnomalyRequest = {
        tagName,
        tagDescription,
        existingTimeSeries,
        injectionStartIndex: startIndex,
        injectionEndIndex: endIndex,
        anomalyType,
        anomalyDescription,
        severity
      };

      console.log('Generating anomaly with request:', request);
      const response = await timeCraftApi.generateAnomaly(request);
      
      if (response.success) {
        // Clear the injection point after successful generation
        clearInjectionPoint(tagIndex);
      } else {
        setAnomalyError(response.message || 'Failed to generate anomaly');
      }
      
      return response;
    } catch (error) {
      console.error('Error generating anomaly:', error);
      setAnomalyError(error instanceof Error ? error.message : 'An unexpected error occurred');
      return null;
    } finally {
      setIsGeneratingAnomaly(false);
    }
  };

  const getAnomalyTypes = () => [
    { value: 'spike', label: 'Spike', description: 'Sudden increase in values' },
    { value: 'dip', label: 'Dip', description: 'Sudden decrease in values' },
    { value: 'drift', label: 'Drift', description: 'Gradual change in baseline' },
    { value: 'noise', label: 'Noise', description: 'Increased variability' },
    { value: 'flatline', label: 'Flatline', description: 'Constant value period' },
    { value: 'oscillation', label: 'Oscillation', description: 'Unusual periodic behavior' },
    { value: 'outliers', label: 'Outliers', description: 'Scattered abnormal points' }
  ];

  return {
    isGeneratingAnomaly,
    anomalyError,
    selectedInjectionPoints,
    selectInjectionPoint,
    clearInjectionPoint,
    generateAnomaly,
    getAnomalyTypes,
    setAnomalyError
  };
};
