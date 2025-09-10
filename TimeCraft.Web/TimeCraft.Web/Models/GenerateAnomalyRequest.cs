namespace TimeCraft.Web.Models;

public class GenerateAnomalyRequest
{
    public string TagName { get; set; } = string.Empty;
    public string TagDescription { get; set; } = string.Empty;
    public List<double> ExistingTimeSeries { get; set; } = new();
    public int InjectionStartIndex { get; set; }
    public int InjectionEndIndex { get; set; }
    public string AnomalyType { get; set; } = string.Empty;
    public string AnomalyDescription { get; set; } = string.Empty;
    public double Severity { get; set; } = 1.0;
}
