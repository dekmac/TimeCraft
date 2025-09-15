namespace TimeCraft.Web.Models.Publishing;

/// <summary>
/// Request model for updating streaming progress information
/// </summary>
public class UpdateStreamingProgressRequest
{
    /// <summary>
    /// Number of data points sent in current streaming session
    /// </summary>
    public int PointsSent { get; set; }
    
    /// <summary>
    /// Current position in the dataset (data point index)
    /// </summary>
    public int CurrentPosition { get; set; }
}