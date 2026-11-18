import io
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from transformers import pipeline

app = FastAPI()

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
CONFIDENCE_THRESHOLD = 0.40  # Порог 40%

# Индексы всех классов птиц в ImageNet-1k (7..24 и 80..100)
BIRD_CLASS_IDS = set(range(7, 25)) | set(range(80, 101))

# Загружаем реальную нейросеть
classifier = pipeline("image-classification", model="timm/resnet50.a1_in1k")

# Строим обратный словарь label -> id из id2label (так как в timm label2id == None)
id2label = classifier.model.config.id2label or {}
LABEL_TO_ID = {label: int(idx) for idx, label in id2label.items()}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(
            status_code=400,
            detail="Допускаются только изображения JPG, PNG или WEBP."
        )

    contents = await file.read()
    try:
        img = Image.open(io.BytesIO(contents))
        img.verify()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
    except (UnidentifiedImageError, Exception):
        raise HTTPException(
            status_code=400,
            detail="Файл повреждён или не является изображением."
        )

    # Нейросеть определяет вид из 1000 классов
    predictions = classifier(img)
    top = predictions[0]
    raw_label = top["label"]
    score = float(top["score"])

    # Проверяем по ID класса, что это именно птица
    class_id = LABEL_TO_ID.get(raw_label, -1)
    is_bird = class_id in BIRD_CLASS_IDS

    if not is_bird or score < CONFIDENCE_THRESHOLD:
        raise HTTPException(
            status_code=422,
            detail="На фото не обнаружена птица. Загрузите чёткий снимок птицы, а не скриншот или другой объект."
        )

    species = raw_label.split(",")[0].strip()
    confidence = round(score * 100, 2)

    # Берем топ-3 варианта для описания
    alternatives = ", ".join(
        [f"{p['label'].split(',')[0]} ({round(p['score'] * 100, 1)}%)" for p in predictions[:3]]
    )
    description = f"Варіанти розпізнавання: {alternatives}"

    return {
        "species": species,
        "confidence": confidence,
        "description": description
    }