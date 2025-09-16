using System.ComponentModel.DataAnnotations;

namespace TimeCraft.Web.Models.Publishing;

public class PublishDatasetRequest
{
    [Required(ErrorMessage = "Dataset name is required")]
    public string DatasetName { get; set; } = string.Empty;
    
    public string Description { get; set; } = string.Empty;
    
    public string? OriginalPrompt { get; set; }
    
    [Required(ErrorMessage = "Tags are required")]
    public List<DatasetTag> Tags { get; set; } = new();
    
    [Required(ErrorMessage = "Event Hub configuration is required")]
    public EventHubConfig EventHubConfig { get; set; } = new();
    
    public OpcUaSettings OpcUaSettings { get; set; } = new();
    
    public Dictionary<string, string> Metadata { get; set; } = new();
}
