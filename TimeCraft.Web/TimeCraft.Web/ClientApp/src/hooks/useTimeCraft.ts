import { useState, useCallback } from 'react';
import type { TimeSeriesData, GeneratedTag, TagProgress, TagProgressStatus } from '../types/api';
import { timeCraftApi } from '../services/timeCraftApi';
import { TIME_HORIZON_OPTIONS, type TimeHorizonOption } from '../types/timeHorizon';

export const useTimeCraft = () => {
  const [description, setDescription] = useState('');
  const [timeHorizon, setTimeHorizon] = useState<TimeHorizonOption>(TIME_HORIZON_OPTIONS[2]); // Default to 24 hours
  const [isLoading, setIsLoading] = useState(false);
  const [tags, setTags] = useState<GeneratedTag[]>([]);
  const [tagProgress, setTagProgress] = useState<TagProgress[]>([]);
  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesData[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loadingDataset, setLoadingDataset] = useState(false);

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
    setDescription('');
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
      
      // Handle batching for large datasets
      if (timeHorizon.batchCount > 1) {
        console.log(`Retrying ${timeHorizon.batchCount} batches for large dataset`);
        
        let allData: number[] = [];
        let allTimestamps: string[] = [];
        
        // Generate data in batches
        for (let batchIndex = 0; batchIndex < timeHorizon.batchCount; batchIndex++) {
          const batchResponse = await timeCraftApi.generateTimeSeries({
            tag: tag.tag,
            scenario: description,
            timeHorizon: {
              period: timeHorizon.config.period,
              unit: timeHorizon.config.unit,
              granularity: timeHorizon.config.granularity,
              totalPoints: timeHorizon.totalPoints,
              batchSize: 500,
              batchIndex: batchIndex
            }
          });

          if (!batchResponse.success) {
            throw new Error(batchResponse.message || `Failed to generate batch ${batchIndex + 1}`);
          }

          allData.push(...batchResponse.timeSeries);
          if (batchResponse.timestamps) {
            allTimestamps.push(...batchResponse.timestamps);
          }
        }
        
        // Create time series data from combined batches
        const timeSeriesEntry: TimeSeriesData = {
          name: tag.tag,
          data: allData,
          timestamps: allTimestamps.length > 0 ? allTimestamps : undefined
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
        
      } else {
        // Single batch retry
        const tsResponse = await timeCraftApi.generateTimeSeries({
          tag: tag.tag,
          scenario: description,
          timeHorizon: {
            period: timeHorizon.config.period,
            unit: timeHorizon.config.unit,
            granularity: timeHorizon.config.granularity,
            totalPoints: timeHorizon.totalPoints,
            batchSize: undefined,
            batchIndex: 0
          }
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
      }

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
      const tagsResponse = await timeCraftApi.generateTags({ 
        Text: description,
        timeHorizon: {
          period: timeHorizon.config.period,
          unit: timeHorizon.config.unit,
          granularity: timeHorizon.config.granularity,
          totalPoints: timeHorizon.totalPoints
        }
      });
      
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
          
          // Handle batching for large datasets
          if (timeHorizon.batchCount > 1) {
            console.log(`Generating ${timeHorizon.batchCount} batches for large dataset (${timeHorizon.totalPoints} points)`);
            
            let allData: number[] = [];
            let allTimestamps: string[] = [];
            
            // Generate data in batches
            for (let batchIndex = 0; batchIndex < timeHorizon.batchCount; batchIndex++) {
              console.log(`Generating batch ${batchIndex + 1}/${timeHorizon.batchCount}`);
              
              const batchResponse = await timeCraftApi.generateTimeSeries({
                tag: tag.tag,
                scenario: description,
                timeHorizon: {
                  period: timeHorizon.config.period,
                  unit: timeHorizon.config.unit,
                  granularity: timeHorizon.config.granularity,
                  totalPoints: timeHorizon.totalPoints,
                  batchSize: 500,
                  batchIndex: batchIndex
                }
              });

              if (!batchResponse.success) {
                throw new Error(batchResponse.message || `Failed to generate batch ${batchIndex + 1}`);
              }

              allData.push(...batchResponse.timeSeries);
              if (batchResponse.timestamps) {
                allTimestamps.push(...batchResponse.timestamps);
              }
            }
            
            // Create time series data from combined batches
            const timeSeriesEntry: TimeSeriesData = {
              name: tag.tag,
              data: allData,
              timestamps: allTimestamps.length > 0 ? allTimestamps : undefined
            };

            // Update progress with completed time series
            updateTagProgress(tagIndex, { 
              status: 'complete',
              timeSeriesData: timeSeriesEntry
            });

            // Add to time series data immediately
            setTimeSeriesData(prev => [...prev, timeSeriesEntry]);
            
          } else {
            // Single batch generation
            const tsResponse = await timeCraftApi.generateTimeSeries({
              tag: tag.tag,
              scenario: description,
              timeHorizon: {
                period: timeHorizon.config.period,
                unit: timeHorizon.config.unit,
                granularity: timeHorizon.config.granularity,
                totalPoints: timeHorizon.totalPoints,
                batchSize: undefined,
                batchIndex: 0
              }
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
          }

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

  const loadDataset = useCallback(async (datasetId: string) => {
    try {
      setLoadingDataset(true);
      setError(null);
      
      console.log('🚀 Loading dataset content with ID:', datasetId);
      
      // Fetch the dataset content including tags and time series data
      const dataset = await timeCraftApi.getDatasetContent(datasetId);
      
      console.log('📊 Full dataset content received:', dataset);
      
      if (!dataset) {
        throw new Error('Dataset not found');
      }

      // Set the description
      if (dataset.description) {
        setDescription(dataset.description);
      }

      // Load the tags and their time series data
      if (dataset.tags && dataset.tags.length > 0) {
        // Create GeneratedTag array for the tags state
        const generatedTags: GeneratedTag[] = dataset.tags.map(tag => ({
          tag: tag.tagName,
          description: tag.description
        }));

        // Create TagProgress array with the loaded time series data
        const loadedTags: TagProgress[] = dataset.tags.map(tag => ({
          tag: tag.tagName,
          description: tag.description,
          status: 'complete' as TagProgressStatus,
          timeSeriesData: {
            name: tag.tagName,
            data: tag.timeSeriesData?.map(point => point.value) || [],
            timestamps: tag.timeSeriesData?.map(point => point.time || '') || []
          }
        }));

        // Set both tags and tagProgress to ensure UI renders correctly
        setTags(generatedTags);
        setTagProgress(loadedTags);
        
        // Also set the global time series data
        const timeSeriesData = loadedTags
          .filter(tag => tag.timeSeriesData)
          .map(tag => tag.timeSeriesData!);
        setTimeSeriesData(timeSeriesData);

        console.log('✅ Dataset content loaded successfully:', {
          datasetName: dataset.datasetName,
          description: dataset.description,
          status: dataset.status,
          publishedAt: dataset.publishedAt,
          totalTags: dataset.totalTags,
          totalDataPoints: dataset.totalDataPoints,
          loadedTags: loadedTags.length,
          loadedTimeSeriesData: timeSeriesData.length
        });
      } else {
        console.log('⚠️ Dataset loaded but no tags found:', dataset);
      }
      
    } catch (err: unknown) {
      console.error('Error loading dataset:', err);
      let errorMessage = 'Failed to load dataset';
      
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (typeof err === 'object' && err !== null && 'response' in err) {
        const response = (err as { response?: { data?: { message?: string } } }).response;
        errorMessage = response?.data?.message || errorMessage;
      }
      
      setError(errorMessage);
    } finally {
      setLoadingDataset(false);
    }
  }, []);

  return {
    description,
    setDescription,
    timeHorizon,
    setTimeHorizon,
    isLoading,
    loadingDataset,
    tags,
    tagProgress,
    timeSeriesData,
    error,
    generateTimeSeries,
    clearAll,
    retryTag,
    updateTagTimeSeriesData,
    loadDataset
  };
};
