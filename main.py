import os
from PIL import Image
from scipy.io.wavfile import write
from transformers import pipeline

# Завантаження моделей Hugging Face
print("Завантаження моделей, зачекайте...")

# Модель 1: Зображення в текст (Image Captioning)
vision_pipe = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")

# Модель 2: Текст у мовлення (Text-to-Speech)
tts_pipe = pipeline("text-to-speech", model="facebook/mms-tts-eng")


def ensure_folders():
    if not os.path.exists("input"):
        os.makedirs("input")
    if not os.path.exists("output"):
        os.makedirs("output")


def analyze_image(image_path):
    if not os.path.exists(image_path):
        print("Помилка: Файл не знайдено!")
        return None

    ext = os.path.splitext(image_path)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png"]:
        print("Помилка: Непідтримуваний формат файлу. Використовуйте JPG або PNG.")
        return None

    try:
        img = Image.open(image_path)
        print("Аналіз зображення...")
        result = vision_pipe(img)
        if result and len(result) > 0:
            description = result[0]["generated_text"]
            return description
        else:
            print("Не вдалося згенерувати опис.")
            return None
    except Exception as e:
        print(f"Помилка відкриття зображення: {e}")
        return None


def generate_audio(text, output_filename="description.wav"):
    try:
        print("Генерація голосу...")
        speech_result = tts_pipe(text)

        output_path = os.path.join("output", output_filename)
        sampling_rate = speech_result["sampling_rate"]
        audio_data = speech_result["audio"][0]

        write(output_path, sampling_rate, audio_data)
        return output_path
    except Exception as e:
        print(f"Помилка при генерації аудіо: {e}")
        return None


def save_description_to_file(image_name, description):
    try:
        with open("descriptions.txt", "a", encoding="utf-8") as f:
            f.write(f"Файл: {image_name}\nОпис: {description}\n--------------------\n")
    except Exception as e:
        print(f"Помилка збереження опису: {e}")


def process_single_image():
    image_path = input("Введіть шлях до фотографії: ").strip()
    
    description = analyze_image(image_path)
    if not description:
        return

    print("\nОпис зображення:")
    print(description)

    out_name = input("Введіть назву вихідного файлу (за замовчуванням description.wav): ").strip()
    if not out_name:
        out_name = "description.wav"
    if not out_name.endswith(".wav"):
        out_name += ".wav"

    audio_path = generate_audio(description, out_name)
    if audio_path:
        image_name = os.path.basename(image_path)
        save_description_to_file(image_name, description)

        print("\n--- ЗВІТ ---")
        print(f"Назва фотографії: {image_name}")
        print(f"Розпізнаний опис: {description}")
        print("Модель Vision: Salesforce/blip-image-captioning-base")
        print("Модель TTS: facebook/mms-tts-eng")
        print(f"Аудіо збережено у: {audio_path}")


def process_multiple_images():
    folder_path = input("Введіть шлях до папки з фотографіями (наприклад, input): ").strip()
    if not os.path.exists(folder_path):
        print("Папку не знайдено.")
        return

    files = [f for f in os.listdir(folder_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    if not files:
        print("У папці немає фотографій.")
        return

    for idx, filename in enumerate(files):
        print(f"\nОбробка [{idx + 1}/{len(files)}]: {filename}")
        full_path = os.path.join(folder_path, filename)
        
        description = analyze_image(full_path)
        if description:
            print(f"Опис: {description}")
            out_audio = f"output_{os.path.splitext(filename)[0]}.wav"
            generate_audio(description, out_audio)
            save_description_to_file(filename, description)


def repeat_speech():
    text = input("Введіть текст для озвучення: ").strip()
    if not text:
        print("Текст порожній.")
        return
    
    out_name = input("Назва файлу аудіо (за замовчуванням custom.wav): ").strip()
    if not out_name:
        out_name = "custom.wav"
    if not out_name.endswith(".wav"):
        out_name += ".wav"

    generate_audio(text, out_name)


def main():
    ensure_folders()
    
    while True:
        print("\n=== AI Vision & Voice Assistant ===")
        print("1. Проаналізувати одну фотографію")
        print("2. Проаналізувати декілька фотографій з папки")
        print("3. Озвучити текст повторно")
        print("0. Вихід")

        choice = input("Ваш вибір: ").strip()

        if choice == "1":
            process_single_email = process_single_image()
        elif choice == "2":
            process_multiple_images()
        elif choice == "3":
            repeat_speech()
        elif choice == "0":
            print("Вихід з програми.")
            break
        else:
            print("Некоректний вибір. Спробуйте ще раз.")


if __name__ == "__main__":
    main()