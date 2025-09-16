using Microsoft.AspNetCore.Mvc;
using TimeCraft.Web.Models.Publishing;
using TimeCraft.Web.Services.Interfaces;

namespace TimeCraft.Web.Controllers;

[ApiController]
[Route("api/[controller]")]
public class PublishingController : ControllerBase
{
    private readonly IPublishingService _publishingService;
    private readonly ILogger<PublishingController> _logger;

    public PublishingController(IPublishingService publishingService, ILogger<PublishingController> logger)
    {
        _publishingService = publishingService;
        _logger = logger;
    }

    [HttpPost("publish-dataset")]
    public async Task<ActionResult<PublishTimeSeriesResponse>> PublishDataset([FromBody] PublishDatasetRequest request)
    {
        _logger.LogInformation("=== PublishDataset method called ===");
        
        try
        {
            if (request == null)
            {
                _logger.LogWarning("Request object is null");
                return BadRequest("Request is required");
            }

            if (!ModelState.IsValid)
            {
                _logger.LogWarning("Invalid model state: {ModelState}", ModelState);
                return BadRequest(ModelState);
            }

            if (request.Tags == null || !request.Tags.Any())
            {
                _logger.LogWarning("No tags provided for dataset publishing");
                return BadRequest("At least one tag is required for dataset publishing");
            }

            // Validate that all tags have time series data
            var tagsWithoutData = request.Tags.Where(tag => tag.TimeSeriesData == null || !tag.TimeSeriesData.Any()).ToList();
            if (tagsWithoutData.Any())
            {
                _logger.LogWarning("Some tags have no time series data: {TagNames}", 
                    string.Join(", ", tagsWithoutData.Select(t => t.TagName)));
                return BadRequest("All tags must have time series data");
            }

            // Create publish record
            var publishRecord = new PublishRecord
            {
                DatasetName = request.DatasetName,
                Description = request.Description,
                OriginalPrompt = request.OriginalPrompt,
                Tags = request.Tags,
                EventHubConfig = request.EventHubConfig,
                OpcUaSettings = request.OpcUaSettings,
                Metadata = request.Metadata,
                TotalDataPoints = request.Tags.Sum(tag => tag.TimeSeriesData.Count)
            };

            // Store the publish record
            var publishId = await _publishingService.CreatePublishRecordAsync(publishRecord);

            _logger.LogInformation("Created publish record {PublishId} for dataset {DatasetName} with {TagCount} tags and {DataPointCount} total data points", 
                publishId, request.DatasetName, request.Tags.Count, publishRecord.TotalDataPoints);

            var response = new PublishTimeSeriesResponse
            {
                PublishId = publishId,
                Message = $"Dataset publish request created successfully. Publishing {request.Tags.Count} tags with OPC UA Delta frames will begin in the background.",
                Status = PublishingStatus.Pending
            };

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating dataset publish request for {DatasetName}", request?.DatasetName);
            return StatusCode(500, "An error occurred while creating the dataset publish request");
        }
    }

    [HttpGet("datasets")]
    public async Task<ActionResult<List<PublishedDataset>>> GetPublishedDatasets()
    {
        try
        {
            _logger.LogInformation("Getting all published datasets");
            
            var datasets = await _publishingService.GetAllPublishedDatasetsAsync();
            
            return Ok(datasets);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting published datasets");
            return StatusCode(500, "An error occurred while retrieving published datasets");
        }
    }

    [HttpGet("datasets/{id}")]
    public async Task<ActionResult<PublishedDataset>> GetPublishedDataset(string id)
    {
        try
        {
            if (string.IsNullOrEmpty(id))
            {
                return BadRequest("Dataset ID is required");
            }

            _logger.LogInformation("Getting published dataset {Id}", id);
            
            var dataset = await _publishingService.GetPublishedDatasetAsync(id);
            
            if (dataset == null)
            {
                return NotFound($"Dataset with ID {id} not found");
            }

            return Ok(dataset);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting published dataset {Id}", id);
            return StatusCode(500, "An error occurred while retrieving the published dataset");
        }
    }

