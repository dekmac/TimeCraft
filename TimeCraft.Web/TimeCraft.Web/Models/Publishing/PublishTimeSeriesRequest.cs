using System.ComponentModel.DataAnnotations;
using TimeCraft.Web.Models;

namespace TimeCraft.Web.Models.Publishing;

public class PublishTimeSeriesRequest
{
    [Required(ErrorMessage = "Dataset name is required")]
    public string DatasetName { get; set; } = string.Empty;
    
    public string Description { get; set; } = string.Empty;
    
    [Required(ErrorMessage = "Time series data is required")]
    public List<TimeSeriesDataPoint> TimeSeriesData { get; set; } = new();
    
    [Required(ErrorMessage = "Event Hub configuration is required")]
    public EventHubConfig EventHubConfig { get; set; } = new();
    
    public Dictionary<string, string> Metadata { get; set; } = new();
}
