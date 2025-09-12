namespace TimeCraft.Web.Settings;

public class PublishingSettings
{
    public int MaxRetryAttempts { get; set; } = 3;
    public int RetryDelaySeconds { get; set; } = 30;
    public string StorageDirectory { get; set; } = "Data/PublishRecords";
}
