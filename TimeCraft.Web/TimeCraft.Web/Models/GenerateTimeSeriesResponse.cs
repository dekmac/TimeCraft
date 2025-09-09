namespace TimeCraft.Web.Models;

public class GenerateTimeSeriesResponse
{
    public bool Success { get; set; }
    public string TagName { get; set; } = string.Empty;
    public List<double> TimeSeries { get; set; } = new();
    public List<string> Timestamps { get; set; } = new();
    public string? Message { get; set; }
}
