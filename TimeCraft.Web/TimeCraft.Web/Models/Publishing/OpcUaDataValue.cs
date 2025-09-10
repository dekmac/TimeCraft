namespace TimeCraft.Web.Models.Publishing;

public class OpcUaDataValue
{
    public string NodeId { get; set; } = string.Empty;
    public string DisplayName { get; set; } = string.Empty;
    public object? Value { get; set; }
    public DateTime SourceTimestamp { get; set; } = DateTime.UtcNow;
    public DateTime ServerTimestamp { get; set; } = DateTime.UtcNow;
    public uint StatusCode { get; set; } = 0; // Good = 0
    public string DataType { get; set; } = "Double";
    public int? ArrayDimensions { get; set; }
}
