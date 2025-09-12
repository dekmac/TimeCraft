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
}
