import React, { useState } from 'react';
import { MiniTimeSeriesChart } from './MiniTimeSeriesChart';
import { AnomalyControls } from './AnomalyControls';
import { PublishModal } from './PublishModal';
import { PublishDatasetModal } from './PublishDatasetModal';
import { useAnomaly } from '../hooks/useAnomaly';
import { timeCraftApi } from '../services/timeCraftApi';
import type { GeneratedTag, TagProgress, TagProgressStatus, TimeSeriesData, EventHubConfig, TimeSeriesDataPoint } from '../types/api';

interface TagsDisplayProps {
  tags: GeneratedTag[];
  tagProgress?: TagProgress[];
  dataLength: number;
  onRetryTag?: (tagIndex: number) => void;
  onUpdateTagData?: (tagIndex: number, newData: number[], newTimestamps?: string[]) => void;
}

const getStatusIcon = (status: TagProgressStatus) => {
  switch (status) {
    case 'pending':
      return '⏳';
    case 'generating-tag':
      return '🏷️';
    case 'tag-complete':
      return '✅';
    case 'generating-timeseries':
      return '📊';
    case 'complete':
      return '🎉';
    case 'error':
      return '❌';
    default:
      return '⏳';
  }
};

const getStatusText = (status: TagProgressStatus) => {
  switch (status) {
    case 'pending':
      return 'Pending';
    case 'generating-tag':
      return 'Generating tag...';
    case 'tag-complete':
      return 'Tag ready';
    case 'generating-timeseries':
      return 'Generating time series...';
    case 'complete':
      return 'Complete';
    case 'error':
      return 'Error';
    default:
      return 'Pending';
  }
};

const getStatusColor = (status: TagProgressStatus) => {
  switch (status) {
    case 'pending':
      return 'text-gray-500';
    case 'generating-tag':
      return 'text-blue-500';
    case 'tag-complete':
      return 'text-green-500';
    case 'generating-timeseries':
      return 'text-blue-500';
    case 'complete':
      return 'text-green-600';
    case 'error':
      return 'text-red-500';
    default:
      return 'text-gray-500';
  }
};

