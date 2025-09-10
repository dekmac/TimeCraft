namespace TimeCraft.Web.Models.Publishing;

public class PublishedDataset
{
    public string Id { get; set; } = string.Empty;
    public string DatasetName { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public PublishingStatus Status { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? PublishedAt { get; set; }
    public string EventHubName { get; set; } = string.Empty;
    public string NamespaceName { get; set; } = string.Empty;
    public int TotalDataPoints { get; set; }
    public int PublishedDataPoints { get; set; }
    public string? ErrorMessage { get; set; }
    public int RetryCount { get; set; }
    public double ProgressPercentage => TotalDataPoints > 0 ? (double)PublishedDataPoints / TotalDataPoints * 100 : 0;
}
