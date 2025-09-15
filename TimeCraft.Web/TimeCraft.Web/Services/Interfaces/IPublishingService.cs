using TimeCraft.Web.Models.Publishing;

namespace TimeCraft.Web.Services.Interfaces;

public interface IPublishingService
{
    Task<string> CreatePublishRecordAsync(PublishRecord publishRecord);
    Task<PublishedDataset?> GetPublishedDatasetAsync(string id);
    Task<List<PublishedDataset>> GetAllPublishedDatasetsAsync();
    Task UpdatePublishRecordAsync(PublishRecord publishRecord);
    Task<PublishRecord?> GetPublishRecordAsync(string id);
    Task<List<PublishRecord>> GetPendingPublishRecordsAsync();
    Task<List<PublishRecord>> GetAllPublishRecordsAsync();
    Task<ExportDeltaFramesCsvResponse> ExportDeltaFramesCsvAsync(ExportDeltaFramesCsvRequest request);
    Task<bool> ForceRetryDatasetAsync(string id);
    Task<byte[]> DownloadDatasetCsvAsync(string id);
    Task<bool> ReIngestDatasetAsync(string id);
    Task<bool> UpdatePublishingModeAsync(string id, PublishingMode mode, StreamConfiguration? config = null);
    Task<bool> StopStreamingAsync(string id);
    Task<bool> StartStreamingAsync(string id);
    Task<bool> PauseStreamingAsync(string id);
    Task<bool> UpdateStreamingProgressAsync(Guid id, int pointsSent, int currentPosition);
    Task<bool> UpdateStreamingStatsAsync(Guid id, bool isActive, int? cycleCount = null);
}
