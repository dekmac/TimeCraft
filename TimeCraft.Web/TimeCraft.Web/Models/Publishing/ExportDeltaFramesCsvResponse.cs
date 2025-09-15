namespace TimeCraft.Web.Models.Publishing;

public class ExportDeltaFramesCsvResponse
{
    public string? FileName { get; set; }
    public byte[]? FileContent { get; set; }
    public string ContentType { get; set; } = "text/csv";
    public int TotalRecords { get; set; }
    public string Message { get; set; } = string.Empty;
}