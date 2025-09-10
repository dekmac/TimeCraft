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

    private async Task<List<PublishRecord>> GetAllPublishRecordsAsync()
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
            Status = record.Status,
            CreatedAt = record.CreatedAt,
            PublishedAt = record.PublishedAt,
            EventHubName = record.EventHubConfig.EventHubName,
            NamespaceName = record.EventHubConfig.NamespaceName,
            TotalDataPoints = record.TotalDataPoints,
            PublishedDataPoints = record.PublishedDataPoints,
            ErrorMessage = record.ErrorMessage,
            RetryCount = record.RetryCount
        };
    }
}
