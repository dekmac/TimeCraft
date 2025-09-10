using TimeCraft.Web.Models;

namespace TimeCraft.Web.Services;

public interface IPythonApiService
{
    Task<GenerateTagsResponse> GenerateTagsAsync(GenerateTagsRequest request);
    Task<GenerateTimeSeriesResponse> GenerateTimeSeriesAsync(GenerateTimeSeriesRequest request);
    Task<RefinePromptResponse> RefinePromptAsync(RefinePromptRequest request);
    Task<GenerateAnomalyResponse> GenerateAnomalyAsync(GenerateAnomalyRequest request);
}
