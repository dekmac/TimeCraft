namespace TimeCraft.Web.Models.Publishing;

/// <summary>
/// Request model for updating a dataset's publishing mode
/// </summary>
public class UpdateModeRequest
{
    /// <summary>
    /// The new publishing mode to set
    /// </summary>
    public PublishingMode Mode { get; set; }

    /// <summary>
    /// Optional stream configuration for streaming modes
    /// </summary>
    public StreamConfiguration? StreamConfig { get; set; }
}