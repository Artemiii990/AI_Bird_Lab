import csv
import os
import matplotlib.pyplot as plt

# Імпорт Hugging Face pipeline
try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

# Модель Hugging Face для аналізу молекул за SMILES
MODEL_NAME = "seyonec/PubChem10M_SMILES_BPE_450k-logP"

# Тестові сполуки (не менше 10)
MOLECULES = [
    {"name": "Етанол", "formula": "C2H6O", "smiles": "CCO", "exp_logp": -0.31},
    {"name": "Оцтова кислота", "formula": "C2H4O2", "smiles": "CC(=O)O", "exp_logp": -0.17},
    {"name": "Бензен", "formula": "C6H6", "smiles": "C1=CC=CC=C1", "exp_logp": 2.13},
    {"name": "Метанол", "formula": "CH4O", "smiles": "CO", "exp_logp": -0.77},
    {"name": "Ацетон", "formula": "C3H6O", "smiles": "CC(=O)C", "exp_logp": -0.24},
    {"name": "Толуол", "formula": "C7H8", "smiles": "CC1=CC=CC=C1", "exp_logp": 2.73},
    {"name": "Фенол", "formula": "C6H6O", "smiles": "OC1=CC=CC=C1", "exp_logp": 1.46},
    {"name": "Аспірин", "formula": "C9H8O4", "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O", "exp_logp": 1.19},
    {"name": "Кофеїн", "formula": "C8H10N4O2", "smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C", "exp_logp": -0.07},
    {"name": "Вода", "formula": "H2O", "smiles": "O", "exp_logp": -1.38}
]


def load_model():
    if not HAS_TRANSFORMERS:
        print("Помилка: бібліотека transformers не встановлена.")
        return None
    try:
        print("Завантаження моделі Hugging Face...")
        predictor = pipeline("text-classification", model=MODEL_NAME)
        return predictor
    except Exception as e:
        print(f"Помилка завантаження моделі: {e}")
        return None


def predict_logp(predictor, smiles):
    if not predictor:
        # Резервний аналіз для тестування без мережі
        return round(len(smiles) * 0.15 - 0.5, 2)
    try:
        result = predictor(smiles)
        # Отримання числового значення
        score = round(result[0]["score"], 2)
        return score
    except Exception as e:
        print(f"Помилка аналізу SMILES ({smiles}): {e}")
        return None


def save_to_csv(data, filename="chemistry_results.csv"):
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["molecule_name", "formula", "smiles", "predicted_property", "predicted_value", "exp_value"])
            for row in data:
                writer.writerow([
                    row["name"],
                    row["formula"],
                    row["smiles"],
                    "LogP (Solubility/Lipophilicity)",
                    row["predicted_logp"],
                    row["exp_logp"]
                ])
        print(f"Результати збережено у файл {filename}")
    except Exception as e:
        print(f"Помилка збереження CSV: {e}")


def plot_results(data):
    try:
        names = [item["name"] for item in data]
        pred_vals = [item["predicted_logp"] for item in data]
        exp_vals = [item["exp_logp"] for item in data]

        plt.figure(figsize=(10, 5))
        plt.plot(names, pred_vals, label="AI Predict (LogP)", marker="o")
        plt.plot(names, exp_vals, label="Experiment (LogP)", marker="s", linestyle="--")
        plt.xticks(rotation=45)
        plt.xlabel("Речовина")
        plt.ylabel("Значення LogP")
        plt.title("Порівняння прогнозу AI з експериментальними даними")
        plt.legend()
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Помилка побудови графіка: {e}")


def process_all(predictor):
    print("\n--- Аналіз 10 хімічних сполук ---")
    results = []

    for item in MOLECULES:
        val = predict_logp(predictor, item["smiles"])
        item_copy = item.copy()
        item_copy["predicted_logp"] = val
        results.append(item_copy)
        print(f"{item['name']} ({item['formula']}) | SMILES: {item['smiles']} | LogP AI: {val}")

    save_to_csv(results)
    return results


def search_molecule(results):
    name = input("\nВведіть назву речовини для пошуку: ").strip().lower()
    found = [m for m in results if name in m["name"].lower()]

    if found:
        for m in found:
            print(f"Знайдено: {m['name']} ({m['formula']})")
            print(f"SMILES: {m['smiles']}")
            print(f"Прогноз LogP: {m['predicted_logp']} | Експер. значення: {m['exp_logp']}")
    else:
        print("Речовину не знайдено.")


def compare_molecules(results):
    print("\n--- Порівняння сполук ---")
    name1 = input("Введіть першу речовину: ").strip().lower()
    name2 = input("Введіть другу речовину: ").strip().lower()

    m1 = next((m for m in results if name1 in m["name"].lower()), None)
    m2 = next((m for m in results if name2 in m["name"].lower()), None)

    if m1 and m2:
        print(f"\n1. {m1['name']}: LogP AI = {m1['predicted_logp']}, Експер. = {m1['exp_logp']}")
        print(f"2. {m2['name']}: LogP AI = {m2['predicted_logp']}, Експер. = {m2['exp_logp']}")
        diff = round(abs(m1['predicted_logp'] - m2['predicted_logp']), 2)
        print(f"Різниця між прогнозами: {diff}")
    else:
        print("Одну або обидві речовини не знайдено.")


def main():
    predictor = load_model()
    results = process_all(predictor)

    while True:
        print("\n=== AI Chemistry Lab ===")
        print("1. Показати відсортовані речовини за LogP")
        print("2. Побудувати графік порівняння")
        print("3. Пошук речовини за назвою")
        print("4. Порівняти дві сполуки")
        print("0. Вихід")

        choice = input("Ваш вибір: ").strip()

        if choice == "1":
            sorted_res = sorted(results, key=lambda x: x["predicted_logp"])
            print("\n--- Відсортовано за зростанням LogP ---")
            for r in sorted_res:
                print(f"{r['name']}: {r['predicted_logp']}")

        elif choice == "2":
            plot_results(results)

        elif choice == "3":
            search_molecule(results)

        elif choice == "4":
            compare_molecules(results)

        elif choice == "0":
            print("Вихід з програми.")
            break
        else:
            print("Некоректний вибір.")


if __name__ == "__main__":
    main()