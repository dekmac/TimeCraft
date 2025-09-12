import React, { useState, useEffect } from 'react';
import { timeCraftApi } from '../services/timeCraftApi';
import type { PublishedDataset } from '../types/api';

export const PublishedDatasets: React.FC = () => {
  const [datasets, setDatasets] = useState<PublishedDataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadDatasets = async () => {
    try {
      setError(null);
      const data = await timeCraftApi.getPublishedDatasets();
      setDatasets(data);
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

  useEffect(() => {
    loadDatasets();
    
    // Set up auto-refresh for datasets that are in progress
    const interval = setInterval(() => {
      const hasInProgressDatasets = datasets.some(d => 
        d.status === 'Pending' || d.status === 'InProgress' || d.status === 'Retrying'
      );
      
      if (hasInProgressDatasets) {
        loadDatasets();
      }
    }, 5000); // Refresh every 5 seconds

    return () => clearInterval(interval);
  }, [datasets]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Completed': return 'text-green-600 bg-green-100';
      case 'Failed': return 'text-red-600 bg-red-100';
      case 'InProgress': return 'text-blue-600 bg-blue-100';
      case 'Pending': return 'text-yellow-600 bg-yellow-100';
      case 'Retrying': return 'text-orange-600 bg-orange-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getProgressBarColor = (status: string) => {
    switch (status) {
      case 'Completed': return 'bg-green-500';
      case 'Failed': return 'bg-red-500';
      case 'InProgress': return 'bg-blue-500';
      case 'Retrying': return 'bg-orange-500';
      default: return 'bg-gray-500';
    }
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
        <h1 className="text-2xl font-bold text-gray-900">Published Datasets</h1>
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
                  {dataset.status}
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
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
              </div>

              {/* Progress Bar */}
              {dataset.status === 'InProgress' || dataset.status === 'Retrying' || dataset.progressPercentage < 100 ? (
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
              ) : null}

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
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
