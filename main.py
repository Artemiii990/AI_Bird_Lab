import csv
import os
from transformers import pipeline

# Доступні моделі для порівняння
MODEL_1 = "distilbert-base-uncased-finetuned-sst-2-english"
MODEL_2 = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Завантаження за замовчуванням (перша модель)
classifier = pipeline("sentiment-analysis", model=MODEL_1)

# Список з 30 відгуків для автоматичного аналізу
TEST_REVIEWS = [
    "The application works perfectly. I use it every day.",
    "The delivery was late, and the package was damaged.",
    "The product is acceptable, but nothing special.",
    "Excellent customer support and fast service!",
    "The software crashes every time I open it.",
    "Pretty good quality for this price.",
    "Terrible experience, I want my money back.",
    "It is okay, does the job.",
    "Best purchase I have made this year!",
    "The UI is confusing and hard to navigate.",
    "Works fine.",
    "Bad.",
    "Oh brilliant, it broke after two minutes of use.",
    "I love waiting three hours for a response from support.",
    "Great design, but the battery life is awful.",
    "The fast shipping was great, but the product arrived broken.",
    "Cheap material, breaks easily.",
    "Super fast delivery and nice packaging.",
    "The app eats too much battery.",
    "Not worth the price at all.",
    "It works, but sometimes it lags.",
    "Absolutely amazing feature set!",
    "Customer service ignored my email.",
    "Decent product for everyday tasks.",
    "Never buying from this brand again.",
    "Easy to set up and works out of the box.",
    "The camera is good, but the speakers are quiet.",
    "Waste of money.",
    "Simple, clean, and useful.",
    "I have mixed feelings about this purchase.",
]


def analyze_text(text, pipe):
    if not text.strip():
        return None
    try:
        res = pipe(text)[0]
        label = res["label"].upper()
        score = round(res["score"], 4)
        return {"text": text, "label": label, "score": score}
    except Exception as e:
        print(f"Помилка при аналізі: {e}")
        return None


def save_to_csv(results, filename="results.csv"):
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Text", "Label", "Score"])
            for r in results:
                writer.writerow([r["text"], r["label"], r["score"]])
        print(f"\nРезультати збережено у файл {filename}")
    except Exception as e:
        print(f"Помилка запису у файл: {e}")


def process_batch(pipe):
    print("\n--- Запуск аналізу списку відгуків ---")
    results = []
    stats = {}

    for text in TEST_REVIEWS:
        res = analyze_text(text, pipe)
        if res:
            results.append(res)
            label = res["label"]
            stats[label] = stats.get(label, 0) + 1

            print(
                f"Текст: {res['text']}\nМітка: {res['label']} | Впевненість: {res['score']}\n"
            )

    print("\n--- СТАТИСТИКА ---")
    print(f"Загальна кількість: {len(results)}")
    for label, count in stats.items():
        print(f"{label}: {count}")

    save_to_csv(results)


def compare_models():
    print("\n--- Порівняння двох моделей Hugging Face ---")
    print(f"Завантаження Моделі 1: {MODEL_1}")
    pipe1 = pipeline("sentiment-analysis", model=MODEL_1)

    print(f"Завантаження Моделі 2: {MODEL_2}")
    pipe2 = pipeline("sentiment-analysis", model=MODEL_2)

    print("\n" + "-" * 50)
    for text in TEST_REVIEWS[:10]:
        r1 = analyze_text(text, pipe1)
        r2 = analyze_text(text, pipe2)

        print(f"Текст: {text}")
        print(f"  Model 1: {r1['label']} ({r1['score']})")
        print(f"  Model 2: {r2['label']} ({r2['score']})")
        print("-" * 50)


def main():
    global classifier

    while True:
        print("\nREVIEW ANALYZER")
        print("1. Проаналізувати один відгук")
        print("2. Проаналізувати готовий список (30 відгуків)")
        print("3. Порівняти дві моделі")
        print("0. Вихід")

        choice = input("Ваш вибір: ").strip()

        if choice == "1":
            text = input("\nВведіть текст відгуку: ").strip()
            if not text:
                print("Помилка: введено порожній текст!")
                continue

            res = analyze_text(text, classifier)
            if res:
                print("\nРезультат:")
                print(f"Текст: {res['text']}")
                print(f"Тональність: {res['label']}")
                print(f"Впевненість: {res['score']}")

        elif choice == "2":
            process_batch(classifier)

        elif choice == "3":
            compare_models()

        elif choice == "0":
            print("Вихід з програми.")
            break

        else:
            print("Некоректний вибір. Спробуйте ще раз.")


if __name__ == "__main__":
    main()