    [HttpGet("datasets/{id}/content")]
    public async Task<ActionResult<DatasetContent>> GetDatasetContent(string id)
    {
        try
        {
            if (string.IsNullOrEmpty(id))
            {
                return BadRequest("Dataset ID is required");
            }

            _logger.LogInformation("Getting dataset content {Id}", id);
            
            var content = await _publishingService.GetDatasetContentAsync(id);
            
            if (content == null)
            {
                return NotFound($"Dataset with ID {id} not found");
            }

            return Ok(content);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting dataset content {Id}", id);
            return StatusCode(500, "An error occurred while retrieving the dataset content");
        }
    }

    [HttpGet("datasets/{id}/status")]
    public async Task<ActionResult<object>> GetPublishingStatus(string id)
    {
        try
        {
            if (string.IsNullOrEmpty(id))
            {
                return BadRequest("Dataset ID is required");
            }

            _logger.LogInformation("Getting publishing status for dataset {Id}", id);
            
            var dataset = await _publishingService.GetPublishedDatasetAsync(id);
            
            if (dataset == null)
            {
                return NotFound($"Dataset with ID {id} not found");
            }

            var statusInfo = new
            {
                Id = dataset.Id,
                Status = dataset.Status.ToString(),
                ProgressPercentage = dataset.ProgressPercentage,
                PublishedDataPoints = dataset.PublishedDataPoints,
                TotalDataPoints = dataset.TotalDataPoints,
                ErrorMessage = dataset.ErrorMessage,
                RetryCount = dataset.RetryCount,
                CreatedAt = dataset.CreatedAt,
                PublishedAt = dataset.PublishedAt
            };

            return Ok(statusInfo);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting publishing status for dataset {Id}", id);
            return StatusCode(500, "An error occurred while retrieving the publishing status");
        }
    }

    [HttpPost("datasets/{id}/force-retry")]
    public async Task<ActionResult> ForceRetryDataset(string id)
    {
        try
        {
            if (string.IsNullOrEmpty(id))
            {
                return BadRequest("Dataset ID is required");
            }

            _logger.LogInformation("Force retry requested for dataset {Id}", id);
            
            var success = await _publishingService.ForceRetryDatasetAsync(id);
            
            if (!success)
            {
                return NotFound($"Dataset with ID {id} not found or could not be reset for retry");
            }

            return Ok(new { message = "Dataset has been reset and will be retried automatically", datasetId = id });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error forcing retry for dataset {Id}", id);
            return StatusCode(500, "An error occurred while forcing retry for the dataset");
        }
    }

    [HttpGet("datasets/{id}/download-csv")]
    public async Task<IActionResult> DownloadDatasetCsv(string id)
    {
        try
        {
            if (string.IsNullOrEmpty(id))
            {
                return BadRequest("Dataset ID is required");
            }

            _logger.LogInformation("Downloading CSV for dataset {Id}", id);
            
            var dataset = await _publishingService.GetPublishedDatasetAsync(id);
            if (dataset == null)
            {
                return NotFound($"Dataset with ID {id} not found");
            }

            var csvData = await _publishingService.DownloadDatasetCsvAsync(id);
            
            var fileName = $"{dataset.DatasetName.Replace(" ", "_")}_{DateTime.UtcNow:yyyyMMdd_HHmmss}.csv";
            
            return File(csvData, "text/csv", fileName);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error downloading CSV for dataset {Id}", id);
            return StatusCode(500, "An error occurred while downloading the CSV file");
        }
    }

    [HttpPost("datasets/{id}/export-csv")]
    public async Task<IActionResult> ExportDeltaFramesCsv(string id, [FromBody] ExportDeltaFramesCsvRequest? request = null)
    {
        try
        {
            if (string.IsNullOrEmpty(id))
            {
                return BadRequest("Dataset ID is required");
            }

            // Create request if not provided
            request ??= new ExportDeltaFramesCsvRequest();
            request.DatasetId = id;

            _logger.LogInformation("Exporting OPC UA delta frames CSV for dataset {Id}", id);
            
            var result = await _publishingService.ExportDeltaFramesCsvAsync(request);
            
            if (result.FileContent == null)
            {
                return NotFound("No data available for export");
            }

            return File(result.FileContent, result.ContentType, result.FileName);
        }
        catch (ArgumentException ex)
        {
            _logger.LogWarning(ex, "Invalid request for CSV export of dataset {Id}", id);
            return BadRequest(ex.Message);
        }
        catch (InvalidOperationException ex)
        {
            _logger.LogWarning(ex, "Operation error during CSV export of dataset {Id}", id);
            return NotFound(ex.Message);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error exporting OPC UA delta frames CSV for dataset {Id}", id);
            return StatusCode(500, "An error occurred while exporting the CSV file");
        }
    }

