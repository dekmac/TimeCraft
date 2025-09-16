namespace TimeCraft.Web.Models.Publishing;

public class DatasetContent
{
    public string Id { get; set; } = string.Empty;
    public string DatasetName { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string? OriginalPrompt { get; set; }
    public string? ScenarioParameters { get; set; }
    public List<DatasetTag> Tags { get; set; } = new();
    public PublishingStatus Status { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? PublishedAt { get; set; }
    public int TotalTags { get; set; }
    public int TotalDataPoints { get; set; }
}