using Azure.Identity;
using Azure.Messaging.EventHubs;
using Azure.Messaging.EventHubs.Producer;
using Microsoft.Extensions.Options;
using System.Text;
using System.Text.Json;
using TimeCraft.Web.Models;
using TimeCraft.Web.Models.Publishing;
using TimeCraft.Web.Services.Interfaces;
using TimeCraft.Web.Settings;

namespace TimeCraft.Web.Services.Implementations;

public class OpcUaDeltaFramePublisher : IOpcUaDeltaFramePublisher
{
    private readonly PublishingSettings _settings;
    private readonly ILogger<OpcUaDeltaFramePublisher> _logger;
    private readonly JsonSerializerOptions _jsonOptions;

    public OpcUaDeltaFramePublisher(IOptions<PublishingSettings> settings, ILogger<OpcUaDeltaFramePublisher> logger)
    {
        _settings = settings.Value;
        _logger = logger;
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = false // Compact for Event Hub
        };
    }

    private DateTime GetDatasetBaselineTimestamp(PublishRecord publishRecord)
    {
        DateTime? earliestTime = null;
        
        foreach (var tag in publishRecord.Tags)
        {
            foreach (var dataPoint in tag.TimeSeriesData)
            {
                if (DateTime.TryParse(dataPoint.Time, out var parsedTime))
                {
                    if (earliestTime == null || parsedTime < earliestTime)
                    {
                        earliestTime = parsedTime;
                    }
                }
            }
        }
        
        return earliestTime ?? DateTime.UtcNow;
    }

    public async Task PublishDatasetAsync(PublishRecord publishRecord, CancellationToken cancellationToken = default)
    {
        if (publishRecord?.EventHubConfig == null || publishRecord.Tags == null)
        {
            throw new ArgumentNullException(nameof(publishRecord));
        }

        EventHubProducerClient? producer = null;
        
        try
        {
            _logger.LogInformation("Starting to publish dataset {DatasetName} with {TagCount} tags using OPC UA Delta frames", 
                publishRecord.DatasetName, publishRecord.Tags.Count);

            // Create the Event Hub producer client
            producer = CreateEventHubProducer(publishRecord.EventHubConfig);

            // Update status to in progress and set publish start time for timestamp calculations
            publishRecord.Status = PublishingStatus.InProgress;
            publishRecord.PublishedAt = DateTime.UtcNow; // Set this early so we can use it as the anchor time
            publishRecord.PublishedDataPoints = 0;

            // Calculate total data points across all tags
            publishRecord.TotalDataPoints = publishRecord.Tags.Sum(tag => tag.TimeSeriesData.Count);

            // Calculate the baseline timestamp from the earliest data point in the entire dataset
            var datasetBaselineTime = GetDatasetBaselineTimestamp(publishRecord);
            
            // Use PublishedAt as the actual start time for the simulation
            var publishStartTime = publishRecord.PublishedAt.Value;

            // Get the maximum number of data points from any tag for synchronization
            var maxDataPoints = publishRecord.Tags.Max(tag => tag.TimeSeriesData.Count);

            // Publish data points in synchronized batches across all tags
            for (int timeIndex = 0; timeIndex < maxDataPoints; timeIndex++)
            {
                cancellationToken.ThrowIfCancellationRequested();

                // Create delta frames for this time index across all tags
                var deltaFrames = new List<OpcUaDeltaFrame>();
                
                foreach (var tag in publishRecord.Tags)
                {
                    if (timeIndex < tag.TimeSeriesData.Count)
                    {
                        var dataPoint = new List<TimeSeriesDataPoint> { tag.TimeSeriesData[timeIndex] };
                        var deltaFrame = CreateDeltaFrame(tag, dataPoint, publishRecord.OpcUaSettings, publishRecord.CurrentSequenceNumber++, datasetBaselineTime, publishStartTime);
                        deltaFrames.Add(deltaFrame);
                    }
                }

                if (deltaFrames.Any())
                {
                    await PublishDeltaFramesAsync(producer, deltaFrames, publishRecord, cancellationToken);
                    publishRecord.PublishedDataPoints += deltaFrames.Count;
                }

                // Add small delay to simulate real-time publishing
                if (publishRecord.OpcUaSettings.PublishingInterval > 0)
                {
                    await Task.Delay(Math.Min(publishRecord.OpcUaSettings.PublishingInterval, 100), cancellationToken);
                }

                // Log progress every 100 data points
                if (timeIndex % 100 == 0)
                {
                    _logger.LogDebug("Published {PublishedPoints}/{TotalPoints} data points for dataset {DatasetName}", 
                        publishRecord.PublishedDataPoints, publishRecord.TotalDataPoints, publishRecord.DatasetName);
                }
            }

            // Mark as completed
            publishRecord.Status = PublishingStatus.Completed;
            publishRecord.ErrorMessage = null;

            _logger.LogInformation("Successfully published dataset {DatasetName} with {TagCount} tags and {DataPointCount} total data points", 
                publishRecord.DatasetName, publishRecord.Tags.Count, publishRecord.PublishedDataPoints);
        }
        catch (OperationCanceledException)
        {
            _logger.LogWarning("Publishing of dataset {DatasetName} was cancelled", publishRecord.DatasetName);
            publishRecord.Status = PublishingStatus.Failed;
            publishRecord.ErrorMessage = "Publishing was cancelled";
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error publishing dataset {DatasetName} to Event Hub {EventHubName}", 
                publishRecord.DatasetName, publishRecord.EventHubConfig.EventHubName);

            publishRecord.Status = PublishingStatus.Failed;
            publishRecord.ErrorMessage = ex.Message;
            throw;
        }
        finally
        {
            if (producer != null)
            {
                await producer.DisposeAsync();
            }
        }
    }

    public OpcUaDeltaFrame CreateDeltaFrame(DatasetTag tag, List<TimeSeriesDataPoint> dataPoints, OpcUaSettings opcUaSettings, int sequenceNumber, 
        DateTime datasetBaselineTime, DateTime publishStartTime)
    {
        var deltaFrame = new OpcUaDeltaFrame
        {
            DataSetWriterId = $"{opcUaSettings.ApplicationName}:{tag.TagName}",
            Timestamp = DateTime.UtcNow,
            SequenceNumber = sequenceNumber
        };

        // Create OPC UA data values for each data point
        foreach (var dataPoint in dataPoints)
        {
            var nodeId = $"ns={opcUaSettings.NamespaceIndex};s={tag.TagName}";
            
            // Calculate the simulated timestamp relative to when publishing started
            DateTime sourceTimestamp;
            if (DateTime.TryParse(dataPoint.Time, out var dataPointTime))
            {
                // Calculate the offset from the dataset baseline
                var offsetFromBaseline = dataPointTime - datasetBaselineTime;
                // Apply that offset to the actual publish start time
                sourceTimestamp = publishStartTime.Add(offsetFromBaseline);
            }
            else
            {
                // Fallback to current time if parsing fails
                sourceTimestamp = DateTime.UtcNow;
            }
            
            var opcUaDataValue = new OpcUaDataValue
            {
                NodeId = nodeId,
                DisplayName = tag.TagName,
                Value = dataPoint.Value,
                SourceTimestamp = sourceTimestamp, // Now calculated relative to publish start time!
                ServerTimestamp = DateTime.UtcNow,
                StatusCode = 0, // Good
                DataType = tag.DataType
            };

            deltaFrame.DataValues.Add(opcUaDataValue);
        }

        // Add metadata
        deltaFrame.MessageMetadata.Add("NamespaceUri", opcUaSettings.NamespaceUri);
        deltaFrame.MessageMetadata.Add("TagDescription", tag.Description);
        deltaFrame.MessageMetadata.Add("Unit", tag.Unit ?? "");
        deltaFrame.MessageMetadata.Add("PublishingInterval", opcUaSettings.PublishingInterval.ToString());

        // Add tag metadata
        foreach (var metadata in tag.Metadata)
        {
            deltaFrame.MessageMetadata.Add($"Tag.{metadata.Key}", metadata.Value);
        }

        return deltaFrame;
    }

    // Interface compatibility method - maintains original signature
    public OpcUaDeltaFrame CreateDeltaFrame(DatasetTag tag, List<TimeSeriesDataPoint> dataPoints, OpcUaSettings opcUaSettings, int sequenceNumber)
    {
        // For backward compatibility with the interface - use current time as baseline
        var datasetBaselineTime = DateTime.UtcNow;
        var publishStartTime = DateTime.UtcNow;
        return CreateDeltaFrame(tag, dataPoints, opcUaSettings, sequenceNumber, datasetBaselineTime, publishStartTime);
    }

    public Task<bool> ValidateOpcUaConfigurationAsync(OpcUaSettings opcUaSettings)
    {
        try
        {
            // Basic validation
            if (string.IsNullOrEmpty(opcUaSettings.NamespaceUri))
            {
                _logger.LogWarning("OPC UA namespace URI is required");
                return Task.FromResult(false);
            }

            if (string.IsNullOrEmpty(opcUaSettings.ApplicationName))
            {
                _logger.LogWarning("OPC UA application name is required");
                return Task.FromResult(false);
            }

            if (opcUaSettings.PublishingInterval < 0)
            {
                _logger.LogWarning("OPC UA publishing interval must be non-negative");
                return Task.FromResult(false);
            }

            _logger.LogDebug("OPC UA configuration is valid");
            return Task.FromResult(true);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error validating OPC UA configuration");
            return Task.FromResult(false);
        }
    }

    private EventHubProducerClient CreateEventHubProducer(EventHubConfig config)
    {
        try
        {
            if (config.UseManagedIdentity)
            {
                var credential = new DefaultAzureCredential();
                var fullyQualifiedNamespace = config.GetFullyQualifiedNamespace();
                
                _logger.LogDebug("Creating Event Hub producer with managed identity for {Namespace}/{EventHub}", 
                    fullyQualifiedNamespace, config.EventHubName);
                
                return new EventHubProducerClient(fullyQualifiedNamespace, config.EventHubName, credential);
            }
            else if (!string.IsNullOrEmpty(config.ConnectionString))
            {
                _logger.LogDebug("Creating Event Hub producer with connection string for Event Hub {EventHub}", 
                    config.EventHubName);
                
                return new EventHubProducerClient(config.ConnectionString, config.EventHubName);
            }
            else
            {
                throw new InvalidOperationException("Either managed identity must be enabled or a connection string must be provided");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating Event Hub producer for {EventHub}", config.EventHubName);
            throw;
        }
    }

    private async Task PublishDeltaFramesAsync(EventHubProducerClient producer, List<OpcUaDeltaFrame> deltaFrames, 
        PublishRecord publishRecord, CancellationToken cancellationToken)
    {
        using var eventBatch = await producer.CreateBatchAsync(cancellationToken);

        foreach (var deltaFrame in deltaFrames)
        {
            var eventData = CreateEventData(deltaFrame, publishRecord);
            
            if (!eventBatch.TryAdd(eventData))
            {
                // If the batch is full, send it and create a new one
                if (eventBatch.Count > 0)
                {
                    await producer.SendAsync(eventBatch, cancellationToken);
                    _logger.LogDebug("Sent OPC UA delta frame batch with {EventCount} events", eventBatch.Count);
                }

                // Create a new batch and add the current event
                using var newBatch = await producer.CreateBatchAsync(cancellationToken);
                if (!newBatch.TryAdd(eventData))
                {
                    throw new InvalidOperationException("OPC UA delta frame is too large to fit in a batch");
                }
                
                await producer.SendAsync(newBatch, cancellationToken);
                return;
            }
        }

        // Send the final batch
        if (eventBatch.Count > 0)
        {
            await producer.SendAsync(eventBatch, cancellationToken);
            _logger.LogDebug("Sent final OPC UA delta frame batch with {EventCount} events", eventBatch.Count);
        }
    }

    private EventData CreateEventData(OpcUaDeltaFrame deltaFrame, PublishRecord publishRecord)
    {
        var eventPayload = new
        {
            MessageType = "OpcUaDeltaFrame",
            DatasetId = publishRecord.Id,
            DatasetName = publishRecord.DatasetName,
            DataSetWriterId = deltaFrame.DataSetWriterId,
            Timestamp = deltaFrame.Timestamp,
            SequenceNumber = deltaFrame.SequenceNumber,
            DataValues = deltaFrame.DataValues,
            MessageMetadata = deltaFrame.MessageMetadata,
            PublishedAt = DateTime.UtcNow
        };

        var jsonPayload = JsonSerializer.Serialize(eventPayload, _jsonOptions);
        var eventData = new EventData(Encoding.UTF8.GetBytes(jsonPayload));

        // Add custom properties for Event Hub routing and filtering
        eventData.Properties.Add("MessageType", "OpcUaDeltaFrame");
        eventData.Properties.Add("DatasetId", publishRecord.Id);
        eventData.Properties.Add("DatasetName", publishRecord.DatasetName);
        eventData.Properties.Add("DataSetWriterId", deltaFrame.DataSetWriterId);
        eventData.Properties.Add("SequenceNumber", deltaFrame.SequenceNumber.ToString());

        // Use partition key if specified
        if (!string.IsNullOrEmpty(publishRecord.EventHubConfig.PartitionKey))
        {
            eventData.Properties.Add("PartitionKey", publishRecord.EventHubConfig.PartitionKey);
        }

        return eventData;
    }
}