    [HttpGet("datasets/{id}/export-csv")]
    public async Task<IActionResult> ExportDeltaFramesCsvGet(string id, 
        [FromQuery] bool useRelativeTimestamps = true,
        [FromQuery] DateTime? startTime = null,
        [FromQuery] DateTime? endTime = null,
        [FromQuery] DateTime? referenceTime = null,
        [FromQuery] string[]? tagFilter = null)
    {
        try
        {
            if (string.IsNullOrEmpty(id))
            {
                return BadRequest("Dataset ID is required");
            }

            var request = new ExportDeltaFramesCsvRequest
            {
                DatasetId = id,
                UseRelativeTimestamps = useRelativeTimestamps,
                StartTime = startTime,
                EndTime = endTime,
                ReferenceTime = referenceTime,
                TagFilter = tagFilter?.ToList()
            };

            _logger.LogInformation("Exporting OPC UA delta frames CSV for dataset {Id} with relative timestamps: {UseRelative}", 
                id, useRelativeTimestamps);
            
            var result = await _publishingService.ExportDeltaFramesCsvAsync(request);
            
            if (result.FileContent == null)
            {
                return NotFound("No data available for export");
            }

            return File(result.FileContent, result.ContentType, result.FileName);
        }
        catch (ArgumentException ex)
        {
            _logger.LogWarning(ex, "Invalid request for CSV export of dataset {Id}", id);
            return BadRequest(ex.Message);
        }
        catch (InvalidOperationException ex)
        {
            _logger.LogWarning(ex, "Operation error during CSV export of dataset {Id}", id);
            return NotFound(ex.Message);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error exporting OPC UA delta frames CSV for dataset {Id}", id);
            return StatusCode(500, "An error occurred while exporting the CSV file");
        }
    }

    [HttpPost("datasets/{id}/re-ingest")]
    public async Task<ActionResult> ReIngestDataset(string id)
    {
        try
        {
            if (string.IsNullOrEmpty(id))
            {
                return BadRequest("Dataset ID is required");
            }

            _logger.LogInformation("Re-ingestion requested for dataset {Id}", id);
            
            var success = await _publishingService.ReIngestDatasetAsync(id);
            
            if (!success)
            {
                return NotFound($"Dataset with ID {id} not found or cannot be re-ingested (must be in batch mode)");
            }

            return Ok(new { message = "Dataset re-ingestion initiated successfully", datasetId = id });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error re-ingesting dataset {Id}", id);
            return StatusCode(500, "An error occurred while re-ingesting the dataset");
        }
    }

    [HttpPut("datasets/{id}/mode")]
    public async Task<ActionResult> UpdatePublishingMode(string id, [FromBody] UpdateModeRequest request)
    {
        try
        {
            if (string.IsNullOrEmpty(id))
            {
                _logger.LogWarning("Dataset ID is null or empty");
                return BadRequest("Dataset ID is required");
            }

            if (request == null)
            {
                _logger.LogWarning("Mode update request is null");
                return BadRequest("Mode update request is required");
            }

            _logger.LogInformation("Updating publishing mode for dataset {Id} to {Mode}. Request: {@Request}", 
                id, request.Mode, request);
            
            var success = await _publishingService.UpdatePublishingModeAsync(id, request.Mode, request.StreamConfig);
            
            if (!success)
            {
                _logger.LogWarning("Failed to update publishing mode for dataset {Id} - dataset not found", id);
                return NotFound($"Dataset with ID {id} not found");
            }

            _logger.LogInformation("Successfully updated publishing mode for dataset {Id} to {Mode}", id, request.Mode);
            return Ok(new { message = $"Publishing mode updated to {request.Mode}", datasetId = id, mode = request.Mode });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating publishing mode for dataset {Id}", id);
            return StatusCode(500, "An error occurred while updating the publishing mode");
        }
    }

