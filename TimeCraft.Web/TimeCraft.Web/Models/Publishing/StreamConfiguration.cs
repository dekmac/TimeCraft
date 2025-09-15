namespace TimeCraft.Web.Models.Publishing;

public class StreamConfiguration
{
    /// <summary>
    /// Publishing mode for this dataset
    /// </summary>
    public PublishingMode Mode { get; set; } = PublishingMode.Batch;
    
    /// <summary>
    /// Interval between data points in milliseconds (for real-time streaming)
    /// </summary>
    public int StreamIntervalMs { get; set; } = 1000; // Default 1 second
    
    /// <summary>
    /// Speed multiplier for real-time streaming (1.0 = real-time, 2.0 = 2x speed, 0.5 = half speed)
    /// </summary>
    public double StreamSpeed { get; set; } = 1.0;
    
    /// <summary>
    /// Number of loop cycles to run (null = infinite)
    /// </summary>
    public int? LoopCycles { get; set; } = null;
    
    /// <summary>
    /// Pause between loop cycles in milliseconds
    /// </summary>
    public int LoopPauseMs { get; set; } = 5000; // Default 5 seconds
    
    /// <summary>
    /// Whether streaming/looping is currently active
    /// </summary>
    public bool IsActive { get; set; } = true;
    
    /// <summary>
    /// Current cycle number (for loop mode)
    /// </summary>
    public int CurrentCycle { get; set; } = 0;
    
    /// <summary>
    /// When the streaming started (for real-time mode)
    /// </summary>
    public DateTime? StreamStartTime { get; set; }
    
    /// <summary>
    /// Number of times this dataset has been re-ingested (for batch mode)
    /// </summary>
    public int ReIngestionCount { get; set; } = 0;
    
    /// <summary>
    /// Current position in the dataset for streaming (data point index)
    /// </summary>
    public int CurrentStreamPosition { get; set; } = 0;
    
    /// <summary>
    /// Total number of data points sent in current streaming session
    /// </summary>
    public int StreamPointsSent { get; set; } = 0;
    
    /// <summary>
    /// When the current streaming session was paused
    /// </summary>
    public DateTime? PausedAt { get; set; }
    
    /// <summary>
    /// Total time spent streaming (excluding paused time)
    /// </summary>
    public TimeSpan TotalStreamTime { get; set; } = TimeSpan.Zero;
}