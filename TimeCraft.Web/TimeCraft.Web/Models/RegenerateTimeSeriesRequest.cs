using System.ComponentModel.DataAnnotations;

namespace TimeCraft.Web.Models;

public class RegenerateTimeSeriesRequest
{
    [Required(ErrorMessage = "Tag is required")]
    public string Tag { get; set; } = string.Empty;
    
    [Required(ErrorMessage = "Scenario is required")]
    public string Scenario { get; set; } = string.Empty;
    
    public string? Instructions { get; set; }
    
    public int SequenceLength { get; set; } = 100;
    
    public int TagIndex { get; set; }
    
    public TimeHorizonInfo? TimeHorizon { get; set; }
}