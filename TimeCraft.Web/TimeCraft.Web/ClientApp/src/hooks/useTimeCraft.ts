import { useState } from 'react';
import type { TimeSeriesData, GeneratedTag } from '../types/api';
import { timeCraftApi } from '../services/timeCraftApi';

export const useTimeCraft = () => {
  const [description, setDescription] = useState('');
  const [dataLength, setDataLength] = useState(100);
  const [isLoading, setIsLoading] = useState(false);
  const [tags, setTags] = useState<GeneratedTag[]>([]);
  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesData[]>([]);
  const [error, setError] = useState<string | null>(null);

  const generateTimeSeries = async () => {
    if (!description.trim()) {
      setError('Please enter a scenario description');
      return;
    }

    // Prevent multiple simultaneous calls
    if (isLoading) {
      console.log('Already loading, skipping duplicate call');
      return;
    }

    console.log('Starting generateTimeSeries...');
    setIsLoading(true);
    setError(null);
    setTags([]);
    setTimeSeriesData([]);

    try {
      // Generate tags
      const tagResponse = await timeCraftApi.generateTags({
        text: description
      });

      if (!tagResponse.success) {
        throw new Error(tagResponse.message || 'Failed to generate tags');
      }

      const generatedTags = tagResponse.tags;
      setTags(generatedTags);

      // Generate time series for each tag
      const seriesPromises = generatedTags.map(async (tag: GeneratedTag) => {
        const tsResponse = await timeCraftApi.generateTimeSeries({
          tag: tag.tag,
          scenario: description
        });

        if (!tsResponse.success) {
          throw new Error(`Failed to generate time series for tag: ${tag.tag}`);
        }

        return {
          name: tag.tag,
          data: tsResponse.time_series,
          timestamps: tsResponse.timestamps
        };
      });

      const allSeries = await Promise.all(seriesPromises);
      setTimeSeriesData(allSeries);

    } catch (err: unknown) {
      console.error('Error generating time series:', err);
      let errorMessage = 'Failed to generate time series';
      
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (typeof err === 'object' && err !== null && 'response' in err) {
        const response = (err as { response?: { data?: { message?: string } } }).response;
        errorMessage = response?.data?.message || errorMessage;
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    description,
    setDescription,
    dataLength,
    setDataLength,
    isLoading,
    tags,
    timeSeriesData,
    error,
    generateTimeSeries
  };
};
