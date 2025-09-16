using Azure.Identity;
using Azure.Messaging.EventHubs;
using Azure.Messaging.EventHubs.Producer;
using Microsoft.Extensions.Options;
using System.Text;
using System.Text.Json;
using TimeCraft.Web.Models.Publishing;
using TimeCraft.Web.Services.Interfaces;
using TimeCraft.Web.Settings;

namespace TimeCraft.Web.Services.Implementations;

public class EventHubPublisher : IEventHubPublisher
{
    private readonly PublishingSettings _settings;
    private readonly ILogger<EventHubPublisher> _logger;
    private readonly JsonSerializerOptions _jsonOptions;

    public EventHubPublisher(IOptions<PublishingSettings> settings, ILogger<EventHubPublisher> logger)
    {
        _settings = settings.Value;
        _logger = logger;
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };
    }

    public async Task PublishAsync(PublishRecord publishRecord, CancellationToken cancellationToken = default)
    {
        if (publishRecord?.EventHubConfig == null)
        {
            throw new ArgumentNullException(nameof(publishRecord));
        }

        EventHubProducerClient? producer = null;
        
        try
        {
            _logger.LogInformation("Starting to publish dataset {DatasetName} to Event Hub {EventHubName}", 
                publishRecord.DatasetName, publishRecord.EventHubConfig.EventHubName);

            // Create the Event Hub producer client
            producer = CreateEventHubProducer(publishRecord.EventHubConfig);

            // Update status to in progress and set publish start time for timestamp calculations
            publishRecord.Status = PublishingStatus.InProgress;
            publishRecord.PublishedAt = DateTime.UtcNow; // Set this early so we can use it as the anchor time
            publishRecord.PublishedDataPoints = 0;

            // Calculate total data points across all tags
            publishRecord.TotalDataPoints = publishRecord.Tags.Sum(tag => tag.TimeSeriesData.Count);

            var batchSize = 100; // Process in batches to avoid memory issues
            var totalBatches = (int)Math.Ceiling((double)publishRecord.TotalDataPoints / batchSize);

            // Process all time series data from all tags
            var allDataPoints = new List<(string TagName, Models.TimeSeriesDataPoint DataPoint)>();
            foreach (var tag in publishRecord.Tags)
            {
                foreach (var dataPoint in tag.TimeSeriesData)
                {
                    allDataPoints.Add((tag.TagName, dataPoint));
                }
            }

            for (int batchIndex = 0; batchIndex < totalBatches; batchIndex++)
            {
                cancellationToken.ThrowIfCancellationRequested();

                var batch = allDataPoints
                    .Skip(batchIndex * batchSize)
                    .Take(batchSize)
                    .ToList();

                await PublishBatchAsync(producer, batch, publishRecord, cancellationToken);

                publishRecord.PublishedDataPoints += batch.Count;
                
                _logger.LogDebug("Published batch {BatchIndex}/{TotalBatches} for dataset {DatasetName}", 
                    batchIndex + 1, totalBatches, publishRecord.DatasetName);
            }

            // Mark as completed  
            publishRecord.Status = PublishingStatus.Completed;
            publishRecord.ErrorMessage = null;

            _logger.LogInformation("Successfully published dataset {DatasetName} with {DataPointCount} data points", 
                publishRecord.DatasetName, publishRecord.PublishedDataPoints);
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

    private async Task PublishBatchAsync(EventHubProducerClient producer, List<(string TagName, Models.TimeSeriesDataPoint DataPoint)> taggedDataPoints, 
        PublishRecord publishRecord, CancellationToken cancellationToken)
    {
        using var eventBatch = await producer.CreateBatchAsync(cancellationToken);

        // Calculate the baseline timestamp from the earliest data point in the entire dataset
        var datasetBaselineTime = GetDatasetBaselineTimestamp(publishRecord);
        
        // Use PublishedAt as the actual start time for the simulation
        var publishStartTime = publishRecord.PublishedAt ?? DateTime.UtcNow;

        foreach (var (tagName, dataPoint) in taggedDataPoints)
        {
            var eventData = CreateEventData(tagName, dataPoint, publishRecord, datasetBaselineTime, publishStartTime);
            
            if (!eventBatch.TryAdd(eventData))
            {
                // If the batch is full, send it and create a new one
                if (eventBatch.Count > 0)
                {
                    await producer.SendAsync(eventBatch, cancellationToken);
                    _logger.LogDebug("Sent batch with {EventCount} events", eventBatch.Count);
                }

                // Create a new batch and add the current event
                using var newBatch = await producer.CreateBatchAsync(cancellationToken);
                if (!newBatch.TryAdd(eventData))
                {
                    throw new InvalidOperationException("Event is too large to fit in a batch");
                }
                
                await producer.SendAsync(newBatch, cancellationToken);
                return;
            }
        }

        // Send the final batch
        if (eventBatch.Count > 0)
        {
            await producer.SendAsync(eventBatch, cancellationToken);
            _logger.LogDebug("Sent final batch with {EventCount} events", eventBatch.Count);
        }
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

    private EventData CreateEventData(string tagName, Models.TimeSeriesDataPoint dataPoint, PublishRecord publishRecord, 
        DateTime datasetBaselineTime, DateTime publishStartTime)
    {
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
        
        var eventPayload = new
        {
            DatasetId = publishRecord.Id,
            DatasetName = publishRecord.DatasetName,
            Description = publishRecord.Description,
            TagName = tagName,
            Time = dataPoint.Time,
            Value = dataPoint.Value,
            SourceTimestamp = sourceTimestamp, // This is the key field you mentioned!
            PublishedAt = DateTime.UtcNow, // Keep the actual publish time for reference
            Metadata = publishRecord.Metadata
        };

        var jsonPayload = JsonSerializer.Serialize(eventPayload, _jsonOptions);
        var eventData = new EventData(Encoding.UTF8.GetBytes(jsonPayload));

        // Add custom properties
        eventData.Properties.Add("DatasetId", publishRecord.Id);
        eventData.Properties.Add("DatasetName", publishRecord.DatasetName);
        eventData.Properties.Add("EventType", "TimeSeriesDataPoint");

        // Use partition key if specified
        if (!string.IsNullOrEmpty(publishRecord.EventHubConfig.PartitionKey))
        {
            eventData.Properties.Add("PartitionKey", publishRecord.EventHubConfig.PartitionKey);
        }

        return eventData;
    }
}
