using System.Net.Http.Headers;
using System.Text.Json;
using Microsoft.EntityFrameworkCore;

namespace BirdLab;

public class BirdService(AppDb db, IHttpClientFactory http)
{
    private const long MaxFileSize = 10 * 1024 * 1024; // максимально можно 10мб

    // Отправить фото в Python AI и сохранить в БД
    public async Task<BirdRecord> AnalyzeAndSaveAsync(IFormFile file)
    {
        if (file is null || file.Length == 0)
            throw new InvalidOperationException("Файл не выбран или пустой.");

        if (file.Length > MaxFileSize)
            throw new InvalidOperationException("Размер файла не должен превышать 10 МБ.");

        await using var stream = file.OpenReadStream();

        if (!IsValidImageSignature(stream))
            throw new InvalidOperationException("Недопустимый формат файла. Загрузите фото в формате JPG, PNG или WEBP.");

        using var form = new MultipartFormDataContent();
        using var fileContent = new StreamContent(stream);
        fileContent.Headers.ContentType = new MediaTypeHeaderValue(
            string.IsNullOrWhiteSpace(file.ContentType) ? "application/octet-stream" : file.ContentType
        );
        form.Add(fileContent, "file", file.FileName);

        var response = await http.CreateClient("ai").PostAsync("/predict", form);

        if (!response.IsSuccessStatusCode)
        {
            var errorJson = await response.Content.ReadAsStringAsync();
            var detail = ExtractErrorDetail(errorJson) ?? "На фото не обнаружена птица.";
            throw new InvalidOperationException(detail);
        }

        var ai = await response.Content.ReadFromJsonAsync<AiResult>()
                 ?? throw new InvalidOperationException("Пустой ответ от AI-сервера.");

        var record = new BirdRecord
        {
            FileName = file.FileName,
            Species = ai.Species,
            Confidence = ai.Confidence,
            Description = ai.Description
        };

        db.History.Add(record);
        await db.SaveChangesAsync();
        return record;
    }

    // Получить историю (с поиском, если передали текст)
    public async Task<List<BirdRecord>> GetHistoryAsync(string? search)
    {
        var query = db.History.AsQueryable();
        if (!string.IsNullOrWhiteSpace(search))
            query = query.Where(x => x.Species.Contains(search));

        return await query.OrderByDescending(x => x.Id).ToListAsync();
    }

    // Посчитать статистику по видам
    public async Task<object> GetStatsAsync()
    {
        return await db.History
            .GroupBy(x => x.Species)
            .Select(g => new { species = g.Key, count = g.Count() })
            .ToListAsync();
    }

    private static string? ExtractErrorDetail(string json)
    {
        try
        {
            using var doc = JsonDocument.Parse(json);
            return doc.RootElement.TryGetProperty("detail", out var prop) ? prop.GetString() : null;
        }
        catch
        {
            return null;
        }
    }

    private static bool IsValidImageSignature(Stream stream)
    {
        if (stream.Length < 12) return false;

        Span<byte> header = stackalloc byte[12];
        int bytesRead = stream.Read(header);
        stream.Position = 0;

        if (bytesRead < 12) return false;

        // JPEG
        bool isJpeg = header[0] == 0xFF && header[1] == 0xD8 && header[2] == 0xFF;
        // PNG
        bool isPng = header[0] == 0x89 && header[1] == 0x50 && header[2] == 0x4E && header[3] == 0x47;
        // WEBP
        bool isWebp = header[0] == 0x52 && header[1] == 0x49 && header[2] == 0x46 && header[3] == 0x46 &&
                      header[8] == 0x57 && header[9] == 0x45 && header[10] == 0x42 && header[11] == 0x50;

        return isJpeg || isPng || isWebp;
    }
}