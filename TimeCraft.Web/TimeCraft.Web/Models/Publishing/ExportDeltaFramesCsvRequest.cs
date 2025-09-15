namespace TimeCraft.Web.Models.Publishing;

public class ExportDeltaFramesCsvRequest
{
    public string DatasetId { get; set; } = string.Empty;
    public DateTime? StartTime { get; set; }
    public DateTime? EndTime { get; set; }
    public bool UseRelativeTimestamps { get; set; } = true;
    public DateTime? ReferenceTime { get; set; } // If null, uses DateTime.UtcNow
    public List<string>? TagFilter { get; set; } // Optional filter by tag names
}