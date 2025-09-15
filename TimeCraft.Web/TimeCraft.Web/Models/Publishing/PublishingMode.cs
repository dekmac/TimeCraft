using System.Text.Json.Serialization;

namespace TimeCraft.Web.Models.Publishing;

[JsonConverter(typeof(JsonStringEnumConverter))]
public enum PublishingMode
{
    /// <summary>
    /// Publish all data once and complete
    /// </summary>
    Batch = 0,
    
    /// <summary>
    /// Continuously loop through the dataset, repeating cycles
    /// </summary>
    Loop = 1,
    
    /// <summary>
    /// Stream data as if it's happening in real-time with proper timing intervals
    /// </summary>
    RealTimeStream = 2
}