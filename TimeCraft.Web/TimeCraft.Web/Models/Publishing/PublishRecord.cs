using TimeCraft.Web.Models;

namespace TimeCraft.Web.Models.Publishing;

public class PublishRecord
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string DatasetName { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string? OriginalPrompt { get; set; }
    public string? ScenarioParameters { get; set; }
    public List<DatasetTag> Tags { get; set; } = new();
    public EventHubConfig EventHubConfig { get; set; } = new();
    public OpcUaSettings OpcUaSettings { get; set; } = new();
    public PublishingStatus Status { get; set; } = PublishingStatus.Pending;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? PublishedAt { get; set; }
    public string? ErrorMessage { get; set; }
    public int RetryCount { get; set; } = 0;
    public int TotalDataPoints { get; set; }
    public int PublishedDataPoints { get; set; } = 0;
    public int CurrentSequenceNumber { get; set; } = 0;
    public Dictionary<string, string> Metadata { get; set; } = new();
}
