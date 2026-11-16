using Microsoft.EntityFrameworkCore;

namespace BirdLab;

public record AiResult(string Species, double Confidence, string Description);

public class BirdRecord
{
    public int Id { get; set; }
    public string FileName { get; set; } = "";
    public string Species { get; set; } = "";
    public double Confidence { get; set; }
    public string Description { get; set; } = "";
    public DateTime Date { get; set; } = DateTime.UtcNow;
}

public class AppDb(DbContextOptions<AppDb> options) : DbContext(options)
{
    public DbSet<BirdRecord> History => Set<BirdRecord>();
}

public class BirdService(AppDb db, IHttpClientFactory http)
{
    // Метод 1: Отправить фото в Python AI и сохранить в БД
    public async Task<BirdRecord> AnalyzeAndSaveAsync(IFormFile file)
    {
        using var form = new MultipartFormDataContent();
        form.Add(new StreamContent(file.OpenReadStream()), "file", file.FileName);

        var response = await http.CreateClient("ai").PostAsync("/predict", form);
        var ai = await response.Content.ReadFromJsonAsync<AiResult>();

        var record = new BirdRecord
        {
            FileName = file.FileName,
            Species = ai!.Species,
            Confidence = ai.Confidence,
            Description = ai.Description
        };

        db.History.Add(record);
        await db.SaveChangesAsync();
        return record;
    }

    // Метод 2: Получить историю (с поиском, если передали текст)
    public async Task<List<BirdRecord>> GetHistoryAsync(string? search)
    {
        var query = db.History.AsQueryable();
        if (!string.IsNullOrWhiteSpace(search))
            query = query.Where(x => x.Species.Contains(search));

        return await query.OrderByDescending(x => x.Id).ToListAsync();
    }

    // Метод 3: Посчитать статистику по видам
    public async Task<object> GetStatsAsync()
    {
        return await db.History
            .GroupBy(x => x.Species)
            .Select(g => new { species = g.Key, count = g.Count() })
            .ToListAsync();
    }
}