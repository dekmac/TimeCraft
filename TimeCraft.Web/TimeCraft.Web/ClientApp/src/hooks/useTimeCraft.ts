import { useState } from 'react';
import type { TimeSeriesData, GeneratedTag, TagProgress, TagProgressStatus } from '../types/api';
import { timeCraftApi } from '../services/timeCraftApi';

export const useTimeCraft = () => {
  const [description, setDescription] = useState('');
  const [dataLength, setDataLength] = useState(100);
  const [isLoading, setIsLoading] = useState(false);
  const [tags, setTags] = useState<GeneratedTag[]>([]);
  const [tagProgress, setTagProgress] = useState<TagProgress[]>([]);
  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesData[]>([]);
  const [error, setError] = useState<string | null>(null);

    const updateTagProgress = (index: number, updates: Partial<TagProgress>) => {
    setTagProgress(prev => prev.map((tag, i) => 
      i === index ? { ...tag, ...updates } : tag
    ));
  };

  const generateTimeSeries = async () => {
    if (!description.trim()) {
      setError('Please enter a description');
      return;
    }

    setIsLoading(true);
    setError(null);
    setTags([]);
    setTagProgress([]);
    setTimeSeriesData([]);

    try {
      console.log('Generating tags for description:', description);
      
      // Step 1: Generate tags
      const tagsResponse = await timeCraftApi.generateTags({ text: description });
      
      if (!tagsResponse.success || !tagsResponse.tags) {
        throw new Error(tagsResponse.message || 'Failed to generate tags');
      }

      const generatedTags = tagsResponse.tags;
      setTags(generatedTags);

      // Initialize progress for each tag
      const initialProgress: TagProgress[] = generatedTags.map(tag => ({
        ...tag,
        status: 'tag-complete' as TagProgressStatus
      }));
      setTagProgress(initialProgress);

      // Step 2: Generate time series for each tag progressively
      for (let i = 0; i < generatedTags.length; i++) {
        const tag = generatedTags[i];
        
        try {
          // Update status to generating time series
          updateTagProgress(i, { status: 'generating-timeseries' });

          console.log(`Generating time series for tag: ${tag.tag}`);
          
          const tsResponse = await timeCraftApi.generateTimeSeries({
            tag: tag.tag,
            scenario: description
          });

          if (!tsResponse.success) {
            throw new Error(tsResponse.message || 'Failed to generate time series');
          }

          // Create time series data
          const timeSeriesEntry: TimeSeriesData = {
            name: tsResponse.tagName,
            data: tsResponse.timeSeries,
            timestamps: tsResponse.timestamps
          };

          // Update progress with completed time series
          updateTagProgress(i, { 
            status: 'complete',
            timeSeriesData: timeSeriesEntry
          });

          // Add to time series data immediately
          setTimeSeriesData(prev => [...prev, timeSeriesEntry]);

        } catch (tagError: unknown) {
          console.error(`Error generating time series for tag ${tag.tag}:`, tagError);
          
          let errorMessage = 'Failed to generate time series';
          if (tagError instanceof Error) {
            errorMessage = tagError.message;
          }

          updateTagProgress(i, { 
            status: 'error',
            error: errorMessage
          });
        }
      }

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
    tagProgress,
    timeSeriesData,
    error,
    generateTimeSeries
  };
};