    [HttpPost("datasets/{id}/stop")]
    public async Task<ActionResult> StopStreaming(string id)
    {
        try
        {
            if (string.IsNullOrEmpty(id))
            {
                return BadRequest("Dataset ID is required");
            }

            _logger.LogInformation("Stop streaming requested for dataset {Id}", id);
            
            var success = await _publishingService.StopStreamingAsync(id);
            
            if (!success)
            {
                return NotFound($"Dataset with ID {id} not found");
            }

            return Ok(new { message = "Streaming stopped successfully", datasetId = id });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error stopping streaming for dataset {Id}", id);
            return StatusCode(500, "An error occurred while stopping streaming");
        }
    }

    [HttpPost("datasets/{id}/start")]
    public async Task<ActionResult> StartStreaming(string id)
    {
        try
        {
            if (string.IsNullOrEmpty(id))
            {
                return BadRequest("Dataset ID is required");
            }

            _logger.LogInformation("Start streaming requested for dataset {Id}", id);
            
            var success = await _publishingService.StartStreamingAsync(id);
            
            if (!success)
            {
                return NotFound($"Dataset with ID {id} not found");
            }

            return Ok(new { message = "Streaming started successfully", datasetId = id });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error starting streaming for dataset {Id}", id);
            return StatusCode(500, "An error occurred while starting streaming");
        }
    }

    [HttpPost("datasets/{id}/pause")]
    public async Task<ActionResult> PauseStreaming(string id)
    {
        try
        {
            if (string.IsNullOrEmpty(id))
            {
                return BadRequest("Dataset ID is required");
            }

            _logger.LogInformation("Pause streaming requested for dataset {Id}", id);
            
            var success = await _publishingService.PauseStreamingAsync(id);
            
            if (!success)
            {
                return NotFound($"Dataset with ID {id} not found");
            }

            return Ok(new { message = "Streaming paused successfully", datasetId = id });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error pausing streaming for dataset {Id}", id);
            return StatusCode(500, "An error occurred while pausing streaming");
        }
    }

    [HttpPost("datasets/{id}/update-progress")]
    public async Task<ActionResult> UpdateStreamingProgress(string id, [FromBody] UpdateStreamingProgressRequest request)
    {
        try
        {
            if (string.IsNullOrEmpty(id))
            {
                return BadRequest("Dataset ID is required");
            }

            if (!Guid.TryParse(id, out var guid))
            {
                return BadRequest("Invalid dataset ID format");
            }

            if (request == null)
            {
                return BadRequest("Progress update data is required");
            }

            _logger.LogDebug("Update streaming progress for dataset {Id}: {PointsSent} points, position {Position}", 
                id, request.PointsSent, request.CurrentPosition);
            
            var success = await _publishingService.UpdateStreamingProgressAsync(guid, request.PointsSent, request.CurrentPosition);
            
            if (!success)
            {
                return NotFound($"Dataset with ID {id} not found or not configured for streaming");
            }

            return Ok(new { message = "Streaming progress updated successfully" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating streaming progress for dataset {Id}", id);
            return StatusCode(500, "An error occurred while updating streaming progress");
        }
    }

    [HttpPost("datasets/{id}/update-stats")]
    public async Task<ActionResult> UpdateStreamingStats(string id, [FromBody] UpdateStreamingStatsRequest request)
    {
        try
        {
            if (string.IsNullOrEmpty(id))
            {
                return BadRequest("Dataset ID is required");
            }

            if (!Guid.TryParse(id, out var guid))
            {
                return BadRequest("Invalid dataset ID format");
            }

            if (request == null)
            {
                return BadRequest("Stats update data is required");
            }

            _logger.LogDebug("Update streaming stats for dataset {Id}: active={IsActive}, cycle={CycleCount}", 
                id, request.IsActive, request.CycleCount);
            
            var success = await _publishingService.UpdateStreamingStatsAsync(guid, request.IsActive, request.CycleCount);
            
            if (!success)
            {
                return NotFound($"Dataset with ID {id} not found or not configured for streaming");
            }

            return Ok(new { message = "Streaming stats updated successfully" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating streaming stats for dataset {Id}", id);
            return StatusCode(500, "An error occurred while updating streaming stats");
        }
    }
}
