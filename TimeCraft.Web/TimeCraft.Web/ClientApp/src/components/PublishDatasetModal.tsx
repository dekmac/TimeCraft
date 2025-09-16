import React, { useState } from 'react';
import { timeCraftApi } from '../services/timeCraftApi';
import type { 
  TagProgress, 
  PublishDatasetRequest, 
  EventHubConfig, 
  OpcUaSettings, 
  DatasetTag 
} from '../types/api';

interface PublishDatasetModalProps {
  isOpen: boolean;
  onClose: () => void;
  tags: TagProgress[];
  timeHorizon: import('../types/timeHorizon').TimeHorizonOption;
  onPublishSuccess: (publishId: string) => void;
}

export const PublishDatasetModal: React.FC<PublishDatasetModalProps> = ({
  isOpen,
  onClose,
  tags,
  timeHorizon,
  onPublishSuccess
}) => {
  const [datasetName, setDatasetName] = useState('');
  const [description, setDescription] = useState('');
  const [eventHubName, setEventHubName] = useState('');
  const [namespaceName, setNamespaceName] = useState('');
  const [useManagedIdentity, setUseManagedIdentity] = useState(true);
  const [connectionString, setConnectionString] = useState('');
  const [opcUaNamespaceUri, setOpcUaNamespaceUri] = useState('urn:TimeCraft:Industrial');
  const [opcUaApplicationName, setOpcUaApplicationName] = useState('TimeCraft Publisher');
  const [publishingInterval, setPublishingInterval] = useState(1000);
  const [isPublishing, setIsPublishing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const completedTags = tags.filter(tag => 
    tag.status === 'complete' && 
    tag.timeSeriesData && 
    tag.timeSeriesData.data.length > 0
  );

  const handlePublish = async () => {
    setError(null);
    setIsPublishing(true);

    try {
      // Validate form
      if (!datasetName.trim()) {
        throw new Error('Dataset name is required');
      }
      if (!eventHubName.trim()) {
        throw new Error('Event Hub name is required');
      }
      if (!namespaceName.trim()) {
        throw new Error('Namespace name is required');
      }
      if (!useManagedIdentity && !connectionString.trim()) {
        throw new Error('Connection string is required when not using managed identity');
      }
      if (completedTags.length === 0) {
        throw new Error('No completed tags available for publishing');
      }

      // Convert tags to dataset format
      const datasetTags: DatasetTag[] = completedTags.map(tag => ({
        tagName: tag.tag,
        description: tag.description,
        timeSeriesData: tag.timeSeriesData!.data.map((value, index) => ({
          time: tag.timeSeriesData!.timestamps?.[index] || new Date(Date.now() + index * 1000).toISOString(),
          value: value
        })),
        dataType: 'Double',
        unit: 'Units',
        metadata: {
          originalTag: tag.tag,
          generatedAt: new Date().toISOString()
        }
      }));

      const eventHubConfig: EventHubConfig = {
        eventHubName: eventHubName.trim(),
        namespaceName: namespaceName.trim(),
        connectionString: useManagedIdentity ? undefined : connectionString.trim(),
        useManagedIdentity: useManagedIdentity,
        partitionKey: datasetName.toLowerCase().replace(/\s+/g, '-')
      };

      const opcUaSettings: OpcUaSettings = {
        namespaceUri: opcUaNamespaceUri,
        namespaceIndex: 2,
        useDataSetWriterId: true,
        publishingInterval: publishingInterval,
        enableDeltaFrames: true,
        applicationName: opcUaApplicationName,
        applicationUri: `urn:TimeCraft:${opcUaApplicationName.replace(/\s+/g, '')}`
      };

      const publishRequest: PublishDatasetRequest = {
        datasetName: datasetName.trim(),
        description: description.trim(),
        tags: datasetTags,
        eventHubConfig: eventHubConfig,
        opcUaSettings: opcUaSettings,
        metadata: {
          publishedBy: 'TimeCraft Web UI',
          publishedAt: new Date().toISOString(),
          tagCount: datasetTags.length.toString(),
          totalDataPoints: datasetTags.reduce((sum, tag) => sum + tag.timeSeriesData.length, 0).toString()
        }
      };

      console.log('Publishing dataset with request:', publishRequest);
      const response = await timeCraftApi.publishDataset(publishRequest);
      
      onPublishSuccess(response.publishId);
      onClose();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred while publishing';
      setError(errorMessage);
      console.error('Error publishing dataset:', err);
    } finally {
      setIsPublishing(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Publish Dataset to Event Hub</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
              disabled={isPublishing}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
              {error}
            </div>
          )}

          <div className="mb-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="text-lg font-semibold text-blue-800 mb-2">Dataset Summary</h3>
            <p className="text-blue-700">
              <strong>{completedTags.length}</strong> completed tags will be published as OPC UA Delta frames
            </p>
            <div className="mt-2 space-y-1">
              {completedTags.map((tag, index) => (
                <div key={index} className="text-sm text-blue-600">
                  • {tag.tag}: {tag.timeSeriesData?.data.length || 0} data points
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            {/* Dataset Information */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Dataset Name *
              </label>
              <input
                type="text"
                value={datasetName}
                onChange={(e) => setDatasetName(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., Industrial Sensor Data"
                disabled={isPublishing}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                rows={3}
                placeholder="Describe this dataset..."
                disabled={isPublishing}
              />
            </div>

            {/* Event Hub Configuration */}
            <div className="border-t pt-4">
              <h4 className="text-lg font-semibold text-gray-800 mb-3">Event Hub Configuration</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Event Hub Name *
                  </label>
                  <input
                    type="text"
                    value={eventHubName}
                    onChange={(e) => setEventHubName(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="timecraft-events"
                    disabled={isPublishing}
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
                    className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="your-eventhub-namespace"
                    disabled={isPublishing}
                  />
                </div>
              </div>

              <div className="mt-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={useManagedIdentity}
                    onChange={(e) => setUseManagedIdentity(e.target.checked)}
                    className="mr-2"
                    disabled={isPublishing}
                  />
                  <span className="text-sm text-gray-700">Use Managed Identity (recommended)</span>
                </label>
              </div>

              {!useManagedIdentity && (
                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Connection String *
                  </label>
                  <input
                    type="password"
                    value={connectionString}
                    onChange={(e) => setConnectionString(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Endpoint=sb://..."
                    disabled={isPublishing}
                  />
                </div>
              )}
            </div>

            {/* OPC UA Configuration */}
            <div className="border-t pt-4">
              <h4 className="text-lg font-semibold text-gray-800 mb-3">OPC UA Delta Frame Settings</h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Namespace URI
                  </label>
                  <input
                    type="text"
                    value={opcUaNamespaceUri}
                    onChange={(e) => setOpcUaNamespaceUri(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    disabled={isPublishing}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Application Name
                  </label>
                  <input
                    type="text"
                    value={opcUaApplicationName}
                    onChange={(e) => setOpcUaApplicationName(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    disabled={isPublishing}
                  />
                </div>
              </div>

              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Publishing Interval (ms)
                </label>
                <input
                  type="number"
                  value={publishingInterval}
                  onChange={(e) => setPublishingInterval(parseInt(e.target.value) || 1000)}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  min="100"
                  max="10000"
                  disabled={isPublishing}
                />
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-3 mt-6 pt-4 border-t">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-600 border border-gray-300 rounded hover:bg-gray-50"
              disabled={isPublishing}
            >
              Cancel
            </button>
            <button
              onClick={handlePublish}
              className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              disabled={isPublishing || completedTags.length === 0}
            >
              {isPublishing && (
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              )}
              {isPublishing ? 'Publishing...' : 'Publish Dataset'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