export const TagsDisplay: React.FC<TagsDisplayProps> = ({ tags, tagProgress, dataLength, onRetryTag, onUpdateTagData }) => {
  const [publishModalOpen, setPublishModalOpen] = useState(false);
  const [datasetModalOpen, setDatasetModalOpen] = useState(false);
  const [selectedTagForPublish, setSelectedTagForPublish] = useState<{index: number; tag: GeneratedTag; data: TimeSeriesData} | null>(null);
  const [publishLoading, setPublishLoading] = useState(false);
  const [publishError, setPublishError] = useState<string | null>(null);
  const [datasetPublishError, setDatasetPublishError] = useState<string | null>(null);
  const [publishSuccess, setPublishSuccess] = useState<string | null>(null);
  const [datasetPublishSuccess, setDatasetPublishSuccess] = useState<string | null>(null);

  const {
    isGeneratingAnomaly,
    anomalyError,
    selectedInjectionPoints,
    selectInjectionPoint,
    generateAnomaly,
    getAnomalyTypes,
    setAnomalyError
  } = useAnomaly();

  if (tags.length === 0) {
    return null;
  }

  const handlePublishClick = (tagIndex: number, tag: GeneratedTag, progress: TagProgress) => {
    if (progress?.timeSeriesData) {
      setSelectedTagForPublish({
        index: tagIndex,
        tag,
        data: progress.timeSeriesData
      });
      setPublishModalOpen(true);
      setPublishError(null);
      setPublishSuccess(null);
    }
  };

  const handlePublish = async (eventHubConfig: EventHubConfig, datasetName: string, description: string) => {
    if (!selectedTagForPublish) return;

    setPublishLoading(true);
    setPublishError(null);

    try {
      // Convert TimeSeriesData to TimeSeriesDataPoint format
      const timeSeriesData: TimeSeriesDataPoint[] = selectedTagForPublish.data.data.map((value, index) => ({
        value,
        time: selectedTagForPublish.data.timestamps?.[index] || index.toString()
      }));

      const publishRequest = {
        datasetName,
        description: description || `Time series data for ${selectedTagForPublish.tag.tag}`,
        timeSeriesData,
        eventHubConfig,
        metadata: {
          tagName: selectedTagForPublish.tag.tag,
          tagDescription: selectedTagForPublish.tag.description,
          originalDataLength: selectedTagForPublish.data.data.length.toString()
        }
      };

      const response = await timeCraftApi.publishTimeSeries(publishRequest);
      
      setPublishSuccess(`Dataset "${datasetName}" has been queued for publishing. Publish ID: ${response.publishId}`);
      setPublishModalOpen(false);
      setSelectedTagForPublish(null);

    } catch (error) {
      console.error('Error publishing time series:', error);
      setPublishError(error instanceof Error ? error.message : 'Failed to publish time series');
    } finally {
      setPublishLoading(false);
    }
  };

  const handleCloseModal = () => {
    setPublishModalOpen(false);
    setSelectedTagForPublish(null);
    setPublishError(null);
  };

  const handleDatasetPublishClick = () => {
    setDatasetModalOpen(true);
    setDatasetPublishError(null);
    setDatasetPublishSuccess(null);
  };

  const handleDatasetPublishSuccess = (publishId: string) => {
    setDatasetPublishSuccess(`Dataset has been queued for publishing. Publish ID: ${publishId}`);
    setDatasetModalOpen(false);
  };

  const handleCloseDatasetModal = () => {
    setDatasetModalOpen(false);
    setDatasetPublishError(null);
  };

  const handleGenerateAnomaly = async (
    tagIndex: number,
    tagName: string,
    tagDescription: string,
    existingTimeSeries: number[],
    anomalyType: string,
    anomalyDescription: string,
    severity: number
  ) => {
    const result = await generateAnomaly(
      tagIndex,
      tagName,
      tagDescription,
      existingTimeSeries,
      anomalyType,
      anomalyDescription,
      severity
    );
    
    if (result?.success && result.modifiedTimeSeries && onUpdateTagData) {
      // Update the tag progress with the new time series data
      onUpdateTagData(tagIndex, result.modifiedTimeSeries, result.timestamps);
      console.log('Anomaly generated successfully:', result);
    }
  };

  return (
    <div className="glass-effect p-6 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Generated Tags</h3>
        
        {/* Publish All Tags as Dataset Button */}
        {tags.some((_, index) => tagProgress?.[index]?.status === 'complete') && (
          <button
            onClick={handleDatasetPublishClick}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors duration-200 flex items-center"
          >
            📦 Publish All as Dataset
          </button>
        )}
      </div>

      {/* Dataset Publish Success Message */}
      {datasetPublishSuccess && (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded text-sm text-green-700">
          <div className="flex items-center justify-between">
            <span>{datasetPublishSuccess}</span>
            <button
              onClick={() => setDatasetPublishSuccess(null)}
              className="text-green-400 hover:text-green-600"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Dataset Publish Error Display */}
      {datasetPublishError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
          <div className="flex items-center justify-between">
            <span>{datasetPublishError}</span>
            <button
              onClick={() => setDatasetPublishError(null)}
              className="text-red-400 hover:text-red-600"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {tags.map((tag, index) => {
          const progress = tagProgress?.[index];
          const status = progress?.status || 'pending';
          const isLoading = status === 'generating-tag' || status === 'generating-timeseries';
          
          return (
            <div key={index} className={`p-4 bg-white/50 rounded-lg border-l-4 ${
              status === 'complete' ? 'border-green-500' :
              status === 'error' ? 'border-red-500' :
              isLoading ? 'border-blue-500' : 'border-gray-300'
            }`}>
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium text-gray-800">{tag.tag}</h4>
                <div className="flex items-center space-x-2">
                  <span className="text-lg">{getStatusIcon(status)}</span>
                  {isLoading && (
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
                  )}
                </div>
              </div>
              <p className="text-sm text-gray-600 mb-3">{tag.description}</p>
              
              {/* Mini Time Series Chart */}
              {progress?.timeSeriesData && (
                <div className="mb-3">
                  <MiniTimeSeriesChart 
                    data={progress.timeSeriesData.data} 
                    tagName={tag.tag}
                    dataLength={dataLength}
                    selectedInjectionPoint={selectedInjectionPoints.get(index)}
                    isInteractive={status === 'complete'}
                    onPointClick={(pointIndex) => selectInjectionPoint(index, pointIndex)}
                  />
                  <div className="mt-1 text-xs text-gray-500 text-center">
                    Range: {Math.min(...progress.timeSeriesData.data).toFixed(3)} - {Math.max(...progress.timeSeriesData.data).toFixed(3)}
                  </div>
                </div>
              )}

              {/* Anomaly Controls - only show for completed tags */}
              {status === 'complete' && progress?.timeSeriesData && (
                <div className="mb-3">
                  <AnomalyControls
                    tagIndex={index}
                    tagName={tag.tag}
                    tagDescription={tag.description}
                    existingTimeSeries={progress.timeSeriesData.data}
                    selectedInjectionPoint={selectedInjectionPoints.get(index)}
                    isGeneratingAnomaly={isGeneratingAnomaly}
                    anomalyTypes={getAnomalyTypes()}
                    onGenerateAnomaly={handleGenerateAnomaly}
                    onSelectInjectionPoint={selectInjectionPoint}
                  />
                </div>
              )}

              {/* Publish Button - only show for completed tags */}
              {status === 'complete' && progress?.timeSeriesData && (
                <div className="mb-3">
                  <button
                    onClick={() => handlePublishClick(index, tag, progress)}
                    disabled={publishLoading}
                    className="w-full px-3 py-2 bg-green-600 hover:bg-green-700 text-white text-sm rounded transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                  >
                    {publishLoading && selectedTagForPublish?.index === index ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Publishing...
                      </>
                    ) : (
                      <>
                        📤 Publish to Event Hub
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* Success Message */}
              {publishSuccess && (
                <div className="mb-2 p-2 bg-green-50 border border-green-200 rounded text-xs text-green-700">
                  <div className="flex items-center justify-between">
                    <span>{publishSuccess}</span>
                    <button
                      onClick={() => setPublishSuccess(null)}
                      className="text-green-400 hover:text-green-600"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              )}

              {/* Publish Error Display */}
              {publishError && (
                <div className="mb-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
                  <div className="flex items-center justify-between">
                    <span>{publishError}</span>
                    <button
                      onClick={() => setPublishError(null)}
                      className="text-red-400 hover:text-red-600"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              )}

              {/* Error Display */}
              {anomalyError && (
                <div className="mb-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
                  <div className="flex items-center justify-between">
                    <span>{anomalyError}</span>
                    <button
                      onClick={() => setAnomalyError(null)}
                      className="text-red-400 hover:text-red-600"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              )}
              
              <div className="flex items-center justify-between">
                <span className={`text-xs font-medium ${getStatusColor(status)}`}>
                  {getStatusText(status)}
                </span>
                <div className="flex items-center space-x-2">
                  {progress?.error && (
                    <span className="text-xs text-red-500" title={progress.error}>
                      ⚠️
                    </span>
                  )}
                  {status === 'error' && onRetryTag && (
                    <button
                      onClick={() => onRetryTag(index)}
                      className="text-xs bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded transition-colors duration-200"
                      title="Retry generating time series for this tag"
                    >
                      🔄 Retry
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      {/* Publish Modal */}
      <PublishModal
        isOpen={publishModalOpen}
        onClose={handleCloseModal}
        onPublish={handlePublish}
        timeSeriesData={selectedTagForPublish?.data || null}
        isLoading={publishLoading}
      />

      {/* Dataset Publish Modal */}
      <PublishDatasetModal
        isOpen={datasetModalOpen}
        onClose={handleCloseDatasetModal}
        tags={tagProgress || []}
        dataLength={dataLength}
        onPublishSuccess={handleDatasetPublishSuccess}
      />
    </div>
  );
};
