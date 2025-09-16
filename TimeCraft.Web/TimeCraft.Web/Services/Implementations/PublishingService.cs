using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Options;
using TimeCraft.Web.Models.Publishing;
using TimeCraft.Web.Services.Interfaces;
using TimeCraft.Web.Settings;

namespace TimeCraft.Web.Services.Implementations;

public class PublishingService : IPublishingService
{
    private readonly PublishingSettings _settings;
    private readonly ILogger<PublishingService> _logger;
    private readonly string _storageDirectory;
    private readonly JsonSerializerOptions _jsonOptions;

    public PublishingService(IOptions<PublishingSettings> settings, ILogger<PublishingService> logger)
    {
        _settings = settings.Value;
        _logger = logger;
        _storageDirectory = Path.GetFullPath(_settings.StorageDirectory);
        
        // Ensure storage directory exists
        Directory.CreateDirectory(_storageDirectory);
        
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            WriteIndented = true
        };
    }

    public async Task<string> CreatePublishRecordAsync(PublishRecord publishRecord)
    {
        try
        {
            if (publishRecord == null)
            {
                throw new ArgumentNullException(nameof(publishRecord));
            }

            publishRecord.Id = Guid.NewGuid().ToString();
            publishRecord.CreatedAt = DateTime.UtcNow;
            publishRecord.Status = PublishingStatus.Pending;
            publishRecord.TotalDataPoints = publishRecord.Tags.Sum(tag => tag.TimeSeriesData.Count);

            var filePath = GetRecordFilePath(publishRecord.Id);
            var json = JsonSerializer.Serialize(publishRecord, _jsonOptions);
            
            await File.WriteAllTextAsync(filePath, json);
            
            _logger.LogInformation("Created publish record {PublishId} for dataset {DatasetName}", 
                publishRecord.Id, publishRecord.DatasetName);
            
            return publishRecord.Id;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating publish record for dataset {DatasetName}", 
                publishRecord?.DatasetName);
            throw;
        }
    }

    public async Task<PublishedDataset?> GetPublishedDatasetAsync(string id)
    {
        try
        {
            var publishRecord = await GetPublishRecordAsync(id);
            
            return publishRecord != null ? MapToPublishedDataset(publishRecord) : null;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting published dataset {Id}", id);
            return null;
        }
    }

    public async Task<DatasetContent?> GetDatasetContentAsync(string id)
    {
        try
        {
            var publishRecord = await GetPublishRecordAsync(id);
            
            return publishRecord != null ? MapToDatasetContent(publishRecord) : null;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting dataset content {Id}", id);
            return null;
        }
    }

    public async Task<List<PublishedDataset>> GetAllPublishedDatasetsAsync()
    {
        try
        {
            var publishRecords = await GetAllPublishRecordsAsync();
            
            return publishRecords.Select(MapToPublishedDataset).ToList();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting all published datasets");
            return new List<PublishedDataset>();
        }
    }

    public async Task UpdatePublishRecordAsync(PublishRecord publishRecord)
    {
        try
        {
            if (publishRecord == null)
            {
                throw new ArgumentNullException(nameof(publishRecord));
            }

            var filePath = GetRecordFilePath(publishRecord.Id);
            var json = JsonSerializer.Serialize(publishRecord, _jsonOptions);
            
            await File.WriteAllTextAsync(filePath, json);
            
            _logger.LogDebug("Updated publish record {PublishId}", publishRecord.Id);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating publish record {PublishId}", publishRecord?.Id);
            throw;
        }
    }

    public async Task<bool> UpdateStreamingProgressAsync(Guid id, int pointsSent, int currentPosition)
    {
        try
        {
            var record = await GetPublishRecordAsync(id.ToString());
            if (record?.StreamConfig == null) return false;

            record.StreamConfig.StreamPointsSent = pointsSent;
            record.StreamConfig.CurrentStreamPosition = currentPosition;

            await UpdatePublishRecordAsync(record);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update streaming progress for {Id}", id);
            return false;
        }
    }

    public async Task<bool> UpdateStreamingStatsAsync(Guid id, bool isActive, int? cycleCount = null)
    {
        try
        {
            var record = await GetPublishRecordAsync(id.ToString());
            if (record?.StreamConfig == null) return false;

            var wasActive = record.StreamConfig.IsActive;
            record.StreamConfig.IsActive = isActive;

            // Track timing
            if (isActive && !wasActive)
            {
                // Starting/resuming
                record.StreamConfig.PausedAt = null;
            }
            else if (!isActive && wasActive)
            {
                // Pausing
                record.StreamConfig.PausedAt = DateTime.UtcNow;
            }

            if (cycleCount.HasValue)
            {
                record.StreamConfig.CurrentCycle = cycleCount.Value;
            }

            await UpdatePublishRecordAsync(record);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to update streaming stats for {Id}", id);
            return false;
        }
    }

    public async Task<PublishRecord?> GetPublishRecordAsync(string id)
    {
        try
        {
            var filePath = GetRecordFilePath(id);
            
            if (!File.Exists(filePath))
            {
                return null;
            }

            var json = await File.ReadAllTextAsync(filePath);
            var publishRecord = JsonSerializer.Deserialize<PublishRecord>(json, _jsonOptions);
            
            return publishRecord;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting publish record {Id}", id);
            return null;
        }
    }

    public async Task<List<PublishRecord>> GetPendingPublishRecordsAsync()
    {
        try
        {
            var allRecords = await GetAllPublishRecordsAsync();
            
            return allRecords
                .Where(r => r.Status == PublishingStatus.Pending || r.Status == PublishingStatus.Retrying)
                .ToList();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting pending publish records");
            return new List<PublishRecord>();
        }
    }

    public async Task<bool> ForceRetryDatasetAsync(string id)
    {
        try
        {
            var publishRecord = await GetPublishRecordAsync(id);
            
            if (publishRecord == null)
            {
                _logger.LogWarning("Publish record {Id} not found for force retry", id);
                return false;
            }

            // Reset the publish record for retry
            publishRecord.Status = PublishingStatus.Pending;
            publishRecord.RetryCount = 0;
            publishRecord.ErrorMessage = null;
            publishRecord.PublishedDataPoints = 0;
            publishRecord.CurrentSequenceNumber = 1;
            publishRecord.PublishedAt = null;

            // Save the updated record
            await UpdatePublishRecordAsync(publishRecord);

            _logger.LogInformation("Force retry initiated for dataset {DatasetName} (ID: {Id})", 
                publishRecord.DatasetName, id);

            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error forcing retry for dataset {Id}", id);
            return false;
        }
    }

    public async Task<List<PublishRecord>> GetAllPublishRecordsAsync()
    {
        var records = new List<PublishRecord>();
        
        if (!Directory.Exists(_storageDirectory))
        {
            return records;
        }

        var files = Directory.GetFiles(_storageDirectory, "*.json");
        
        foreach (var file in files)
        {
            try
            {
                var json = await File.ReadAllTextAsync(file);
                var record = JsonSerializer.Deserialize<PublishRecord>(json, _jsonOptions);
                
                if (record != null)
                {
                    records.Add(record);
                }
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Error reading publish record file {File}", file);
            }
        }
        
        return records.OrderByDescending(r => r.CreatedAt).ToList();
    }

    private string GetRecordFilePath(string id)
    {
        return Path.Combine(_storageDirectory, $"{id}.json");
    }

    private static PublishedDataset MapToPublishedDataset(PublishRecord record)
    {
        return new PublishedDataset
        {
            Id = record.Id,
            DatasetName = record.DatasetName,
            Description = record.Description,
            OriginalPrompt = record.OriginalPrompt,
            ScenarioParameters = record.ScenarioParameters,
            StreamConfig = record.StreamConfig ?? new StreamConfiguration
            {
                Mode = PublishingMode.Batch,
                StreamIntervalMs = 1000,
                StreamSpeed = 1.0,
                LoopCycles = 1,
                LoopPauseMs = 0,
                IsActive = false,
                CurrentCycle = 0,
                ReIngestionCount = 0
            },
            Status = record.Status,
            CreatedAt = record.CreatedAt,
            PublishedAt = record.PublishedAt,
            EventHubName = record.EventHubConfig.EventHubName,
            NamespaceName = record.EventHubConfig.NamespaceName,
            TotalDataPoints = record.TotalDataPoints,
            PublishedDataPoints = record.PublishedDataPoints,
            TotalTags = record.Tags.Count,
            PublishedTags = record.Status == PublishingStatus.Completed ? record.Tags.Count : 0, // For now, tags are either all published or none
            ErrorMessage = record.ErrorMessage,
            RetryCount = record.RetryCount
        };
    }

    private static DatasetContent MapToDatasetContent(PublishRecord record)
    {
        return new DatasetContent
        {
            Id = record.Id,
            DatasetName = record.DatasetName,
            Description = record.Description,
            OriginalPrompt = record.OriginalPrompt,
            ScenarioParameters = record.ScenarioParameters,
            Tags = record.Tags,
            Status = record.Status,
            CreatedAt = record.CreatedAt,
            PublishedAt = record.PublishedAt,
            TotalTags = record.Tags.Count,
            TotalDataPoints = record.TotalDataPoints
        };
    }

    public async Task<ExportDeltaFramesCsvResponse> ExportDeltaFramesCsvAsync(ExportDeltaFramesCsvRequest request)
    {
        try
        {
            if (string.IsNullOrEmpty(request.DatasetId))
            {
                throw new ArgumentException("Dataset ID is required", nameof(request));
            }

            var publishRecord = await GetPublishRecordAsync(request.DatasetId);
            if (publishRecord == null)
            {
                throw new InvalidOperationException($"Dataset with ID {request.DatasetId} not found");
            }

            if (publishRecord.Tags == null || !publishRecord.Tags.Any())
            {
                throw new InvalidOperationException("No tags found in the dataset");
            }

            // Filter tags if specified
            var tagsToExport = request.TagFilter != null && request.TagFilter.Any()
                ? publishRecord.Tags.Where(tag => request.TagFilter.Contains(tag.TagName)).ToList()
                : publishRecord.Tags;

            if (!tagsToExport.Any())
            {
                throw new InvalidOperationException("No matching tags found for export");
            }

            // Set reference time for relative timestamps
            var referenceTime = request.ReferenceTime ?? DateTime.UtcNow;

            // Generate CSV content
            var csvContent = GenerateDeltaFramesCsv(tagsToExport, publishRecord, request, referenceTime);
            var fileContent = System.Text.Encoding.UTF8.GetBytes(csvContent);

            // Generate filename with timestamp
            var timestamp = DateTime.UtcNow.ToString("yyyyMMdd_HHmmss");
            var fileName = $"opcua_deltaframes_{publishRecord.DatasetName}_{timestamp}.csv";

            var totalRecords = tagsToExport.Sum(tag => tag.TimeSeriesData.Count);

            return new ExportDeltaFramesCsvResponse
            {
                FileName = fileName,
                FileContent = fileContent,
                ContentType = "text/csv",
                TotalRecords = totalRecords,
                Message = $"Successfully exported {totalRecords} OPC UA delta frames for dataset '{publishRecord.DatasetName}'"
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error exporting delta frames CSV for dataset {DatasetId}", request.DatasetId);
            throw;
        }
    }

    private string GenerateDeltaFramesCsv(List<DatasetTag> tags, PublishRecord publishRecord, ExportDeltaFramesCsvRequest request, DateTime referenceTime)
    {
        var csv = new System.Text.StringBuilder();

        // Write CSV header
        if (request.UseRelativeTimestamps)
        {
            csv.AppendLine("RelativeTimeSeconds,OriginalTimestamp,TagName,NodeId,DisplayName,Value,DataType,StatusCode,SequenceNumber,DataSetWriterId");
        }
        else
        {
            csv.AppendLine("Timestamp,TagName,NodeId,DisplayName,Value,DataType,StatusCode,SequenceNumber,DataSetWriterId");
        }

        int sequenceNumber = 1;

        // Process each tag and its time series data
        foreach (var tag in tags)
        {
            if (tag.TimeSeriesData == null) continue;

            for (int i = 0; i < tag.TimeSeriesData.Count; i++)
            {
                var dataPoint = tag.TimeSeriesData[i];
                
                // Generate timestamp based on index (since TimeSeriesDataPoint.Time might be a string identifier)
                // Use the creation time of the dataset plus interval for each data point
                var intervalMinutes = 5; // Default 5-minute intervals, can be configurable
                var dataPointTimestamp = publishRecord.CreatedAt.AddMinutes(i * intervalMinutes);

                // Apply time filtering if specified
                if (request.StartTime.HasValue && dataPointTimestamp < request.StartTime.Value)
                    continue;
                if (request.EndTime.HasValue && dataPointTimestamp > request.EndTime.Value)
                    continue;

                // Create simulated OPC UA delta frame data
                var nodeId = $"ns=2;s={tag.TagName}";
                var displayName = tag.TagName;
                var value = dataPoint.Value;
                var dataType = GetDataType(value);
                var statusCode = 0; // Good status
                var dataSetWriterId = $"{publishRecord.DatasetName}_{tag.TagName}";

                if (request.UseRelativeTimestamps)
                {
                    var relativeSeconds = (dataPointTimestamp - referenceTime).TotalSeconds;
                    csv.AppendLine($"{relativeSeconds:F3},{dataPointTimestamp:yyyy-MM-dd HH:mm:ss.fff},{EscapeCsvValue(tag.TagName)},{EscapeCsvValue(nodeId)},{EscapeCsvValue(displayName)},{value},{EscapeCsvValue(dataType)},{statusCode},{sequenceNumber},{EscapeCsvValue(dataSetWriterId)}");
                }
                else
                {
                    csv.AppendLine($"{dataPointTimestamp:yyyy-MM-dd HH:mm:ss.fff},{EscapeCsvValue(tag.TagName)},{EscapeCsvValue(nodeId)},{EscapeCsvValue(displayName)},{value},{EscapeCsvValue(dataType)},{statusCode},{sequenceNumber},{EscapeCsvValue(dataSetWriterId)}");
                }

                sequenceNumber++;
            }
        }

        return csv.ToString();
    }

    private static string GetDataType(object? value)
    {
        return value switch
        {
            double => "Double",
            float => "Float",
            int => "Int32",
            long => "Int64",
            bool => "Boolean",
            string => "String",
            _ => "Variant"
        };
    }

    private static string EscapeCsvValue(string? value)
    {
        if (string.IsNullOrEmpty(value))
            return string.Empty;

        // Escape CSV values that contain commas, quotes, or newlines
        if (value.Contains(',') || value.Contains('"') || value.Contains('\n') || value.Contains('\r'))
        {
            return $"\"{value.Replace("\"", "\"\"")}\"";
        }

        return value;
    }

    public async Task<byte[]> DownloadDatasetCsvAsync(string id)
    {
        try
        {
            var publishRecord = await GetPublishRecordAsync(id);
            if (publishRecord == null)
            {
                throw new FileNotFoundException($"Dataset with ID {id} not found");
            }

            var csv = new StringBuilder();
            
            // Add CSV header
            csv.AppendLine("TagName,Description,Time,Value,DataType,Unit");

            // Add data for each tag
            foreach (var tag in publishRecord.Tags)
            {
                foreach (var dataPoint in tag.TimeSeriesData)
                {
                    csv.AppendLine($"{EscapeCsvValue(tag.TagName)}," +
                                 $"{EscapeCsvValue(tag.Description)}," +
                                 $"{EscapeCsvValue(dataPoint.Time)}," +
                                 $"{dataPoint.Value}," +
                                 $"{EscapeCsvValue(tag.DataType)}," +
                                 $"{EscapeCsvValue(tag.Unit)}");
                }
            }

            return System.Text.Encoding.UTF8.GetBytes(csv.ToString());
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating CSV for dataset {DatasetId}", id);
            throw;
        }
    }

    public async Task<bool> ReIngestDatasetAsync(string id)
    {
        try
        {
            var publishRecord = await GetPublishRecordAsync(id);
            if (publishRecord == null)
            {
                _logger.LogWarning("Cannot re-ingest dataset {Id}: not found", id);
                return false;
            }

            // Only allow re-ingestion for batch mode
            if (publishRecord.StreamConfig.Mode != PublishingMode.Batch)
            {
                _logger.LogWarning("Cannot re-ingest dataset {Id}: not in batch mode", id);
                return false;
            }

            // Reset publishing progress
            publishRecord.Status = PublishingStatus.Pending;
            publishRecord.PublishedDataPoints = 0;
            publishRecord.CurrentSequenceNumber = 0;
            publishRecord.ErrorMessage = null;
            publishRecord.StreamConfig.ReIngestionCount++;
            publishRecord.StreamConfig.StreamStartTime = DateTime.UtcNow;

            await UpdatePublishRecordAsync(publishRecord);
            
            _logger.LogInformation("Re-ingestion initiated for dataset {Id}, count: {Count}", 
                id, publishRecord.StreamConfig.ReIngestionCount);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error re-ingesting dataset {Id}", id);
            return false;
        }
    }

    public async Task<bool> UpdatePublishingModeAsync(string id, PublishingMode mode, StreamConfiguration? config = null)
    {
        try
        {
            var publishRecord = await GetPublishRecordAsync(id);
            if (publishRecord == null)
            {
                _logger.LogWarning("Cannot update publishing mode for dataset {Id}: not found", id);
                return false;
            }

            // Initialize StreamConfig for old datasets that don't have it
            if (publishRecord.StreamConfig == null)
            {
                publishRecord.StreamConfig = new StreamConfiguration
                {
                    Mode = PublishingMode.Batch,
                    StreamIntervalMs = 1000,
                    StreamSpeed = 1.0,
                    LoopCycles = 1,
                    LoopPauseMs = 0,
                    IsActive = false,
                    CurrentCycle = 0,
                    ReIngestionCount = 0
                };
            }

            var oldMode = publishRecord.StreamConfig.Mode;
            publishRecord.StreamConfig.Mode = mode;
            
            // Apply new configuration if provided
            if (config != null)
            {
                publishRecord.StreamConfig.StreamIntervalMs = config.StreamIntervalMs;
                publishRecord.StreamConfig.StreamSpeed = config.StreamSpeed;
                publishRecord.StreamConfig.LoopCycles = config.LoopCycles;
                publishRecord.StreamConfig.LoopPauseMs = config.LoopPauseMs;
            }

            // Reset appropriate fields when changing modes
            if (mode != oldMode)
            {
                publishRecord.StreamConfig.CurrentCycle = 0;
                publishRecord.StreamConfig.IsActive = true;
                
                // Reset progress if switching to a repeating mode
                if (mode != PublishingMode.Batch)
                {
                    publishRecord.PublishedDataPoints = 0;
                    publishRecord.CurrentSequenceNumber = 0;
                    publishRecord.Status = PublishingStatus.Pending;
                }
            }

            await UpdatePublishRecordAsync(publishRecord);
            
            _logger.LogInformation("Updated publishing mode for dataset {Id} from {OldMode} to {NewMode}", 
                id, oldMode, mode);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating publishing mode for dataset {Id}", id);
            return false;
        }
    }

    public async Task<bool> StopStreamingAsync(string id)
    {
        try
        {
            var publishRecord = await GetPublishRecordAsync(id);
            if (publishRecord == null)
            {
                return false;
            }

            // Initialize StreamConfig for old datasets that don't have it
            if (publishRecord.StreamConfig == null)
            {
                publishRecord.StreamConfig = new StreamConfiguration
                {
                    Mode = PublishingMode.Batch,
                    StreamIntervalMs = 1000,
                    StreamSpeed = 1.0,
                    LoopCycles = 1,
                    LoopPauseMs = 0,
                    IsActive = false,
                    CurrentCycle = 0,
                    ReIngestionCount = 0
                };
            }

            publishRecord.StreamConfig.IsActive = false;
            await UpdatePublishRecordAsync(publishRecord);
            
            _logger.LogInformation("Stopped streaming for dataset {Id}", id);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error stopping streaming for dataset {Id}", id);
            return false;
        }
    }

    public async Task<bool> StartStreamingAsync(string id)
    {
        try
        {
            var publishRecord = await GetPublishRecordAsync(id);
            if (publishRecord == null)
            {
                return false;
            }

            // Initialize StreamConfig for old datasets that don't have it
            if (publishRecord.StreamConfig == null)
            {
                publishRecord.StreamConfig = new StreamConfiguration
                {
                    Mode = PublishingMode.Batch,
                    StreamIntervalMs = 1000,
                    StreamSpeed = 1.0,
                    LoopCycles = 1,
                    LoopPauseMs = 0,
                    IsActive = false,
                    CurrentCycle = 0,
                    ReIngestionCount = 0
                };
            }

            publishRecord.StreamConfig.IsActive = true;
            publishRecord.StreamConfig.StreamStartTime = DateTime.UtcNow;
            
            // If starting fresh, reset status
            if (publishRecord.Status == PublishingStatus.Completed || publishRecord.Status == PublishingStatus.Failed)
            {
                publishRecord.Status = PublishingStatus.Pending;
            }

            await UpdatePublishRecordAsync(publishRecord);
            
            _logger.LogInformation("Started streaming for dataset {Id}", id);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error starting streaming for dataset {Id}", id);
            return false;
        }
    }

    public async Task<bool> PauseStreamingAsync(string id)
    {
        try
        {
            var publishRecord = await GetPublishRecordAsync(id);
            if (publishRecord == null)
            {
                return false;
            }

            // Initialize StreamConfig for old datasets that don't have it
            if (publishRecord.StreamConfig == null)
            {
                publishRecord.StreamConfig = new StreamConfiguration
                {
                    Mode = PublishingMode.Batch,
                    StreamIntervalMs = 1000,
                    StreamSpeed = 1.0,
                    LoopCycles = 1,
                    LoopPauseMs = 0,
                    IsActive = false,
                    CurrentCycle = 0,
                    ReIngestionCount = 0
                };
            }

            publishRecord.StreamConfig.IsActive = false;
            await UpdatePublishRecordAsync(publishRecord);
            
            _logger.LogInformation("Paused streaming for dataset {Id}", id);
            return true;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error pausing streaming for dataset {Id}", id);
            return false;
        }
    }
}
