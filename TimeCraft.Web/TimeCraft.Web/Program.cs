
using TimeCraft.Web.Services;
using TimeCraft.Web.Services.Interfaces;
using TimeCraft.Web.Services.Implementations;
using TimeCraft.Web.Settings;
using System.Text.Json.Serialization;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllersWithViews()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter());
        options.JsonSerializerOptions.PropertyNamingPolicy = System.Text.Json.JsonNamingPolicy.CamelCase;
    });

// Add HTTP client for Python API communication
builder.Services.AddHttpClient<IPythonApiService, PythonApiService>();

// Configure settings
builder.Services.Configure<PublishingSettings>(
    builder.Configuration.GetSection("Publishing"));

// Add publishing services
builder.Services.AddScoped<IPublishingService, PublishingService>();
builder.Services.AddScoped<IEventHubPublisher, EventHubPublisher>();
builder.Services.AddScoped<IOpcUaDeltaFramePublisher, OpcUaDeltaFramePublisher>();

// Add background service for publishing
builder.Services.AddHostedService<PublishingBackgroundService>();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseRouting();

// Add authentication and authorization middleware
app.UseAuthentication();
app.UseAuthorization();

// Enable API controller routing
app.MapControllers();

app.MapControllerRoute(name: "default", pattern: "{controller}/{action=Index}/{id?}");

app.MapFallbackToFile("index.html");

app.Run();
