namespace TimeCraft.Web.Models.Publishing;

/// <summary>
/// Request model for updating streaming statistics
/// </summary>
public class UpdateStreamingStatsRequest
{
    /// <summary>
    /// Whether the streaming is currently active
    /// </summary>
    public bool IsActive { get; set; }
    
    /// <summary>
    /// Current cycle count (optional, for loop mode)
    /// </summary>
    public int? CycleCount { get; set; }
}