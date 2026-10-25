from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Simple FastAPI App")


# Простой JSON эндпоинт (API)
@app.get("/api/hello")
def get_hello():
    return {"status": "success", "message": "Привет от FastAPI!"}


# Простая HTML-страница
@app.get("/", response_class=HTMLResponse)
def get_home_page():
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>FastAPI Test Page</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f6f9;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .card {
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                text-align: center;
            }
            h1 { color: #2563eb; }
            p { color: #4b5563; }
            a {
                display: inline-block;
                margin-top: 15px;
                padding: 10px 20px;
                background-color: #2563eb;
                color: white;
                text-decoration: none;
                border-radius: 8px;
            }
            a:hover { background-color: #1d4ed8; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🚀 FastAPI работает отлично!</h1>
            <p>Это тестовая HTML-страница, запущенная на FastAPI.</p>
            <a href="/docs" target="_blank">Открыть Swagger Документацию</a>
        </div>
    </body>
    </html>
    """


# Запуск сервера прямо из скрипта
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)