namespace TimeCraft.Web.Models;

public class GenerateTimeSeriesRequest
{
    public string? Tag { get; set; }
    public string? Scenario { get; set; }
    public TimeHorizonInfo? TimeHorizon { get; set; }
}

public class TimeHorizonInfo
{
    public int Period { get; set; }
    public string? Unit { get; set; } // minutes, hours, days, weeks
    public string? Granularity { get; set; } // minute, hour, day
    public int TotalPoints { get; set; }
    public int? BatchSize { get; set; }
    public int? BatchIndex { get; set; }
}
