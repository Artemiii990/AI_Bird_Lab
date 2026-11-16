using Microsoft.AspNetCore.Mvc;

namespace BirdLab;

[ApiController]
[Route("api/birds")]
public class BirdsController(BirdService service) : ControllerBase
{
    [HttpPost("analyze")]
    public async Task<IActionResult> Analyze(IFormFile file)
        => Ok(await service.AnalyzeAndSaveAsync(file));

    [HttpGet("history")]
    public async Task<IActionResult> History([FromQuery] string? search)
        => Ok(await service.GetHistoryAsync(search));

    [HttpGet("stats")]
    public async Task<IActionResult> Stats()
        => Ok(await service.GetStatsAsync());
}