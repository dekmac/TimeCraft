namespace TimeCraft.Web.Models.Publishing;

public class PublishTimeSeriesResponse
{
    public string PublishId { get; set; } = string.Empty;
    public string Message { get; set; } = string.Empty;
    public PublishingStatus Status { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
