import React, { useState, useEffect } from 'react';
import ExportCsvButton from './ExportCsvButton';

interface Dataset {
  id: string;
  datasetName: string;
  description: string;
  status: string;
  createdAt: string;
  totalDataPoints: number;
  tags?: Array<{ tagName: string }>;
}

const DatasetExportExample: React.FC = () => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/publishing/datasets');
      
      if (!response.ok) {
        throw new Error('Failed to fetch datasets');
      }
      
      const data = await response.json();
      setDatasets(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading datasets...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 className="text-red-800 font-medium">Error Loading Datasets</h3>
        <p className="text-red-600 text-sm mt-1">{error}</p>
        <button
          onClick={fetchDatasets}
          className="mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  if (datasets.length === 0) {
    return (
      <div className="text-center py-8">
        <h3 className="text-gray-600 font-medium">No Published Datasets</h3>
        <p className="text-gray-500 text-sm mt-1">
          Publish a dataset first to see CSV export options.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">Published Datasets</h2>
        <button
          onClick={fetchDatasets}
          className="px-3 py-1 text-sm text-blue-600 hover:text-blue-800"
        >
          Refresh
        </button>
      </div>

      <div className="grid gap-4">
        {datasets.map((dataset) => (
          <div key={dataset.id} className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
            {/* Dataset Header */}
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-medium text-gray-900">{dataset.datasetName}</h3>
                <p className="text-gray-600 text-sm mt-1">{dataset.description}</p>
              </div>
              <span className={`
                px-2 py-1 rounded-full text-xs font-medium
                ${dataset.status === 'Completed' 
                  ? 'bg-green-100 text-green-800' 
                  : dataset.status === 'InProgress'
                  ? 'bg-blue-100 text-blue-800'
                  : dataset.status === 'Failed'
                  ? 'bg-red-100 text-red-800'
                  : 'bg-gray-100 text-gray-800'
                }
              `}>
                {dataset.status}
              </span>
            </div>

            {/* Dataset Info */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
              <div>
                <span className="text-gray-500">Created:</span>
                <div className="font-medium">
                  {new Date(dataset.createdAt).toLocaleDateString()}
                </div>
              </div>
              <div>
                <span className="text-gray-500">Data Points:</span>
                <div className="font-medium">{dataset.totalDataPoints.toLocaleString()}</div>
              </div>
              <div>
                <span className="text-gray-500">Tags:</span>
                <div className="font-medium">{dataset.tags?.length || 0}</div>
              </div>
              <div>
                <span className="text-gray-500">Dataset ID:</span>
                <div className="font-mono text-xs break-all">{dataset.id}</div>
              </div>
            </div>

            {/* Tags Preview */}
            {dataset.tags && dataset.tags.length > 0 && (
              <div className="mb-4">
                <span className="text-gray-500 text-sm">Available Tags:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {dataset.tags.slice(0, 5).map((tag) => (
                    <span
                      key={tag.tagName}
                      className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                    >
                      {tag.tagName}
                    </span>
                  ))}
                  {dataset.tags.length > 5 && (
                    <span className="px-2 py-1 bg-gray-100 text-gray-500 rounded text-xs">
                      +{dataset.tags.length - 5} more
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Export Button */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-100">
              <div className="text-sm text-gray-500">
                Export OPC UA delta frames as CSV with configurable timestamps and filtering
              </div>
              <ExportCsvButton
                datasetId={dataset.id}
                datasetName={dataset.datasetName}
                availableTags={dataset.tags?.map(tag => tag.tagName) || []}
                className="ml-4"
              />
            </div>
          </div>
        ))}
      </div>

      {/* Info Section */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
        <h4 className="text-blue-800 font-medium mb-2">CSV Export Features</h4>
        <ul className="text-blue-700 text-sm space-y-1">
          <li>• Export with relative timestamps (seconds from reference time) or absolute timestamps</li>
          <li>• Filter by specific tags to export only the data you need</li>
          <li>• Set custom time ranges to export data from specific periods</li>
          <li>• Includes full OPC UA delta frame information (NodeId, StatusCode, SequenceNumber, etc.)</li>
          <li>• Files are automatically named with dataset name and timestamp</li>
        </ul>
      </div>
    </div>
  );
};

export default DatasetExportExample;