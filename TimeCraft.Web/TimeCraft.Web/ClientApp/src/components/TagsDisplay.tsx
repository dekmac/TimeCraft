import React from 'react';
import { MiniTimeSeriesChart } from './MiniTimeSeriesChart';
import type { GeneratedTag, TagProgress, TagProgressStatus } from '../types/api';

interface TagsDisplayProps {
  tags: GeneratedTag[];
  tagProgress?: TagProgress[];
  dataLength: number;
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

export const TagsDisplay: React.FC<TagsDisplayProps> = ({ tags, tagProgress, dataLength }) => {
  if (tags.length === 0) {
    return null;
  }

  return (
    <div className="glass-effect p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Generated Tags</h3>
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
                  />
                  <div className="mt-1 text-xs text-gray-500 text-center">
                    Range: {Math.min(...progress.timeSeriesData.data).toFixed(3)} - {Math.max(...progress.timeSeriesData.data).toFixed(3)}
                  </div>
                </div>
              )}
              
              <div className="flex items-center justify-between">
                <span className={`text-xs font-medium ${getStatusColor(status)}`}>
                  {getStatusText(status)}
                </span>
                {progress?.error && (
                  <span className="text-xs text-red-500" title={progress.error}>
                    ⚠️
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
