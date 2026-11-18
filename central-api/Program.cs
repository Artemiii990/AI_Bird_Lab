using BirdLab;
using Microsoft.AspNetCore.Diagnostics;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddSwaggerGen();

builder.Services.AddCors(options =>
{
    options.AddPolicy("FrontendPolicy", policy =>
    {
        policy.WithOrigins("http://localhost:3000", "http://127.0.0.1:3000")
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// Регистрируем БД, клиент к Python и наш BirdService
builder.Services.AddDbContext<AppDb>(o => o.UseSqlServer(builder.Configuration.GetConnectionString("Default")));
builder.Services.AddHttpClient("ai", c => c.BaseAddress = new Uri(builder.Configuration["AiUrl"] ?? "http://ai-server:8000"));
builder.Services.AddScoped<BirdService>();

var app = builder.Build();

using (var scope = app.Services.CreateScope())
    scope.ServiceProvider.GetRequiredService<AppDb>().Database.EnsureCreated();

// перехват ошибок с сохранением CORS-заголовков
app.UseExceptionHandler(errorApp =>
{
    errorApp.Run(async context =>
    {
        var exception = context.Features.Get<IExceptionHandlerFeature>()?.Error;
        var isValidationError = exception is InvalidOperationException;

        context.Response.StatusCode = isValidationError
            ? StatusCodes.Status400BadRequest
            : StatusCodes.Status500InternalServerError;

        await context.Response.WriteAsJsonAsync(new
        {
            detail = isValidationError ? exception!.Message : "Внутренняя ошибка сервера."
        });
    });
});

app.UseSwagger();
app.UseSwaggerUI();

app.UseCors("FrontendPolicy");
app.MapControllers();

app.Run();