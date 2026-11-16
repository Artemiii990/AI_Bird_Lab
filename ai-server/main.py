import io
from fastapi import FastAPI, UploadFile, File
from PIL import Image
from transformers import pipeline

app = FastAPI()

# Загружаем реальную нейросеть (при первом старте скачает ~100 МБ)
classifier = pipeline("image-classification", model="timm/resnet50.a1_in1k")

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    img = Image.open(io.BytesIO(await file.read())).convert("RGB")
    
    # Нейросеть сама определяет вид из 1000 классов
    predictions = classifier(img)
    top = predictions[0]
    
    species = top["label"].split(",")[0].strip()
    confidence = round(top["score"] * 100, 2)
    
    # Берем топ-3 варианта для описания
    alternatives = ", ".join([f"{p['label'].split(',')[0]} ({round(p['score']*100, 1)}%)" for p in predictions[:3]])
    description = f"Варіанти розпізнавання: {alternatives}"

    return {
        "species": species,
        "confidence": confidence,
        "description": description
    }