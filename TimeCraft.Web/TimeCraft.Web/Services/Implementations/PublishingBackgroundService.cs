using Microsoft.Extensions.Options;
using TimeCraft.Web.Models.Publishing;
using TimeCraft.Web.Services.Interfaces;
using TimeCraft.Web.Settings;

namespace TimeCraft.Web.Services.Implementations;

public class PublishingBackgroundService : BackgroundService
{
    private readonly IServiceScopeFactory _serviceScopeFactory;
    private readonly PublishingSettings _settings;
    private readonly ILogger<PublishingBackgroundService> _logger;

    public PublishingBackgroundService(
        IServiceScopeFactory serviceScopeFactory,
        IOptions<PublishingSettings> settings,
        ILogger<PublishingBackgroundService> logger)
    {
        _serviceScopeFactory = serviceScopeFactory;
        _settings = settings.Value;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _logger.LogInformation("Publishing background service started");

        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await ProcessPendingPublishRecordsAsync(stoppingToken);
                await ProcessActiveStreamingDatasetsAsync(stoppingToken);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in publishing background service");
            }

            // Wait before checking for more pending records
            await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken);
        }

        _logger.LogInformation("Publishing background service stopped");
    }

    private async Task ProcessPendingPublishRecordsAsync(CancellationToken cancellationToken)
    {
        using var scope = _serviceScopeFactory.CreateScope();
        var publishingService = scope.ServiceProvider.GetRequiredService<IPublishingService>();
        var opcUaPublisher = scope.ServiceProvider.GetRequiredService<IOpcUaDeltaFramePublisher>();

        var pendingRecords = await publishingService.GetPendingPublishRecordsAsync();

        foreach (var record in pendingRecords)
        {
            if (cancellationToken.IsCancellationRequested)
            {
                break;
            }

            await ProcessPublishRecordAsync(record, publishingService, opcUaPublisher, cancellationToken);
        }
    }

    private async Task ProcessPublishRecordAsync(
        PublishRecord record, 
        IPublishingService publishingService, 
        IOpcUaDeltaFramePublisher opcUaPublisher,
        CancellationToken cancellationToken)
    {
        try
        {
            _logger.LogInformation("Processing publish record {PublishId} for dataset {DatasetName}", 
                record.Id, record.DatasetName);

            // Check if we should retry
            if (record.Status == PublishingStatus.Failed && record.RetryCount >= _settings.MaxRetryAttempts)
            {
                _logger.LogWarning("Publish record {PublishId} has exceeded max retry attempts ({MaxRetries})", 
                    record.Id, _settings.MaxRetryAttempts);
                return;
            }

            // If it's a retry, wait for the retry delay
            if (record.Status == PublishingStatus.Retrying)
            {
                var timeSinceLastAttempt = DateTime.UtcNow - record.CreatedAt;
                var retryDelay = TimeSpan.FromSeconds(_settings.RetryDelaySeconds);
                
                if (timeSinceLastAttempt < retryDelay)
                {
                    _logger.LogDebug("Publish record {PublishId} is not ready for retry yet", record.Id);
                    return;
                }
            }

            // Update retry count if this is a retry
            if (record.Status == PublishingStatus.Failed || record.Status == PublishingStatus.Retrying)
            {
                record.RetryCount++;
                record.Status = PublishingStatus.Retrying;
                await publishingService.UpdatePublishRecordAsync(record);
                
                _logger.LogInformation("Retrying publish record {PublishId} (attempt {RetryCount}/{MaxRetries})", 
                    record.Id, record.RetryCount, _settings.MaxRetryAttempts);
            }

            // Attempt to publish using OPC UA Delta frames
            await opcUaPublisher.PublishDatasetAsync(record, cancellationToken);

            // Update the record with success
            await publishingService.UpdatePublishRecordAsync(record);

            _logger.LogInformation("Successfully published dataset {DatasetName} (ID: {PublishId})", 
                record.DatasetName, record.Id);
        }
        catch (OperationCanceledException)
        {
            _logger.LogInformation("Publishing operation was cancelled for record {PublishId}", record.Id);
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error publishing record {PublishId} for dataset {DatasetName}", 
                record.Id, record.DatasetName);

            try
            {
                // Update record with failure
                record.Status = record.RetryCount < _settings.MaxRetryAttempts 
                    ? PublishingStatus.Retrying 
                    : PublishingStatus.Failed;
                record.ErrorMessage = ex.Message;
                
                await publishingService.UpdatePublishRecordAsync(record);
            }
            catch (Exception updateEx)
            {
                _logger.LogError(updateEx, "Error updating failed publish record {PublishId}", record.Id);
            }
        }
    }

    private async Task ProcessActiveStreamingDatasetsAsync(CancellationToken cancellationToken)
    {
        using var scope = _serviceScopeFactory.CreateScope();
        var publishingService = scope.ServiceProvider.GetRequiredService<IPublishingService>();
        var opcUaPublisher = scope.ServiceProvider.GetRequiredService<IOpcUaDeltaFramePublisher>();

        var allRecords = await publishingService.GetAllPublishRecordsAsync();
        var activeStreamingRecords = allRecords.Where(r => 
            r.StreamConfig != null && 
            r.StreamConfig.IsActive &&
            (r.StreamConfig.Mode == PublishingMode.Loop || r.StreamConfig.Mode == PublishingMode.RealTimeStream) &&
            r.Status == PublishingStatus.Completed
        ).ToList();

        foreach (var record in activeStreamingRecords)
        {
            if (cancellationToken.IsCancellationRequested)
            {
                break;
            }

            await ProcessStreamingDatasetAsync(record, publishingService, opcUaPublisher, cancellationToken);
        }
    }

    private async Task ProcessStreamingDatasetAsync(
        PublishRecord record, 
        IPublishingService publishingService, 
        IOpcUaDeltaFramePublisher opcUaPublisher,
        CancellationToken cancellationToken)
    {
        try
        {
            if (record.StreamConfig == null || record.Tags == null) return;
            if (!Guid.TryParse(record.Id, out var recordGuid)) return;

            var streamConfig = record.StreamConfig;
            var totalDataPoints = record.Tags.Max(tag => tag.TimeSeriesData.Count);
            
            // Check if we should send the next data point
            var lastUpdate = streamConfig.PausedAt ?? DateTime.UtcNow.AddMinutes(-1);
            var timeSinceLastUpdate = DateTime.UtcNow - lastUpdate;
            var effectiveInterval = TimeSpan.FromMilliseconds(streamConfig.StreamIntervalMs / streamConfig.StreamSpeed);
            
            if (timeSinceLastUpdate < effectiveInterval)
            {
                return; // Not time for next update yet
            }

            // Get current position
            var currentPosition = streamConfig.CurrentStreamPosition;
            
            // Check if we've reached the end
            if (currentPosition >= totalDataPoints)
            {
                if (streamConfig.Mode == PublishingMode.Loop && 
                    (!streamConfig.LoopCycles.HasValue || streamConfig.CurrentCycle < streamConfig.LoopCycles.Value))
                {
                    // Reset to beginning for next loop cycle
                    currentPosition = 0;
                    streamConfig.CurrentCycle++;
                    _logger.LogInformation("Starting loop cycle {Cycle} for dataset {DatasetName}", 
                        streamConfig.CurrentCycle, record.DatasetName);
                }
                else
                {
                    // Stop streaming
                    streamConfig.IsActive = false;
                    await publishingService.UpdateStreamingStatsAsync(recordGuid, false);
                    _logger.LogInformation("Streaming completed for dataset {DatasetName}", record.DatasetName);
                    return;
                }
            }

            // For now, just simulate progress updates
            var pointsSent = Math.Min(currentPosition + 1, totalDataPoints);
            streamConfig.CurrentStreamPosition = pointsSent;
            streamConfig.StreamPointsSent += record.Tags.Count; // Count all tags as sent
            
            await publishingService.UpdateStreamingProgressAsync(recordGuid, streamConfig.StreamPointsSent, streamConfig.CurrentStreamPosition);
            
            _logger.LogDebug("Simulated streaming progress: {Position}/{Total} for dataset {DatasetName}", 
                streamConfig.CurrentStreamPosition, totalDataPoints, record.DatasetName);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing streaming dataset {DatasetName}", record.DatasetName);
            
            // Stop streaming on error
            if (record.StreamConfig != null && Guid.TryParse(record.Id, out var errorGuid))
            {
                record.StreamConfig.IsActive = false;
                await publishingService.UpdateStreamingStatsAsync(errorGuid, false);
            }
        }
    }

    public override async Task StopAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("Publishing background service is stopping");
        await base.StopAsync(cancellationToken);
    }
}
