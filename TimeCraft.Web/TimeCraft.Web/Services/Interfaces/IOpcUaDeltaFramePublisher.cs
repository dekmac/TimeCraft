using TimeCraft.Web.Models;
using TimeCraft.Web.Models.Publishing;

namespace TimeCraft.Web.Services.Interfaces;

public interface IOpcUaDeltaFramePublisher
{
    Task PublishDatasetAsync(PublishRecord publishRecord, CancellationToken cancellationToken = default);
    OpcUaDeltaFrame CreateDeltaFrame(DatasetTag tag, List<TimeSeriesDataPoint> dataPoints, OpcUaSettings opcUaSettings, int sequenceNumber);
    Task<bool> ValidateOpcUaConfigurationAsync(OpcUaSettings opcUaSettings);
}
