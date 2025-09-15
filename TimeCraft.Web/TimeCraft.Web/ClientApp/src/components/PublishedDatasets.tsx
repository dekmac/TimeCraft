import React, { useState, useEffect, useRef } from 'react';
import { timeCraftApi } from '../services/timeCraftApi';
import type { PublishedDataset, PublishingMode, StreamConfiguration } from '../types/api';

export const PublishedDatasets: React.FC = () => {
  const [datasets, setDatasets] = useState<PublishedDataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [retryingDatasets, setRetryingDatasets] = useState<Set<string>>(new Set());
  const [downloadingDatasets, setDownloadingDatasets] = useState<Set<string>>(new Set());
  const [expandedDatasets, setExpandedDatasets] = useState<Set<string>>(new Set());
  const [reIngestingDatasets, setReIngestingDatasets] = useState<Set<string>>(new Set());
  const [streamControlDatasets, setStreamControlDatasets] = useState<Set<string>>(new Set());
  const [modeUpdateDatasets, setModeUpdateDatasets] = useState<Set<string>>(new Set());
  const datasetsRef = useRef<PublishedDataset[]>([]);

  const loadDatasets = async () => {
    try {
      setError(null);
      const data = await timeCraftApi.getPublishedDatasets();
      setDatasets(data);
      datasetsRef.current = data;
    } catch (err) {
      console.error('Error loading published datasets:', err);
      setError('Failed to load published datasets. Please try again.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDatasets();
  };

  const handleForceRetry = async (datasetId: string, datasetName: string) => {
    try {
      setRetryingDatasets(prev => new Set(prev).add(datasetId));
      
      await timeCraftApi.forceRetryDataset(datasetId);
      
      // Refresh datasets to show updated status
      await loadDatasets();
      
      console.log(`Force retry initiated for dataset: ${datasetName}`);
    } catch (err) {
      console.error('Error forcing retry:', err);
      setError(`Failed to force retry for dataset "${datasetName}". Please try again.`);
    } finally {
      setRetryingDatasets(prev => {
        const newSet = new Set(prev);
        newSet.delete(datasetId);
        return newSet;
      });
    }
  };

  const handleDownloadCsv = async (datasetId: string, datasetName: string) => {
    try {
      setDownloadingDatasets(prev => new Set(prev).add(datasetId));
      
      const filename = `${datasetName.replace(/[^a-zA-Z0-9]/g, '_')}_${new Date().toISOString().slice(0, 10)}.csv`;
      await timeCraftApi.downloadDatasetCsv(datasetId, filename);
      
      console.log(`Downloaded CSV for dataset: ${datasetName}`);
    } catch (err) {
      console.error('Error downloading CSV:', err);
      setError(`Failed to download CSV for dataset "${datasetName}". Please try again.`);
    } finally {
      setDownloadingDatasets(prev => {
        const newSet = new Set(prev);
        newSet.delete(datasetId);
        return newSet;
      });
    }
  };

  const handleReIngest = async (datasetId: string, datasetName: string) => {
    try {
      setReIngestingDatasets(prev => new Set(prev).add(datasetId));
      
      await timeCraftApi.reIngestDataset(datasetId);
      
      // Refresh datasets to show updated status
      await loadDatasets();
      
      console.log(`Re-ingestion initiated for dataset: ${datasetName}`);
    } catch (err) {
      console.error('Error re-ingesting dataset:', err);
      setError(`Failed to re-ingest dataset "${datasetName}". Please try again.`);
    } finally {
      setReIngestingDatasets(prev => {
        const newSet = new Set(prev);
        newSet.delete(datasetId);
        return newSet;
      });
    }
  };

  const handleStreamControl = async (datasetId: string, datasetName: string, action: 'start' | 'stop' | 'pause') => {
    try {
      setStreamControlDatasets(prev => new Set(prev).add(datasetId));
      
      switch (action) {
        case 'start':
          await timeCraftApi.startStreaming(datasetId);
          break;
        case 'stop':
          await timeCraftApi.stopStreaming(datasetId);
          break;
        case 'pause':
          await timeCraftApi.pauseStreaming(datasetId);
          break;
      }
      
      // Refresh datasets to show updated status
      await loadDatasets();
      
      console.log(`${action} streaming for dataset: ${datasetName}`);
    } catch (err) {
      console.error(`Error ${action}ing streaming:`, err);
      setError(`Failed to ${action} streaming for dataset "${datasetName}". Please try again.`);
    } finally {
      setStreamControlDatasets(prev => {
        const newSet = new Set(prev);
        newSet.delete(datasetId);
        return newSet;
      });
    }
  };

  const handleModeUpdate = async (datasetId: string, datasetName: string, newMode: PublishingMode) => {
    try {
      setModeUpdateDatasets(prev => new Set(prev).add(datasetId));
      
      await timeCraftApi.updatePublishingMode(datasetId, { mode: newMode });
      
      // Refresh datasets to show updated status
      await loadDatasets();
      
      console.log(`Updated publishing mode to ${newMode} for dataset: ${datasetName}`);
    } catch (err) {
      console.error('Error updating publishing mode:', err);
      setError(`Failed to update publishing mode for dataset "${datasetName}". Please try again.`);
    } finally {
      setModeUpdateDatasets(prev => {
        const newSet = new Set(prev);
        newSet.delete(datasetId);
        return newSet;
      });
    }
  };

  const handleSpeedChange = async (datasetId: string, datasetName: string, newSpeed: number) => {
    try {
      setStreamControlDatasets(prev => new Set(prev).add(datasetId));
      
      const dataset = datasets.find(d => d.id === datasetId);
      if (!dataset?.streamConfig) return;
      
      const updatedConfig = {
        ...dataset.streamConfig,
        streamSpeed: newSpeed
      };
      
      await timeCraftApi.updatePublishingMode(datasetId, { 
        mode: dataset.streamConfig.mode, 
        streamConfig: updatedConfig 
      });
      
      // Refresh datasets to show updated configuration
      await loadDatasets();
      
      console.log(`Updated stream speed to ${newSpeed}x for dataset: ${datasetName}`);
    } catch (err) {
      console.error('Error updating stream speed:', err);
      setError(`Failed to update stream speed for dataset "${datasetName}". Please try again.`);
    } finally {
      setStreamControlDatasets(prev => {
        const newSet = new Set(prev);
        newSet.delete(datasetId);
        return newSet;
      });
    }
  };

  const handleIntervalChange = async (datasetId: string, datasetName: string, newInterval: number) => {
    try {
      setStreamControlDatasets(prev => new Set(prev).add(datasetId));
      
      const dataset = datasets.find(d => d.id === datasetId);
      if (!dataset?.streamConfig) return;
      
      const updatedConfig = {
        ...dataset.streamConfig,
        streamIntervalMs: newInterval
      };
      
      await timeCraftApi.updatePublishingMode(datasetId, { 
        mode: dataset.streamConfig.mode, 
        streamConfig: updatedConfig 
      });
      
      // Refresh datasets to show updated configuration
      await loadDatasets();
      
      console.log(`Updated stream interval to ${newInterval}ms for dataset: ${datasetName}`);
    } catch (err) {
      console.error('Error updating stream interval:', err);
      setError(`Failed to update stream interval for dataset "${datasetName}". Please try again.`);
    } finally {
      setStreamControlDatasets(prev => {
        const newSet = new Set(prev);
        newSet.delete(datasetId);
        return newSet;
      });
    }
  };

  const toggleDatasetExpansion = (datasetId: string) => {
    setExpandedDatasets(prev => {
      const newSet = new Set(prev);
      if (newSet.has(datasetId)) {
        newSet.delete(datasetId);
      } else {
        newSet.add(datasetId);
      }
      return newSet;
    });
  };

  useEffect(() => {
    loadDatasets();
    
    // Set up auto-refresh for datasets that are in progress or actively streaming
    const interval = setInterval(() => {
      const hasInProgressDatasets = datasetsRef.current.some(d => {
        const statusString = getStatusString(d.status);
        const isInProgress = statusString === 'Pending' || statusString === 'InProgress' || statusString === 'Retrying';
        const isActivelyStreaming = d.streamConfig?.isActive === true;
        return isInProgress || isActivelyStreaming;
      });
      
      if (hasInProgressDatasets) {
        loadDatasets();
      }
    }, 2000); // Refresh every 2 seconds for real-time updates

    return () => clearInterval(interval);
  }, []); // Empty dependency array - only run on mount

  const getStatusColor = (status: string | number) => {
    const statusString = typeof status === 'number' 
      ? ['Pending', 'InProgress', 'Completed', 'Failed', 'Retrying'][status] || 'Unknown'
      : status;
      
    switch (statusString) {
      case 'Completed': return 'text-green-600 bg-green-100';
      case 'Failed': return 'text-red-600 bg-red-100';
      case 'InProgress': return 'text-blue-600 bg-blue-100';
      case 'Pending': return 'text-yellow-600 bg-yellow-100';
      case 'Retrying': return 'text-orange-600 bg-orange-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusString = (status: string | number): string => {
    return typeof status === 'number' 
      ? ['Pending', 'InProgress', 'Completed', 'Failed', 'Retrying'][status] || 'Unknown'
      : status;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const calculateEstimatedTimeRemaining = (dataset: PublishedDataset): string => {
    if (!dataset.streamConfig?.isActive || !dataset.streamConfig.currentStreamPosition) {
      return 'N/A';
    }

    const currentPosition = dataset.streamConfig.currentStreamPosition;
    const totalPoints = dataset.totalDataPoints;
    const remainingPoints = totalPoints - currentPosition;
    
    if (remainingPoints <= 0) {
      return 'Complete';
    }

    const intervalMs = dataset.streamConfig.streamIntervalMs;
    const speed = dataset.streamConfig.streamSpeed;
    
    // Calculate effective interval considering speed multiplier
    const effectiveIntervalMs = intervalMs / speed;
    
    // Estimate remaining time in milliseconds
    const remainingTimeMs = remainingPoints * effectiveIntervalMs;
    
    // Convert to readable format
    const remainingSeconds = Math.round(remainingTimeMs / 1000);
    
    if (remainingSeconds < 60) {
      return `${remainingSeconds}s`;
    } else if (remainingSeconds < 3600) {
      const minutes = Math.floor(remainingSeconds / 60);
      const seconds = remainingSeconds % 60;
      return `${minutes}m ${seconds}s`;
    } else {
      const hours = Math.floor(remainingSeconds / 3600);
      const minutes = Math.floor((remainingSeconds % 3600) / 60);
      return `${hours}h ${minutes}m`;
    }
  };

  const getProgressBarColor = (status: string | number) => {
    const statusString = getStatusString(status);
    switch (statusString) {
      case 'Completed': return 'bg-green-500';
      case 'Failed': return 'bg-red-500';
      case 'InProgress': return 'bg-blue-500';
      case 'Retrying': return 'bg-orange-500';
      default: return 'bg-gray-500';
    }
  };

  const getPublishingModeDisplay = (dataset: PublishedDataset): string => {
    return dataset.streamConfig?.mode || 'Batch';
  };

  const canReIngest = (dataset: PublishedDataset): boolean => {
    const mode = getPublishingModeDisplay(dataset);
    return mode === 'Batch' && getStatusString(dataset.status) === 'Completed';
  };

  const canControlStreaming = (dataset: PublishedDataset): boolean => {
    const mode = getPublishingModeDisplay(dataset);
    return mode === 'Loop' || mode === 'RealTimeStream';
  };

  const isStreamingActive = (dataset: PublishedDataset): boolean => {
    return dataset.streamConfig?.isActive || false;
  };

  const isStreamingPaused = (dataset: PublishedDataset): boolean => {
    // For now, we'll consider it paused if it's not active but the mode supports streaming
    const mode = getPublishingModeDisplay(dataset);
    const supportsStreaming = mode === 'Loop' || mode === 'RealTimeStream';
    return supportsStreaming && !isStreamingActive(dataset);
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading published datasets...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center">
          <h1 className="text-2xl font-bold text-gray-900">Published Datasets</h1>
          {/* Real-time indicator */}
          {datasetsRef.current.some(d => d.streamConfig?.isActive === true) && (
            <div className="ml-3 flex items-center text-sm text-green-600">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-1 animate-pulse"></div>
              Live Updates
            </div>
          )}
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 flex items-center"
        >
          {refreshing ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Refreshing...
            </>
          ) : (
            'Refresh'
          )}
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded">
          {error}
        </div>
      )}

      {datasets.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-lg mb-2">📊</div>
          <p className="text-gray-600 mb-2">No datasets have been published yet.</p>
          <p className="text-sm text-gray-500">
            Generate some time series data and publish it to see it here.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {datasets.map((dataset) => (
            <div key={dataset.id} className="bg-white border rounded-lg p-6 shadow-sm">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900">{dataset.datasetName}</h3>
                  {dataset.description && (
                    <p className="text-gray-600 text-sm mt-1">{dataset.description}</p>
                  )}
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(dataset.status)}`}>
                  {getStatusString(dataset.status)}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-4">
                <div>
                  <p className="text-xs text-gray-500 uppercase font-medium">Event Hub</p>
                  <p className="text-sm text-gray-900">{dataset.eventHubName}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase font-medium">Namespace</p>
                  <p className="text-sm text-gray-900">{dataset.namespaceName}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase font-medium">Data Points</p>
                  <p className="text-sm text-gray-900">
                    {dataset.publishedDataPoints} / {dataset.totalDataPoints}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase font-medium">Tags</p>
                  <p className="text-sm text-gray-900">
                    <span className={`font-semibold ${dataset.publishedTags === dataset.totalTags ? 'text-green-600' : 'text-blue-600'}`}>
                      {dataset.publishedTags}
                    </span>
                    <span className="text-gray-500"> / {dataset.totalTags}</span>
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500 uppercase font-medium">Publishing Mode</p>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm text-gray-900">{getPublishingModeDisplay(dataset)}</span>
                    {canControlStreaming(dataset) && (
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        isStreamingActive(dataset) 
                          ? (isStreamingPaused(dataset) ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800')
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {isStreamingActive(dataset) 
                          ? (isStreamingPaused(dataset) ? 'Paused' : 'Active')
                          : 'Stopped'
                        }
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Stream Configuration Info for streaming modes */}
              {canControlStreaming(dataset) && dataset.streamConfig && (
                <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
                  <h4 className="text-xs font-medium text-blue-800 uppercase mb-2">Stream Configuration</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs mb-3">
                    <div>
                      <span className="text-blue-600">Interval:</span>
                      <span className="ml-1 text-blue-900">{dataset.streamConfig.streamIntervalMs}ms</span>
                    </div>
                    <div>
                      <span className="text-blue-600">Speed:</span>
                      <span className="ml-1 text-blue-900">{dataset.streamConfig.streamSpeed}x</span>
                    </div>
                    {getPublishingModeDisplay(dataset) === 'Loop' && dataset.streamConfig.loopCycles && (
                      <div>
                        <span className="text-blue-600">Cycles:</span>
                        <span className="ml-1 text-blue-900">{dataset.streamConfig.currentCycle} / {dataset.streamConfig.loopCycles}</span>
                      </div>
                    )}
                    {dataset.streamConfig.streamStartTime && (
                      <div>
                        <span className="text-blue-600">Started:</span>
                        <span className="ml-1 text-blue-900">{formatDate(dataset.streamConfig.streamStartTime)}</span>
                      </div>
                    )}
                  </div>

                  {/* Streaming Progress Info */}
                  {isStreamingActive(dataset) && (
                    <div className="mb-3 p-2 bg-green-50 border border-green-200 rounded">
                      <h5 className="text-xs font-medium text-green-800 uppercase mb-1">Live Progress</h5>
                      
                      {/* Progress Bar */}
                      <div className="mb-2">
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-green-700">Streaming Progress</span>
                          <span className="text-green-900 font-semibold">
                            {Math.round(((dataset.streamConfig.currentStreamPosition || 0) / dataset.totalDataPoints) * 100)}%
                          </span>
                        </div>
                        <div className="w-full bg-green-200 rounded-full h-2">
                          <div 
                            className="bg-green-600 h-2 rounded-full transition-all duration-300"
                            style={{ 
                              width: `${Math.max(0, Math.min(100, ((dataset.streamConfig.currentStreamPosition || 0) / dataset.totalDataPoints) * 100))}%` 
                            }}
                          ></div>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                        <div>
                          <span className="text-green-600">Points Sent:</span>
                          <span className="ml-1 text-green-900 font-semibold">
                            {dataset.streamConfig.streamPointsSent || 0}
                          </span>
                        </div>
                        <div>
                          <span className="text-green-600">Position:</span>
                          <span className="ml-1 text-green-900 font-semibold">
                            {dataset.streamConfig.currentStreamPosition || 0} / {dataset.totalDataPoints}
                          </span>
                        </div>
                        <div>
                          <span className="text-green-600">Tags Active:</span>
                          <span className="ml-1 text-green-900 font-semibold">
                            {dataset.publishedTags} / {dataset.totalTags}
                          </span>
                        </div>
                        <div>
                          <span className="text-green-600">ETA:</span>
                          <span className="ml-1 text-green-900 font-semibold">
                            {calculateEstimatedTimeRemaining(dataset)}
                          </span>
                        </div>
                        <div>
                          <span className="text-green-600">Rate:</span>
                          <span className="ml-1 text-green-900 font-semibold">
                            {dataset.streamConfig.streamSpeed}x @ {dataset.streamConfig.streamIntervalMs}ms
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* Speed Control */}
                  <div className="flex items-center space-x-3 mb-2">
                    <label htmlFor={`speed-control-${dataset.id}`} className="text-xs text-blue-700 font-medium">
                      Replay Speed:
                    </label>
                    <input
                      id={`speed-control-${dataset.id}`}
                      type="range"
                      min="0.1"
                      max="10"
                      step="0.1"
                      value={dataset.streamConfig.streamSpeed}
                      onChange={(e) => handleSpeedChange(dataset.id, dataset.datasetName, parseFloat(e.target.value))}
                      disabled={streamControlDatasets.has(dataset.id)}
                      className="flex-1 h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50"
                    />
                    <span className="text-xs text-blue-900 font-mono min-w-[3rem]">
                      {dataset.streamConfig.streamSpeed.toFixed(1)}x
                    </span>
                  </div>
                  
                  {/* Interval Control */}
                  <div className="flex items-center space-x-3">
                    <label htmlFor={`interval-control-${dataset.id}`} className="text-xs text-blue-700 font-medium">
                      Interval (ms):
                    </label>
                    <input
                      id={`interval-control-${dataset.id}`}
                      type="range"
                      min="100"
                      max="5000"
                      step="100"
                      value={dataset.streamConfig.streamIntervalMs}
                      onChange={(e) => handleIntervalChange(dataset.id, dataset.datasetName, parseInt(e.target.value))}
                      disabled={streamControlDatasets.has(dataset.id)}
                      className="flex-1 h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer disabled:opacity-50"
                    />
                    <span className="text-xs text-blue-900 font-mono min-w-[4rem]">
                      {dataset.streamConfig.streamIntervalMs}ms
                    </span>
                  </div>
                </div>
              )}

              {/* Scenario/Prompt Information */}
              {(dataset.originalPrompt || dataset.scenarioParameters) && (
                <div className="mb-4">
                  <button
                    onClick={() => toggleDatasetExpansion(dataset.id)}
                    className="flex items-center text-sm text-gray-600 hover:text-gray-800 transition-colors"
                  >
                    <span className="mr-1">
                      {expandedDatasets.has(dataset.id) ? '▼' : '▶'}
                    </span>
                    View Original Scenario Details
                  </button>
                  
                  {expandedDatasets.has(dataset.id) && (
                    <div className="mt-3 p-4 bg-gray-50 rounded border">
                      {dataset.originalPrompt && (
                        <div className="mb-3">
                          <h4 className="text-xs font-medium text-gray-700 uppercase mb-2">Original Prompt</h4>
                          <p className="text-sm text-gray-900 whitespace-pre-wrap">{dataset.originalPrompt}</p>
                        </div>
                      )}
                      {dataset.scenarioParameters && (
                        <div>
                          <h4 className="text-xs font-medium text-gray-700 uppercase mb-2">Scenario Parameters</h4>
                          <p className="text-sm text-gray-900 whitespace-pre-wrap">{dataset.scenarioParameters}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Progress Bar */}
              {(() => {
                const statusString = getStatusString(dataset.status);
                return (statusString === 'InProgress' || statusString === 'Retrying' || dataset.progressPercentage < 100) ? (
                  <div className="mb-4">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-xs text-gray-600">Publishing Progress</span>
                      <span className="text-xs text-gray-600">{dataset.progressPercentage.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full transition-all duration-300 ${getProgressBarColor(dataset.status)}`}
                        style={{ width: `${dataset.progressPercentage}%` }}
                      ></div>
                    </div>
                  </div>
                ) : null;
              })()}

              <div className="flex justify-between items-center text-xs text-gray-500">
                <div className="space-x-4">
                  <span>Created: {formatDate(dataset.createdAt)}</span>
                  {dataset.publishedAt && (
                    <span>Published: {formatDate(dataset.publishedAt)}</span>
                  )}
                </div>
                {dataset.retryCount > 0 && (
                  <span className="text-orange-600">Retries: {dataset.retryCount}</span>
                )}
              </div>

              {dataset.errorMessage && (
                <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                  <strong>Error:</strong> {dataset.errorMessage}
                </div>
              )}

              {/* Action buttons */}
              <div className="mt-4 flex flex-wrap justify-end gap-2">
                {/* Download CSV button - available for all datasets */}
                <button
                  onClick={() => handleDownloadCsv(dataset.id, dataset.datasetName)}
                  disabled={downloadingDatasets.has(dataset.id)}
                  className="px-3 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                >
                  {downloadingDatasets.has(dataset.id) ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Downloading...
                    </>
                  ) : (
                    <>
                      📥 Download CSV
                    </>
                  )}
                </button>

                {/* Re-ingest button - only for batch mode completed datasets */}
                {canReIngest(dataset) && (
                  <button
                    onClick={() => handleReIngest(dataset.id, dataset.datasetName)}
                    disabled={reIngestingDatasets.has(dataset.id)}
                    className="px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                  >
                    {reIngestingDatasets.has(dataset.id) ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Re-ingesting...
                      </>
                    ) : (
                      <>
                        🔄 Re-ingest
                      </>
                    )}
                  </button>
                )}

                {/* Streaming controls - only for loop and realtime stream modes */}
                {canControlStreaming(dataset) && (
                  <>
                    {!isStreamingActive(dataset) ? (
                      <button
                        onClick={() => handleStreamControl(dataset.id, dataset.datasetName, 'start')}
                        disabled={streamControlDatasets.has(dataset.id)}
                        className="px-3 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                      >
                        {streamControlDatasets.has(dataset.id) ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                            Starting...
                          </>
                        ) : (
                          <>
                            ▶️ Start Stream
                          </>
                        )}
                      </button>
                    ) : (
                      <>
                        {!isStreamingPaused(dataset) ? (
                          <button
                            onClick={() => handleStreamControl(dataset.id, dataset.datasetName, 'pause')}
                            disabled={streamControlDatasets.has(dataset.id)}
                            className="px-3 py-2 bg-yellow-600 text-white text-sm rounded hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                          >
                            {streamControlDatasets.has(dataset.id) ? (
                              <>
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                Pausing...
                              </>
                            ) : (
                              <>
                                ⏸️ Pause
                              </>
                            )}
                          </button>
                        ) : (
                          <button
                            onClick={() => handleStreamControl(dataset.id, dataset.datasetName, 'start')}
                            disabled={streamControlDatasets.has(dataset.id)}
                            className="px-3 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                          >
                            {streamControlDatasets.has(dataset.id) ? (
                              <>
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                                Resuming...
                              </>
                            ) : (
                              <>
                                ▶️ Resume
                              </>
                            )}
                          </button>
                        )}
                        <button
                          onClick={() => handleStreamControl(dataset.id, dataset.datasetName, 'stop')}
                          disabled={streamControlDatasets.has(dataset.id)}
                          className="px-3 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                        >
                          {streamControlDatasets.has(dataset.id) ? (
                            <>
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                              Stopping...
                            </>
                          ) : (
                            <>
                              ⏹️ Stop
                            </>
                          )}
                        </button>
                      </>
                    )}
                  </>
                )}

                {/* Mode switching buttons */}
                <div className="flex items-center space-x-1">
                  <label htmlFor={`mode-select-${dataset.id}`} className="text-xs text-gray-600">Mode:</label>
                  <select
                    id={`mode-select-${dataset.id}`}
                    value={getPublishingModeDisplay(dataset)}
                    onChange={(e) => handleModeUpdate(dataset.id, dataset.datasetName, e.target.value as PublishingMode)}
                    disabled={modeUpdateDatasets.has(dataset.id)}
                    className="px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
                    title="Select publishing mode"
                  >
                    <option value="Batch">Batch</option>
                    <option value="Loop">Loop</option>
                    <option value="RealTimeStream">Real-time Stream</option>
                  </select>
                </div>

                {/* Force Retry button - only for failed datasets */}
                {getStatusString(dataset.status) === 'Failed' && (
                  <button
                    onClick={() => handleForceRetry(dataset.id, dataset.datasetName)}
                    disabled={retryingDatasets.has(dataset.id)}
                    className="px-3 py-2 bg-orange-600 text-white text-sm rounded hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                  >
                    {retryingDatasets.has(dataset.id) ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Retrying...
                      </>
                    ) : (
                      <>
                        🔄 Force Retry
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
