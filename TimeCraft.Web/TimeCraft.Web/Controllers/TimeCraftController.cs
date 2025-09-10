using Microsoft.AspNetCore.Mvc;
using TimeCraft.Web.Models;
using TimeCraft.Web.Models.Publishing;
using TimeCraft.Web.Services;
using TimeCraft.Web.Services.Interfaces;

namespace TimeCraft.Web.Controllers;

[ApiController]
[Route("api/[controller]")]
public class TimeCraftController : ControllerBase
{
    private readonly IPythonApiService _pythonApiService;
    private readonly IPublishingService _publishingService;
    private readonly ILogger<TimeCraftController> _logger;

    public TimeCraftController(
        IPythonApiService pythonApiService, 
        IPublishingService publishingService,
        ILogger<TimeCraftController> logger)
    {
        _pythonApiService = pythonApiService;
        _publishingService = publishingService;
        _logger = logger;
    }

    [HttpGet("test")]
    public IActionResult Test()
    {
        _logger.LogInformation("=== Test endpoint called ===");
        return Ok(new { message = "API routing is working!", timestamp = DateTime.UtcNow });
    }

    [HttpPost("generate-tags")]
    public async Task<ActionResult<GenerateTagsResponse>> GenerateTags([FromBody] GenerateTagsRequest request)
    {
        _logger.LogInformation("=== GenerateTags method called ===");
        _logger.LogInformation("Request object: {Request}", request != null ? "NOT NULL" : "NULL");
        
        if (request != null)
        {
            _logger.LogInformation("Request.Text: {Text}", request.Text ?? "NULL");
        }
        
        try
        {
            if (request == null)
            {
                _logger.LogWarning("Request object is null");
                return BadRequest("Request is required");
            }
            
            if (string.IsNullOrWhiteSpace(request.Text))
            {
                _logger.LogWarning("Request.Text is null or empty");
                return BadRequest("Text is required");
            }

            _logger.LogInformation("Calling Python API service...");
            var result = await _pythonApiService.GenerateTagsAsync(request);
            _logger.LogInformation("Python API service completed");
            
            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating tags for text: {Text}", request?.Text);
            return StatusCode(500, "An error occurred while generating tags");
        }
    }

    [HttpPost("generate-timeseries")]
    public async Task<ActionResult<GenerateTimeSeriesResponse>> GenerateTimeSeries([FromBody] GenerateTimeSeriesRequest request)
    {
        _logger.LogInformation("=== GenerateTimeSeries method called ===");
        _logger.LogInformation("Request object: {Request}", request != null ? "NOT NULL" : "NULL");
        
        if (request != null)
        {
            _logger.LogInformation("Request.Tag: {Tag}, Request.Scenario: {Scenario}", request.Tag ?? "NULL", request.Scenario ?? "NULL");
        }
        
        try
        {
            if (request == null)
            {
                _logger.LogWarning("Request object is null");
                return BadRequest("Request is required");
            }
            
            if (string.IsNullOrWhiteSpace(request.Tag))
            {
                _logger.LogWarning("Request.Tag is null or empty");
                return BadRequest("Tag is required");
            }
            
            if (string.IsNullOrWhiteSpace(request.Scenario))
            {
                _logger.LogWarning("Request.Scenario is null or empty");
                return BadRequest("Scenario is required");
            }

            _logger.LogInformation("Calling Python API service for time series...");
            var result = await _pythonApiService.GenerateTimeSeriesAsync(request);
            _logger.LogInformation("Python API service completed for time series");
            
            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating time series for tag: {Tag}", request?.Tag);
            return StatusCode(500, "An error occurred while generating time series data");
        }
    }

    [HttpPost("refine-prompt")]
    public async Task<ActionResult<RefinePromptResponse>> RefinePrompt([FromBody] RefinePromptRequest request)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.Prompt))
            {
                return BadRequest("Prompt is required");
            }

            var result = await _pythonApiService.RefinePromptAsync(request);
            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error refining prompt: {Prompt}", request.Prompt);
            return StatusCode(500, "An error occurred while refining the prompt");
        }
    }

    [HttpPost("generate-anomaly")]
    public async Task<ActionResult<GenerateAnomalyResponse>> GenerateAnomaly([FromBody] GenerateAnomalyRequest request)
    {
        _logger.LogInformation("=== GenerateAnomaly method called ===");
        
        try
        {
            if (request == null)
            {
                _logger.LogWarning("Request object is null");
                return BadRequest("Request is required");
            }
            
            if (string.IsNullOrWhiteSpace(request.TagName))
            {
                _logger.LogWarning("Request.TagName is null or empty");
                return BadRequest("Tag name is required");
            }

            if (request.ExistingTimeSeries == null || !request.ExistingTimeSeries.Any())
            {
                _logger.LogWarning("Request.ExistingTimeSeries is null or empty");
                return BadRequest("Existing time series data is required");
            }

            if (request.InjectionStartIndex < 0 || request.InjectionEndIndex >= request.ExistingTimeSeries.Count || request.InjectionStartIndex > request.InjectionEndIndex)
            {
                _logger.LogWarning("Invalid injection indices: {StartIndex}-{EndIndex} for series length {Length}", 
                    request.InjectionStartIndex, request.InjectionEndIndex, request.ExistingTimeSeries.Count);
                return BadRequest("Invalid injection indices");
            }

            _logger.LogInformation("Calling Python API service for anomaly generation...");
            var result = await _pythonApiService.GenerateAnomalyAsync(request);
            _logger.LogInformation("Python API service completed for anomaly generation");
            
            return Ok(result);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating anomaly for tag: {TagName}", request?.TagName);
            return StatusCode(500, "An error occurred while generating anomaly data");
        }
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
                _logger.LogWarning("Invalid model state for dataset publish request");
                return BadRequest(ModelState);
            }

            if (request.Tags == null || !request.Tags.Any())
            {
                _logger.LogWarning("No tags provided for dataset publishing");
                return BadRequest("At least one tag is required for dataset publishing");
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
}
