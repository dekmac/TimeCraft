import React, { useState } from 'react';
import type { EventHubConfig, TimeSeriesData } from '../types/api';

interface PublishModalProps {
  isOpen: boolean;
  onClose: () => void;
  onPublish: (config: EventHubConfig, datasetName: string, description: string) => void;
  timeSeriesData: TimeSeriesData | null;
  isLoading: boolean;
}

export const PublishModal: React.FC<PublishModalProps> = ({
  isOpen,
  onClose,
  onPublish,
  timeSeriesData,
  isLoading
}) => {
  const [datasetName, setDatasetName] = useState('');
  const [description, setDescription] = useState('');
  const [eventHubName, setEventHubName] = useState('');
  const [namespaceName, setNamespaceName] = useState('');
  const [useManagedIdentity, setUseManagedIdentity] = useState(true);
  const [connectionString, setConnectionString] = useState('');
  const [partitionKey, setPartitionKey] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const eventHubConfig: EventHubConfig = {
      eventHubName,
      namespaceName,
      useManagedIdentity,
      connectionString: useManagedIdentity ? undefined : connectionString,
      partitionKey: partitionKey || undefined
    };

    onPublish(eventHubConfig, datasetName, description);
  };

  const handleClose = () => {
    // Reset form
    setDatasetName('');
    setDescription('');
    setEventHubName('');
    setNamespaceName('');
    setUseManagedIdentity(true);
    setConnectionString('');
    setPartitionKey('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Publish to Event Hub</h2>
          <button
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
            disabled={isLoading}
          >
            ×
          </button>
        </div>

        {timeSeriesData && (
          <div className="mb-4 p-3 bg-gray-50 rounded">
            <p className="text-sm text-gray-600">
              Publishing <strong>{timeSeriesData.name}</strong> with {timeSeriesData.data.length} data points
            </p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Dataset Information */}
          <div className="border-b pb-4">
            <h3 className="font-medium mb-3">Dataset Information</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Dataset Name *
              </label>
              <input
                type="text"
                value={datasetName}
                onChange={(e) => setDatasetName(e.target.value)}
                required
                disabled={isLoading}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter a name for this dataset"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={isLoading}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Optional description for this dataset"
              />
            </div>
          </div>

          {/* Event Hub Configuration */}
          <div className="border-b pb-4">
            <h3 className="font-medium mb-3">Event Hub Configuration</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Event Hub Name *
                </label>
                <input
                  type="text"
                  value={eventHubName}
                  onChange={(e) => setEventHubName(e.target.value)}
                  required
                  disabled={isLoading}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="my-eventhub"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Namespace Name *
                </label>
                <input
                  type="text"
                  value={namespaceName}
                  onChange={(e) => setNamespaceName(e.target.value)}
                  required
                  disabled={isLoading}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="my-namespace (without .servicebus.windows.net)"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Partition Key (Optional)
              </label>
              <input
                type="text"
                value={partitionKey}
                onChange={(e) => setPartitionKey(e.target.value)}
                disabled={isLoading}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Optional partition key for event routing"
              />
            </div>
          </div>

          {/* Authentication */}
          <div>
            <h3 className="font-medium mb-3">Authentication</h3>
            
            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="radio"
                  checked={useManagedIdentity}
                  onChange={() => setUseManagedIdentity(true)}
                  disabled={isLoading}
                  className="mr-2"
                />
                <span className="text-sm">Use Managed Identity (Recommended)</span>
              </label>

              <label className="flex items-center">
                <input
                  type="radio"
                  checked={!useManagedIdentity}
                  onChange={() => setUseManagedIdentity(false)}
                  disabled={isLoading}
                  className="mr-2"
                />
                <span className="text-sm">Use Connection String</span>
              </label>

              {!useManagedIdentity && (
                <div className="ml-6">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Connection String *
                  </label>
                  <textarea
                    value={connectionString}
                    onChange={(e) => setConnectionString(e.target.value)}
                    required={!useManagedIdentity}
                    disabled={isLoading}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Endpoint=sb://..."
                  />
                </div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={handleClose}
              disabled={isLoading}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !datasetName || !eventHubName || !namespaceName || (!useManagedIdentity && !connectionString)}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Publishing...' : 'Publish to Event Hub'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
