namespace TimeCraft.Web.Models.Publishing;

public class OpcUaSettings
{
    public string NamespaceUri { get; set; } = "urn:TimeCraft:Industrial";
    public int NamespaceIndex { get; set; } = 2;
    public bool UseDataSetWriterId { get; set; } = true;
    public int PublishingInterval { get; set; } = 1000; // milliseconds
    public bool EnableDeltaFrames { get; set; } = true;
    public string ApplicationName { get; set; } = "TimeCraft Publisher";
    public string ApplicationUri { get; set; } = "urn:TimeCraft:Publisher";
    public Dictionary<string, string> CustomProperties { get; set; } = new();
}
