using TimeCraft.Web.Models.Publishing;

namespace TimeCraft.Web.Services.Interfaces;

public interface IEventHubPublisher
{
    Task PublishAsync(PublishRecord publishRecord, CancellationToken cancellationToken = default);
}
