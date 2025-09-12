namespace TimeCraft.Web.Models.Publishing;

public class DatasetTag
{
    public string TagName { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public List<TimeSeriesDataPoint> TimeSeriesData { get; set; } = new();
    public string DataType { get; set; } = "Double"; // OPC UA data type
    public string? Unit { get; set; }
    public Dictionary<string, string> Metadata { get; set; } = new();
}
