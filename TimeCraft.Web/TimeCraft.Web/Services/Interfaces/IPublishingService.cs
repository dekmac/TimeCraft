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
    Task<ExportDeltaFramesCsvResponse> ExportDeltaFramesCsvAsync(ExportDeltaFramesCsvRequest request);
}
