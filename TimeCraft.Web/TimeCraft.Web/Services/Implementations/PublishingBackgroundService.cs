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
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in publishing background service");
            }

            // Wait before checking for more pending records
            await Task.Delay(TimeSpan.FromSeconds(10), stoppingToken);
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

    public override async Task StopAsync(CancellationToken cancellationToken)
    {
        _logger.LogInformation("Publishing background service is stopping");
        await base.StopAsync(cancellationToken);
    }
}
