namespace TimeCraft.Web.Models;

public class GenerateAnomalyResponse
{
    public bool Success { get; set; }
    public string Message { get; set; } = string.Empty;
    public string TagName { get; set; } = string.Empty;
    public List<double> ModifiedTimeSeries { get; set; } = new();
    public List<string> Timestamps { get; set; } = new();
    public int AnomalyStartIndex { get; set; }
    public int AnomalyEndIndex { get; set; }
    public string AnomalyType { get; set; } = string.Empty;
}
