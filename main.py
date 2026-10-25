from datetime import datetime
import heapq
import sqlite3

# Карта локацій
LOCATIONS = {
    "A": "Центр",
    "B": "Університет",
    "C": "Лікарня",
    "D": "Парк",
    "E": "Вокзал",
    "F": "Торговий центр",
    "G": "Аеропорт",
}

# Граф: v1 -> {v2: (distance, time, traffic)}
GRAPH = {
    "A": {"B": (5, 8, 1.1), "D": (6, 10, 1.0), "C": (7, 12, 1.2)},
    "B": {"A": (5, 8, 1.1), "E": (7, 11, 1.3), "C": (3, 5, 1.0)},
    "C": {"A": (7, 12, 1.2), "B": (3, 5, 1.0), "F": (8, 14, 1.1)},
    "D": {"A": (6, 10, 1.0), "F": (5, 9, 1.0)},
    "E": {"B": (7, 11, 1.3), "G": (6, 8, 1.0), "F": (4, 7, 1.2)},
    "F": {"D": (5, 9, 1.0), "C": (8, 14, 1.1), "E": (4, 7, 1.2), "G": (7, 11, 1.0)},
    "G": {"E": (6, 8, 1.0), "F": (7, 11, 1.0)},
}


# --- РОБОТА З БАЗОЮ ДАНИХ ---


def init_db():
    conn = sqlite3.connect("navigator.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            user_type TEXT
        )
    """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS routes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            start_point TEXT,
            finish_point TEXT,
            route TEXT,
            distance REAL,
            time REAL,
            actual_time REAL,
            actual_distance REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """
    )

    conn.commit()
    conn.close()


