namespace TimeCraft.Web.Models.Publishing;

public class OpcUaDeltaFrame
{
    public string DataSetWriterId { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public int SequenceNumber { get; set; }
    public List<OpcUaDataValue> DataValues { get; set; } = new();
    public Dictionary<string, object> MessageMetadata { get; set; } = new();
}
