using System.Text;
using System.Text.Json;
using TimeCraft.Web.Models;

namespace TimeCraft.Web.Services;

public class PythonApiService : IPythonApiService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<PythonApiService> _logger;
    private readonly string _pythonApiBaseUrl;

    public PythonApiService(
        HttpClient httpClient,
        ILogger<PythonApiService> logger,
        IConfiguration configuration
    )
    {
        _httpClient = httpClient;
        _logger = logger;
        _pythonApiBaseUrl =
            configuration.GetValue<string>("PythonApi:BaseUrl") ?? "http://localhost:8080";

        // Set longer timeout for Azure OpenAI API calls with reflection which can take time
        _httpClient.Timeout = TimeSpan.FromMinutes(5); // 5 minutes for reflection operations
    }

    public async Task<GenerateTagsResponse> GenerateTagsAsync(GenerateTagsRequest request)
    {
        try
        {
            _logger.LogInformation(
                "Calling Python API /generate-tags with text: {Text}",
                request.Text
            );

            var json = JsonSerializer.Serialize(new 
            { 
                text_description = request.Text,
                time_horizon = request.TimeHorizon != null ? new
                {
                    period = request.TimeHorizon.Period,
                    unit = request.TimeHorizon.Unit,
                    granularity = request.TimeHorizon.Granularity,
                    total_points = request.TimeHorizon.TotalPoints
                } : null
            });
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync(
                $"{_pythonApiBaseUrl}/generate-tags",
                content
            );
            response.EnsureSuccessStatusCode();

            var responseJson = await response.Content.ReadAsStringAsync();
            _logger.LogInformation("Python API response: {Response}", responseJson);

            var result = JsonSerializer.Deserialize<JsonElement>(responseJson);

            var tags = new List<GeneratedTag>();

            // Check for enhanced response structure first (with tag_details)
            if (result.TryGetProperty("tag_details", out var tagDetailsElement) && 
                tagDetailsElement.ValueKind == JsonValueKind.Array)
            {
                _logger.LogInformation("Processing enhanced tag response with tag_details");
                
                foreach (var tagDetailElement in tagDetailsElement.EnumerateArray())
                {
                    if (tagDetailElement.ValueKind == JsonValueKind.Object)
                    {
                        var tagName = tagDetailElement.TryGetProperty("tag", out var tagProp) 
                            ? tagProp.GetString() ?? string.Empty 
                            : string.Empty;
                        var unit = tagDetailElement.TryGetProperty("unit", out var unitProp) 
                            ? unitProp.GetString() ?? "units" 
                            : "units";
                        var description = tagDetailElement.TryGetProperty("description", out var descProp) 
                            ? descProp.GetString() ?? $"{tagName} sensor" 
                            : $"{tagName} sensor";

                        if (!string.IsNullOrEmpty(tagName))
                        {
                            tags.Add(new GeneratedTag
                            {
                                Tag = tagName,
                                Description = $"{description} ({unit})"
                            });
                        }
                    }
                }
            }
            // Fallback to simple tags array (legacy format)
            else if (result.TryGetProperty("tags", out var tagsElement) && 
                     tagsElement.ValueKind == JsonValueKind.Array)
            {
                _logger.LogInformation("Processing legacy tag response with simple tags array");
                
                foreach (var tagElement in tagsElement.EnumerateArray())
                {
                    var tagName = tagElement.GetString() ?? string.Empty;
                    if (!string.IsNullOrEmpty(tagName))
                    {
                        tags.Add(new GeneratedTag
                        {
                            Tag = tagName,
                            Description = $"Generated tag: {tagName}"
                        });
                    }
                }
            }
            else
            {
                _logger.LogError(
                    "Python API response missing both 'tag_details' and 'tags' properties: {Response}",
                    responseJson
                );
                return new GenerateTagsResponse
                {
                    Success = false,
                    Message = "Invalid response format from Python API",
                    Tags = new List<GeneratedTag>()
                };
            }

            return new GenerateTagsResponse
            {
                Success = true,
                Tags = tags,
                Message = "Tags generated successfully"
            };
        }
        catch (TaskCanceledException ex) when (ex.CancellationToken.IsCancellationRequested)
        {
            _logger.LogWarning("Python API call for generate-tags was cancelled");
            return new GenerateTagsResponse
            {
                Success = false,
                Message = "Request was cancelled",
                Tags = new List<GeneratedTag>()
            };
        }
        catch (TaskCanceledException ex)
        {
            _logger.LogWarning("Python API call for generate-tags timed out after 2 minutes");
            return new GenerateTagsResponse
            {
                Success = false,
                Message =
                    "Azure OpenAI request timed out - this can happen on first calls. Please try again.",
                Tags = new List<GeneratedTag>()
            };
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "HTTP error calling Python API for generate-tags");
            return new GenerateTagsResponse
            {
                Success = false,
                Message = $"Connection error: {ex.Message}",
                Tags = new List<GeneratedTag>()
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error calling Python API for generate-tags");
            return new GenerateTagsResponse
            {
                Success = false,
                Message = ex.Message,
                Tags = new List<GeneratedTag>()
            };
        }
    }

    public async Task<GenerateTimeSeriesResponse> GenerateTimeSeriesAsync(
        GenerateTimeSeriesRequest request
    )
    {
        try
        {
            _logger.LogInformation(
                "Calling Python API /generate-timeseries-for-tag with tag: {Tag}, scenario: {Scenario}",
                request.Tag,
                request.Scenario
            );

            // Calculate sequence length from time horizon or use default
            int sequenceLength = request.TimeHorizon?.TotalPoints ?? 168;
            
            // Python API expects tag_name and text_description fields
            var json = JsonSerializer.Serialize(
                new
                {
                    tag_name = request.Tag,
                    text_description = request.Scenario,
                    sequence_length = sequenceLength,
                    tag_index = 0,
                    model_name = "gpt-4o",
                    temperature = 0.0,
                    time_horizon = request.TimeHorizon != null ? new
                    {
                        period = request.TimeHorizon.Period,
                        unit = request.TimeHorizon.Unit,
                        granularity = request.TimeHorizon.Granularity,
                        total_points = request.TimeHorizon.TotalPoints,
                        batch_size = request.TimeHorizon.BatchSize,
                        batch_index = request.TimeHorizon.BatchIndex
                    } : null
                }
            );
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            _logger.LogInformation("Sending JSON to Python API: {Json}", json);

            var response = await _httpClient.PostAsync(
                $"{_pythonApiBaseUrl}/generate-timeseries-for-tag",
                content
            );

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError(
                    "Python API returned error {StatusCode}: {ErrorContent}",
                    response.StatusCode,
                    errorContent
                );
                throw new HttpRequestException(
                    $"Python API error {response.StatusCode}: {errorContent}"
                );
            }

            response.EnsureSuccessStatusCode();

            var responseJson = await response.Content.ReadAsStringAsync();
            _logger.LogInformation("Python API response for time series: {Response}", responseJson);
            var result = JsonSerializer.Deserialize<JsonElement>(responseJson);

            // Parse the Python API response structure
            var success =
                result.TryGetProperty("status", out var statusElement)
                && statusElement.GetString() == "success";

            var message = result.TryGetProperty("message", out var messageElement)
                ? messageElement.GetString() ?? "Time series generated"
                : "Time series generated";

            var tagName = result.TryGetProperty("tag_name", out var tagNameElement)
                ? tagNameElement.GetString() ?? ""
                : "";

            var timeSeries = new List<double>();
            if (
                result.TryGetProperty("timeseries", out var timeseriesElement)
                && timeseriesElement.ValueKind == JsonValueKind.Array
            )
            {
                foreach (var item in timeseriesElement.EnumerateArray())
                {
                    if (item.ValueKind == JsonValueKind.Number)
                    {
                        timeSeries.Add(item.GetDouble());
                    }
                }
            }

            // Use timestamps from Python API response, or generate fallback timestamps
            var timestamps = new List<string>();
            
            // Check if Python API returned timestamps
            if (
                result.TryGetProperty("timestamps", out var timestampsElement)
                && timestampsElement.ValueKind == JsonValueKind.Array
            )
            {
                foreach (var timestampItem in timestampsElement.EnumerateArray())
                {
                    if (timestampItem.ValueKind == JsonValueKind.String)
                    {
                        timestamps.Add(timestampItem.GetString() ?? "");
                    }
                }
                _logger.LogInformation("Using {Count} timestamps returned from Python API", timestamps.Count);
            }
            
            // Fallback: generate timestamps if not provided by Python API (for backward compatibility)
            if (timestamps.Count == 0 && timeSeries.Count > 0)
            {
                var startTime = DateTime.UtcNow.AddHours(-timeSeries.Count);
                for (int i = 0; i < timeSeries.Count; i++)
                {
                    timestamps.Add(startTime.AddHours(i).ToString("yyyy-MM-ddTHH:mm:ssZ"));
                }
                _logger.LogWarning("Generated fallback timestamps as Python API did not return timestamps");
            }

            return new GenerateTimeSeriesResponse
            {
                Success = success,
                Message = message,
                TagName = tagName,
                TimeSeries = timeSeries,
                Timestamps = timestamps
            };
        }
        catch (TaskCanceledException ex) when (ex.CancellationToken.IsCancellationRequested)
        {
            _logger.LogWarning("Python API call for generate-timeseries-for-tag was cancelled");
            return new GenerateTimeSeriesResponse
            {
                Success = false,
                Message = "Request was cancelled",
                TagName = request.Tag,
                TimeSeries = new List<double>(),
                Timestamps = new List<string>()
            };
        }
        catch (TaskCanceledException ex)
        {
            _logger.LogWarning(
                "Python API call for generate-timeseries-for-tag timed out after 2 minutes"
            );
            return new GenerateTimeSeriesResponse
            {
                Success = false,
                Message =
                    "Azure OpenAI request timed out - this can happen on first calls. Please try again.",
                TagName = request.Tag,
                TimeSeries = new List<double>(),
                Timestamps = new List<string>()
            };
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "HTTP error calling Python API for generate-timeseries-for-tag");
            return new GenerateTimeSeriesResponse
            {
                Success = false,
                Message = $"Connection error: {ex.Message}",
                TagName = request.Tag,
                TimeSeries = new List<double>(),
                Timestamps = new List<string>()
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(
                ex,
                "Unexpected error calling Python API for generate-timeseries-for-tag"
            );
            return new GenerateTimeSeriesResponse
            {
                Success = false,
                Message = ex.Message,
                TagName = request.Tag,
                TimeSeries = new List<double>(),
                Timestamps = new List<string>()
            };
        }
    }

    public async Task<RefinePromptResponse> RefinePromptAsync(RefinePromptRequest request)
    {
        try
        {
            var json = JsonSerializer.Serialize(new { prompt = request.Prompt });
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync(
                $"{_pythonApiBaseUrl}/refine-prompt",
                content
            );
            response.EnsureSuccessStatusCode();

            var responseJson = await response.Content.ReadAsStringAsync();
            var result = JsonSerializer.Deserialize<JsonElement>(responseJson);

            var refinedPrompt = result.TryGetProperty("refined_prompt", out var promptElement)
                ? promptElement.GetString()
                : string.Empty;

            return new RefinePromptResponse { RefinedPrompt = refinedPrompt };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error calling Python API for refine-prompt");
            throw;
        }
    }

    public async Task<GenerateAnomalyResponse> GenerateAnomalyAsync(GenerateAnomalyRequest request)
    {
        try
        {
            _logger.LogInformation(
                "Calling Python API /generate-anomaly for tag: {TagName}, injection range: {StartIndex}-{EndIndex}",
                request.TagName,
                request.InjectionStartIndex,
                request.InjectionEndIndex
            );

            var json = JsonSerializer.Serialize(new
            {
                tag_name = request.TagName,
                tag_description = request.TagDescription,
                existing_timeseries = request.ExistingTimeSeries,
                injection_start_index = request.InjectionStartIndex,
                injection_end_index = request.InjectionEndIndex,
                anomaly_type = request.AnomalyType,
                anomaly_description = request.AnomalyDescription,
                severity = request.Severity
            });

            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync(
                $"{_pythonApiBaseUrl}/generate-anomaly",
                content
            );
            response.EnsureSuccessStatusCode();

            var responseJson = await response.Content.ReadAsStringAsync();
            _logger.LogInformation("Python API anomaly response: {Response}", responseJson);

            var result = JsonSerializer.Deserialize<JsonElement>(responseJson);

            var success = result.TryGetProperty("success", out var successElement) && successElement.GetBoolean();
            var message = result.TryGetProperty("message", out var messageElement) ? messageElement.GetString() ?? string.Empty : string.Empty;
            var tagName = result.TryGetProperty("tag_name", out var tagNameElement) ? tagNameElement.GetString() ?? request.TagName : request.TagName;

            var modifiedTimeSeries = new List<double>();
            if (result.TryGetProperty("modified_timeseries", out var timeseriesElement) && timeseriesElement.ValueKind == JsonValueKind.Array)
            {
                foreach (var item in timeseriesElement.EnumerateArray())
                {
                    if (item.ValueKind == JsonValueKind.Number)
                    {
                        modifiedTimeSeries.Add(item.GetDouble());
                    }
                }
            }

            var anomalyStartIndex = result.TryGetProperty("anomaly_start_index", out var startElement) ? startElement.GetInt32() : request.InjectionStartIndex;
            var anomalyEndIndex = result.TryGetProperty("anomaly_end_index", out var endElement) ? endElement.GetInt32() : request.InjectionEndIndex;
            var anomalyType = result.TryGetProperty("anomaly_type", out var typeElement) ? typeElement.GetString() ?? request.AnomalyType : request.AnomalyType;

            // Generate timestamps for the modified time series
            var timestamps = new List<string>();
            var startTime = DateTime.UtcNow.AddHours(-modifiedTimeSeries.Count);
            for (int i = 0; i < modifiedTimeSeries.Count; i++)
            {
                timestamps.Add(startTime.AddHours(i).ToString("yyyy-MM-ddTHH:mm:ssZ"));
            }

            return new GenerateAnomalyResponse
            {
                Success = success,
                Message = message,
                TagName = tagName,
                ModifiedTimeSeries = modifiedTimeSeries,
                Timestamps = timestamps,
                AnomalyStartIndex = anomalyStartIndex,
                AnomalyEndIndex = anomalyEndIndex,
                AnomalyType = anomalyType
            };
        }
        catch (TaskCanceledException)
        {
            _logger.LogWarning("Python API call for generate-anomaly timed out");
            return new GenerateAnomalyResponse
            {
                Success = false,
                Message = "Anomaly generation timed out. Please try again.",
                TagName = request.TagName,
                ModifiedTimeSeries = new List<double>(),
                Timestamps = new List<string>()
            };
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "HTTP error calling Python API for generate-anomaly");
            return new GenerateAnomalyResponse
            {
                Success = false,
                Message = $"Connection error: {ex.Message}",
                TagName = request.TagName,
                ModifiedTimeSeries = new List<double>(),
                Timestamps = new List<string>()
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error calling Python API for generate-anomaly");
            return new GenerateAnomalyResponse
            {
                Success = false,
                Message = ex.Message,
                TagName = request.TagName,
                ModifiedTimeSeries = new List<double>(),
                Timestamps = new List<string>()
            };
        }
    }

    public async Task<GenerateTimeSeriesResponse> RegenerateTimeSeriesAsync(RegenerateTimeSeriesRequest request)
    {
        try
        {
            _logger.LogInformation(
                "Regenerating time series for tag: {Tag} with additional instructions: {Instructions}",
                request.Tag,
                request.Instructions ?? "None"
            );

            // Create enhanced scenario with instructions if provided
            var enhancedScenario = request.Scenario;
            if (!string.IsNullOrWhiteSpace(request.Instructions))
            {
                enhancedScenario = $"{request.Scenario}\n\nAdditional Instructions: {request.Instructions}";
            }

            var json = JsonSerializer.Serialize(
                new
                {
                    tag_name = request.Tag,
                    text_description = enhancedScenario,
                    sequence_length = request.SequenceLength,
                    tag_index = request.TagIndex,
                    model_name = "gpt-4o",
                    temperature = 0.0,
                    regeneration_request = true, // Flag to indicate this is a regeneration
                    original_instructions = request.Instructions,
                    time_horizon = request.TimeHorizon != null ? new
                    {
                        period = request.TimeHorizon.Period,
                        unit = request.TimeHorizon.Unit,
                        granularity = request.TimeHorizon.Granularity,
                        total_points = request.TimeHorizon.TotalPoints,
                        batch_size = request.TimeHorizon.BatchSize,
                        batch_index = request.TimeHorizon.BatchIndex
                    } : null
                }
            );
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            _logger.LogInformation("Sending regeneration request to Python API: {Json}", json);

            var response = await _httpClient.PostAsync(
                $"{_pythonApiBaseUrl}/generate-timeseries-for-tag",
                content
            );

            if (!response.IsSuccessStatusCode)
            {
                var errorContent = await response.Content.ReadAsStringAsync();
                _logger.LogError(
                    "Python API returned error {StatusCode} for regeneration: {ErrorContent}",
                    response.StatusCode,
                    errorContent
                );
                throw new HttpRequestException(
                    $"Python API error {response.StatusCode}: {errorContent}"
                );
            }

            response.EnsureSuccessStatusCode();

            var responseJson = await response.Content.ReadAsStringAsync();
            _logger.LogInformation("Python API regeneration response: {Response}", responseJson);
            var result = JsonSerializer.Deserialize<JsonElement>(responseJson);

            // Parse the Python API response structure
            var success =
                result.TryGetProperty("status", out var statusElement)
                && statusElement.GetString() == "success";

            var message = result.TryGetProperty("message", out var messageElement)
                ? messageElement.GetString() ?? "Time series regenerated"
                : "Time series regenerated";

            var tagName = result.TryGetProperty("tag_name", out var tagNameElement)
                ? tagNameElement.GetString()
                : request.Tag;

            var timeSeries = new List<double>();
            if (result.TryGetProperty("timeseries", out var timeseriesElement) &&
                timeseriesElement.ValueKind == JsonValueKind.Array)
            {
                foreach (var item in timeseriesElement.EnumerateArray())
                {
                    if (item.ValueKind == JsonValueKind.Number && item.TryGetDouble(out var value))
                    {
                        timeSeries.Add(value);
                    }
                }
            }

            var timestamps = new List<string>();
            if (result.TryGetProperty("timestamps", out var timestampsElement) &&
                timestampsElement.ValueKind == JsonValueKind.Array)
            {
                foreach (var item in timestampsElement.EnumerateArray())
                {
                    if (item.ValueKind == JsonValueKind.String)
                    {
                        var timestamp = item.GetString();
                        if (!string.IsNullOrEmpty(timestamp))
                        {
                            timestamps.Add(timestamp);
                        }
                    }
                }
            }

            return new GenerateTimeSeriesResponse
            {
                Success = success,
                Message = message,
                TagName = tagName,
                TimeSeries = timeSeries,
                Timestamps = timestamps
            };
        }
        catch (TaskCanceledException ex) when (ex.CancellationToken.IsCancellationRequested)
        {
            _logger.LogWarning("Python API call for regenerate-timeseries was cancelled");
            return new GenerateTimeSeriesResponse
            {
                Success = false,
                Message = "Request was cancelled",
                TagName = request.Tag,
                TimeSeries = new List<double>(),
                Timestamps = new List<string>()
            };
        }
        catch (TaskCanceledException ex)
        {
            _logger.LogWarning("Python API call for regenerate-timeseries timed out");
            return new GenerateTimeSeriesResponse
            {
                Success = false,
                Message = "Request timed out - please try again.",
                TagName = request.Tag,
                TimeSeries = new List<double>(),
                Timestamps = new List<string>()
            };
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "HTTP error calling Python API for regenerate-timeseries");
            return new GenerateTimeSeriesResponse
            {
                Success = false,
                Message = $"Connection error: {ex.Message}",
                TagName = request.Tag,
                TimeSeries = new List<double>(),
                Timestamps = new List<string>()
            };
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error calling Python API for regenerate-timeseries");
            return new GenerateTimeSeriesResponse
            {
                Success = false,
                Message = ex.Message,
                TagName = request.Tag,
                TimeSeries = new List<double>(),
                Timestamps = new List<string>()
            };
        }
    }
}