def get_or_create_user(username, user_type):
    conn = sqlite3.connect("navigator.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()

    if row:
        user_id = row[0]
    else:
        cursor.execute(
            "INSERT INTO users (username, user_type) VALUES (?, ?)",
            (username, user_type),
        )
        conn.commit()
        user_id = cursor.lastrowid

    conn.close()
    return user_id


def save_route(user_id, start, finish, route_str, dist, est_time):
    conn = sqlite3.connect("navigator.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO routes (user_id, start_point, finish_point, route, distance, time)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (user_id, start, finish, route_str, dist, est_time),
    )

    conn.commit()
    route_id = cursor.lastrowid
    conn.close()
    return route_id


def update_actual_trip(route_id, actual_time, actual_dist):
    conn = sqlite3.connect("navigator.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE routes
        SET actual_time = ?, actual_distance = ?
        WHERE id = ?
    """,
        (actual_time, actual_dist, route_id),
    )

    conn.commit()
    conn.close()


def get_history(start=None, finish=None):
    conn = sqlite3.connect("navigator.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT r.*, u.username, u.user_type 
        FROM routes r 
        JOIN users u ON r.user_id = u.id
    """
    params = []

    if start and finish:
        query += " WHERE r.start_point = ? AND r.finish_point = ?"
        params = [start, finish]

    query += " ORDER BY r.created_at DESC"

    cursor.execute(query, params)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_stats():
    conn = sqlite3.connect("navigator.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM routes")
    total = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT route, COUNT(*), AVG(actual_time), AVG(time), AVG(distance)
        FROM routes
        GROUP BY route
        ORDER BY COUNT(*) DESC
    """
    )
    rows = cursor.fetchall()
    conn.close()

    return total, rows


# --- АЛГОРИТМ ДЕЙКСТРИ ---


def dijkstra(start, target):
    distances = {node: float("inf") for node in GRAPH}
    times = {node: float("inf") for node in GRAPH}
    distances[start] = 0
    times[start] = 0

    pq = [(0, start)]
    parent = {}

    while pq:
        curr_time, u = heapq.heappop(pq)

        if curr_time > times[u]:
            continue

        if u == target:
            break

        for v, (dist, t, traffic) in GRAPH.get(u, {}).items():
            calc_time = t * traffic
            if times[u] + calc_time < times[v]:
                times[v] = times[u] + calc_time
                distances[v] = distances[u] + dist
                parent[v] = u
                heapq.heappush(pq, (times[v], v))

    if target not in parent and start != target:
        return None, 0, 0

    path = []
    curr = target
    while curr != start:
        path.append(curr)
        curr = parent[curr]
    path.append(start)
    path.reverse()

    return path, round(distances[target], 1), round(times[target], 1)


# Пошук усіх можливих шляхів для порівняння AI
def find_all_paths(start, target, visited=None, path=None):
    if visited is None:
        visited = set()
    if path is None:
        path = []

    visited.add(start)
    path.append(start)

    paths = []

    if start == target:
        total_d = 0
        total_t = 0
        for i in range(len(path) - 1):
            d, t, tr = GRAPH[path[i]][path[i + 1]]
            total_d += d
            total_t += t * tr
        paths.append((list(path), round(total_d, 1), round(total_t, 1)))
    else:
        for neighbor in GRAPH.get(start, {}):
            if neighbor not in visited:
                paths.extend(find_all_paths(neighbor, target, visited, path))

    path.pop()
    visited.remove(start)
    return paths


# --- AI МОДУЛЬ ---


def ai_recommendation(start, finish, user_id):
    all_routes = find_all_paths(start, finish)
    if not all_routes:
        return "Маршрутів не знайдено."

    history = get_history(start, finish)

    print("\n=== AI-АНАЛІЗ ТА РЕКОМЕНДАЦІЇ ===")

    best_path = None
    min_time = float("inf")

    for path, dist, est_time in all_routes:
        route_str = ",".join(path)
        matching = [
            h
            for h in history
            if h["route"] == route_str and h["actual_time"] is not None
        ]

        if matching:
            avg_actual = sum(h["actual_time"] for h in matching) / len(matching)
            eff_time = avg_actual
            print(
                f"Маршрут {'->'.join(path)}: Прогноз = {est_time} хв | Реальний серединй = {round(avg_actual, 1)} хв ({len(matching)} поїздок)"
            )
        else:
            eff_time = est_time
            print(
                f"Маршрут {'->'.join(path)}: Прогноз = {est_time} хв | Немає історії"
            )

        if eff_time < min_time:
            min_time = eff_time
            best_path = (path, dist, est_time, eff_time)

    res = "\n💡 Висновок AI:\n"
    if best_path:
        p, d, e, eff = best_path
        res += f"Рекомендовано обрати: {' -> '.join(p)}\n"
        res += f"Дистанція: {d} км, Очікуваний час з урахуванням історії: ~{round(eff, 1)} хв."

    return res


# --- MAIN ---


def main():
    init_db()

    print("=== AI NAVIGATOR ===")
    username = input("Введіть ваше ім'я: ").strip()
    user_type = (
        input("Введіть тип (student/worker/driver): ").strip().lower()
    )

    if user_type not in ["student", "worker", "driver"]:
        user_type = "driver"

    user_id = get_or_create_user(username, user_type)
    last_route_id = None

    while True:
        print("\n" + "=" * 20)
        print("1. Знайти маршрут")
        print("2. Додати фактичний час поїздки")
        print("3. Історія")
        print("4. Статистика")
        print("5. AI-рекомендація")
        print("0. Вихід")
        print("=" * 20)

        choice = input("Ваш вибір: ").strip()

        if choice == "1":
            print("\nЛокації:", ", ".join(LOCATIONS.keys()))
            start = input("Звідки: ").strip().upper()
            finish = input("Куди: ").strip().upper()

            if start not in LOCATIONS or finish not in LOCATIONS:
                print("Невірно вказані точки!")
                continue

            path, dist, time_est = dijkstra(start, finish)

            if not path:
                print("Маршрут відсутній.")
                continue

            route_str = ",".join(path)
            print(f"\nЗнайдено оптимальний маршрут (Dijkstra):")
            print(f"Шлях: {' -> '.join(path)}")
            print(f"Відстань: {dist} км")
            print(f"Прогнозований час: {time_est} хв")

            last_route_id = save_route(
                user_id, start, finish, route_str, dist, time_est
            )
            print(f"(Маршрут збережено під ID: {last_route_id})")

        elif choice == "2":
            r_id = input(f"Введіть ID поїздки [{last_route_id}]: ").strip()
            if not r_id:
                r_id = last_route_id

            if not r_id:
                print("ID не вказано.")
                continue

            try:
                act_t = float(input("Фактичний час (хв): "))
                act_d = float(input("Фактична відстань (км): "))
                update_actual_trip(int(r_id), act_t, act_d)
                print("Дані успішно оновлені!")
            except ValueError:
                print("Помилка введення даних.")

        elif choice == "3":
            history = get_history()
            print("\n--- Історія поїздок ---")
            for h in history:
                act = (
                    f"Фактично: {h['actual_time']} хв"
                    if h["actual_time"]
                    else "Немає факт. даних"
                )
                print(
                    f"ID {h['id']} | {h['username']} ({h['user_type']}) | {h['route']} | Прогноз: {h['time']} хв | {act}"
                )

        elif choice == "4":
            total, stats = get_stats()
            print(f"\nВсього поїздок у системі: {total}")
            for s in stats:
                avg_act = round(s[2], 1) if s[2] else "N/A"
                print(
                    f"Маршрут {s[0]} | Поїздок: {s[1]} | Середній факт. час: {avg_act} хв (прогноз: {round(s[3], 1)} хв)"
                )

        elif choice == "5":
            start = input("Звідки: ").strip().upper()
            finish = input("Куди: ").strip().upper()

            if start not in LOCATIONS or finish not in LOCATIONS:
                print("Невірно вказані точки!")
                continue

            rec = ai_recommendation(start, finish, user_id)
            print(rec)

        elif choice == "0":
            print("Вихід з програми.")
            break


if __name__ == "__main__":
    main()