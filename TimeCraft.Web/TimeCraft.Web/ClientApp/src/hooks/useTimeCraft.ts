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

  const updateTagTimeSeriesData = (tagIndex: number, newData: number[], newTimestamps?: string[]) => {
    setTagProgress(prev => prev.map((tag, i) => {
      if (i === tagIndex && tag.timeSeriesData) {
        const updatedTimeSeriesData = {
          ...tag.timeSeriesData,
          data: newData,
          timestamps: newTimestamps || tag.timeSeriesData.timestamps
        };
        
        return {
          ...tag,
          timeSeriesData: updatedTimeSeriesData
        };
      }
      return tag;
    }));

    // Also update the global time series data
    setTimeSeriesData(prev => prev.map(ts => {
      const tag = tagProgress[tagIndex];
      if (tag && ts.name === tag.tag) {
        return {
          ...ts,
          data: newData,
          timestamps: newTimestamps || ts.timestamps
        };
      }
      return ts;
    }));
  };

  const generateTimeSeries = async () => {
    if (!description.trim()) {
      setError('Please enter a description');
      return;
    }

    setIsLoading(true);
    setError(null);

    // Smart behavior: if we have existing tags, be additive; otherwise start fresh
    const isAdditive = tags.length > 0;
    
    if (!isAdditive) {
      // Fresh start - clear everything
      setTags([]);
      setTagProgress([]);
      setTimeSeriesData([]);
    }

    await generateTagsAndTimeSeries(isAdditive);
  };

  const clearAll = () => {
    setTags([]);
    setTagProgress([]);
    setTimeSeriesData([]);
    setError(null);
  };

  const retryTag = async (tagIndex: number) => {
    const tag = tagProgress[tagIndex];
    if (!tag) return;

    // Update status to generating
    updateTagProgress(tagIndex, { 
      status: 'generating-timeseries',
      error: undefined 
    });

    try {
      console.log(`Retrying time series generation for tag: ${tag.tag}`);
      
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
      updateTagProgress(tagIndex, { 
        status: 'complete',
        timeSeriesData: timeSeriesEntry
      });

      // Add to time series data (replace if exists)
      setTimeSeriesData(prev => {
        const filtered = prev.filter(ts => ts.name !== timeSeriesEntry.name);
        return [...filtered, timeSeriesEntry];
      });

    } catch (tagError: unknown) {
      console.error(`Error retrying time series for tag ${tag.tag}:`, tagError);
      
      let errorMessage = 'Failed to generate time series';
      if (tagError instanceof Error) {
        errorMessage = tagError.message;
      }

      updateTagProgress(tagIndex, { 
        status: 'error',
        error: errorMessage
      });
    }
  };

  const generateTagsAndTimeSeries = async (additive: boolean = false) => {

    try {
      console.log('Generating tags for description:', description);
      
      // Step 1: Generate tags
      const tagsResponse = await timeCraftApi.generateTags({ Text: description });
      
      if (!tagsResponse.success || !tagsResponse.tags) {
        throw new Error(tagsResponse.message || 'Failed to generate tags');
      }

      const generatedTags = tagsResponse.tags;
      
      // In additive mode, append to existing tags; otherwise replace
      if (additive) {
        setTags(prev => [...prev, ...generatedTags]);
      } else {
        setTags(generatedTags);
      }

      // Initialize progress for new tags
      const newProgress: TagProgress[] = generatedTags.map(tag => ({
        ...tag,
        status: 'tag-complete' as TagProgressStatus
      }));

      if (additive) {
        setTagProgress(prev => [...prev, ...newProgress]);
      } else {
        setTagProgress(newProgress);
      }

      // Get the starting index for new tags
      const startIndex = additive ? tagProgress.length : 0;

      // Step 2: Generate time series for each new tag progressively
      for (let i = 0; i < generatedTags.length; i++) {
        const tagIndex = startIndex + i;
        const tag = generatedTags[i];
        
        try {
          // Update status to generating time series
          updateTagProgress(tagIndex, { status: 'generating-timeseries' });

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
          updateTagProgress(tagIndex, { 
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

          updateTagProgress(tagIndex, { 
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
    generateTimeSeries,
    clearAll,
    retryTag,
    updateTagTimeSeriesData
  };
};
