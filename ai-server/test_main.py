import io
from PIL import Image
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def create_dummy_image():
    # Генерируем тестовую картинку 224x224 в памяти
    img = Image.new("RGB", (224, 224), color="green")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf

def test_predict_endpoint_returns_valid_bird_data():
    img_bytes = create_dummy_image()
    response = client.post(
        "/predict",
        files={"file": ("test_bird.jpg", img_bytes, "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()
    assert "species" in data
    assert isinstance(data["confidence"], float)
    assert 0 <= data["confidence"] <= 100
    assert "Варіанти розпізнавання:" in data["description"]

def test_predict_without_file_fails():
    response = client.post("/predict")
    assert response.status_code == 422