using System.ComponentModel.DataAnnotations;

namespace TimeCraft.Web.Models.Publishing;

public class EventHubConfig
{
    [Required(ErrorMessage = "Event Hub name is required")]
    public string EventHubName { get; set; } = string.Empty;
    
    [Required(ErrorMessage = "Namespace name is required")]
    public string NamespaceName { get; set; } = string.Empty;
    
    public string? ConnectionString { get; set; }
    
    public bool UseManagedIdentity { get; set; } = true;
    
    public string? PartitionKey { get; set; }
    
    public Dictionary<string, string> AdditionalProperties { get; set; } = new();
    
    // Helper method to get the fully qualified namespace
    public string GetFullyQualifiedNamespace()
    {
        if (NamespaceName.Contains(".servicebus.windows.net"))
        {
            return NamespaceName;
        }
        return $"{NamespaceName}.servicebus.windows.net";
    }
}
