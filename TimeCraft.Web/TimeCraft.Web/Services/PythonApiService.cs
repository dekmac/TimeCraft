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

        // Set longer timeout for Azure OpenAI API calls which can take time
        _httpClient.Timeout = TimeSpan.FromMinutes(2);
    }

    public async Task<GenerateTagsResponse> GenerateTagsAsync(GenerateTagsRequest request)
    {
        try
        {
            _logger.LogInformation(
                "Calling Python API /generate-tags with text: {Text}",
                request.Text
            );

            var json = JsonSerializer.Serialize(new { text_description = request.Text });
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync(
                $"{_pythonApiBaseUrl}/generate-tags",
                content
            );
            response.EnsureSuccessStatusCode();

            var responseJson = await response.Content.ReadAsStringAsync();
            _logger.LogInformation("Python API response: {Response}", responseJson);

            var result = JsonSerializer.Deserialize<JsonElement>(responseJson);

            // Check if response has expected structure
            if (!result.TryGetProperty("tags", out var tagsElement))
            {
                _logger.LogError(
                    "Python API response missing 'tags' property: {Response}",
                    responseJson
                );
                return new GenerateTagsResponse
                {
                    Success = false,
                    Message = "Invalid response format from Python API",
                    Tags = new List<GeneratedTag>()
                };
            }

            var tags = new List<GeneratedTag>();
            if (tagsElement.ValueKind == JsonValueKind.Array)
            {
                foreach (var tagElement in tagsElement.EnumerateArray())
                {
                    var tagName = tagElement.GetString() ?? string.Empty;
                    if (!string.IsNullOrEmpty(tagName))
                    {
                        tags.Add(
                            new GeneratedTag
                            {
                                Tag = tagName,
                                Description = $"Generated tag: {tagName}"
                            }
                        );
                    }
                }
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

            // Python API expects tag_name and text_description fields
            var json = JsonSerializer.Serialize(
                new
                {
                    tag_name = request.Tag,
                    text_description = request.Scenario,
                    sequence_length = 168,
                    tag_index = 0,
                    model_name = "gpt-4o",
                    temperature = 0.0
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

            // Generate timestamps for the time series (assuming hourly data)
            var timestamps = new List<string>();
            var startTime = DateTime.UtcNow.AddHours(-timeSeries.Count);
            for (int i = 0; i < timeSeries.Count; i++)
            {
                timestamps.Add(startTime.AddHours(i).ToString("yyyy-MM-ddTHH:mm:ssZ"));
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
}
