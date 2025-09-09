namespace TimeCraft.Web.Models;

public class GenerateTagsResponse
{
    public bool Success { get; set; }
    public string? Message { get; set; }
    public List<GeneratedTag> Tags { get; set; } = new();
}
