using System.Net;
using System.Text;
using System.Text.Json;
using BirdLab;
using Microsoft.AspNetCore.Http;
using Microsoft.EntityFrameworkCore;

namespace central_api.Tests;

public class BirdServiceTests
{
    // Создаем чистую БД в памяти для каждого теста
    private static AppDb CreateInMemoryDb()
    {
        var options = new DbContextOptionsBuilder<AppDb>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;
        return new AppDb(options);
    }

    // Простая заглушка HTTP-клиента, имитирующая ответ от Python AI
    private static IHttpClientFactory CreateFakeAiHttpClient(string species, double confidence)
    {
        var json = JsonSerializer.Serialize(new { Species = species, Confidence = confidence, Description = "Test bird" });
        var handler = new FakeHttpHandler(json);
        var client = new HttpClient(handler) { BaseAddress = new Uri("http://fake-ai") };
        return new FakeHttpClientFactory(client);
    }

    [Fact]
    public async Task AnalyzeAndSaveAsync_SavesRecordToDatabase()
    {
        // Arrange
        using var db = CreateInMemoryDb();
        var http = CreateFakeAiHttpClient("eagle", 96.4);
        var service = new BirdService(db, http);

        var stream = new MemoryStream(Encoding.UTF8.GetBytes("fake-image-bytes"));
        var file = new FormFile(stream, 0, stream.Length, "file", "eagle.jpg");

        // Act
        var result = await service.AnalyzeAndSaveAsync(file);

        // Assert
        Assert.Equal("eagle", result.Species);
        Assert.Equal(96.4, result.Confidence);
        Assert.Equal(1, await db.History.CountAsync());
    }

    [Fact]
    public async Task GetHistoryAsync_FiltersBySpeciesName()
    {
        // Arrange
        using var db = CreateInMemoryDb();
        db.History.AddRange(
            new BirdRecord { FileName = "1.jpg", Species = "eagle", Confidence = 90 },
            new BirdRecord { FileName = "2.jpg", Species = "sparrow", Confidence = 80 }
        );
        await db.SaveChangesAsync();

        var service = new BirdService(db, CreateFakeAiHttpClient("", 0));

        // Act
        var filtered = await service.GetHistoryAsync("eagle");

        // Assert
        Assert.Single(filtered);
        Assert.Equal("eagle", filtered[0].Species);
    }

    [Fact]
    public async Task GetStatsAsync_GroupsSpeciesCorrectly()
    {
        // Arrange
        using var db = CreateInMemoryDb();
        db.History.AddRange(
            new BirdRecord { Species = "owl" },
            new BirdRecord { Species = "owl" },
            new BirdRecord { Species = "duck" }
        );
        await db.SaveChangesAsync();

        var service = new BirdService(db, CreateFakeAiHttpClient("", 0));

        // Act
        var stats = await service.GetStatsAsync();
        var json = JsonSerializer.Serialize(stats);

        // Assert
        Assert.Contains("\"species\":\"owl\",\"count\":2", json);
        Assert.Contains("\"species\":\"duck\",\"count\":1", json);
    }
}

// Вспомогательные классы для имитации ответа AI без реального HTTP-запроса
class FakeHttpHandler(string responseJson) : HttpMessageHandler
{
    protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        => Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK)
        {
            Content = new StringContent(responseJson, Encoding.UTF8, "application/json")
        });
}

class FakeHttpClientFactory(HttpClient client) : IHttpClientFactory
{
    public HttpClient CreateClient(string name) => client;
}