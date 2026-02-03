from flask import Flask, request, jsonify
import os
import requests
import time
import threading
import random

app = Flask(__name__)

# ================================
# 🔰 Token de Telegram
# ================================
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Храним последние сообщения по каждому чату
last_messages = {}    # { chat_id: message_id }

# ================================
# 🔰 Универсальный поиск chat_id
# ================================
def extract_chat_id(payload):
    if isinstance(payload, list):
        for item in payload:
            cid = extract_chat_id(item)
            if cid:
                return cid
        return None

    if isinstance(payload, dict):
        for key in ["chat_id", "telegram_id"]:
            if key in payload and str(payload[key]).isdigit():
                return payload[key]

        for key, value in payload.items():
            cid = extract_chat_id(value)
            if cid:
                return cid

    return None

# ================================
# 🔰 Telegram Helpers
# ================================
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    r = requests.post(url, json=payload)
    return r.json().get("result", {}).get("message_id")


def edit_message(chat_id, message_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML"}
    requests.post(url, json=payload)


def delete_message(chat_id, message_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage"
    payload = {"chat_id": chat_id, "message_id": message_id}
    requests.post(url, json=payload)


def make_progress_bar(percent, length=20):
    filled = int(length * percent / 100)
    empty = length - filled
    return f"[{'█' * filled}{'▒' * empty}] {percent}%"

# ================================
# 🗑 Функция авто-удаления финального сообщения
# ================================
def delete_after(chat_id, message_id, delay):
    def worker():
        time.sleep(delay)
        delete_message(chat_id, message_id)
    threading.Thread(target=worker, daemon=True).start()

# ================================
# 🔥 ДИНАМИЧЕСКИЕ СООБЩЕНИЯ ДЛЯ ИГР
# ================================
 
# ----- MINES -----
def send_dynamic_mines(chat_id):

    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("⚙️ Conectando al sistema...", 10),
        ("🔍 Analizando la ubicación de las minas...", 30),
        ("🧠 Calculando probabilidad...", 60),
        ("🛠️ Optimizando la señal...", 85),
        ("💣 Señal lista", 100)
    ]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(3)
        if pct == 100:
            success = round(random.uniform(85, 95), 1)
            edit_message(chat_id, msg_id, f"💣 Señal lista — éxito: {success}%")

            # 🔥 удалить итоговое сообщение через 10 сек
            delete_after(chat_id, msg_id, 10)

        else:
            edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")


# ----- LUCKY MINES (обновлённая версия с синим полем и прогресс-баром) -----
def send_dynamic_luckymines(chat_id):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("⚙️ Conectando al sistema...", 10),
        ("🔍 Analizando la ubicación de las minas...", 30),
        ("🧠 Calculando probabilidad...", 60),
        ("🛠️ Optimizando la señal...", 85),
        ("💣 Señal lista", 100)
    ]

    # Отправляем первое сообщение с прогресс-баром
    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    # Обновление прогресса
    for text, pct in steps[1:]:
        time.sleep(3)
        edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")

    # Настройки поля
    size = 5
    lucky_cells = random.choice([2, 3])  # случайно 2 или 3 звезды
    star_positions = random.sample(range(size * size), lucky_cells)
    grid = ["🟦"] * (size * size)

    # Анимация появления звезд перед финальным сообщением
    for pos in star_positions:
        time.sleep(0.5)
        grid[pos] = "⭐"
        field_text = "\n".join(
            [" ".join(grid[i*size:(i+1)*size]) for i in range(size)]
        )
        edit_message(chat_id, msg_id, f"💣 Generando Lucky Mines...\n\n{field_text}")

    # Финальное сообщение с шансом успеха
    success = round(random.uniform(90, 99), 1)
    final_text = (
        f"💣 <b>Señal Lucky Mines lista</b>\n"
        f"🎯 Éxito: {success}%\n"
        f"⭐ Celdas afortunadas: {lucky_cells}\n\n"
        f"{field_text}\n\n"
        f"⚠️ No persigas multiplicadores altos
          🔥 Retira y espera la próxima ronda"
    )
    edit_message(chat_id, msg_id, final_text)

    # Удаление через 25 секунд
    delete_after(chat_id, msg_id, 25)


# ----- CHICKEN ROAD -----
def send_dynamic_chicken(chat_id):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("⚙️ Conectando al sistema...", 20),
        ("🐔 Escaneando el campo...", 40),
        ("🧩 Analizando las celdas seguras...", 60),
        ("🧠 Verificando probabilidades...", 80),
        ("🔥 Preparando la señal…", 90),
        ("✅ Señal lista", 100)
    ]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(2)
        if pct == 100:
            edit_message(chat_id, msg_id, "🐔 Señal lista — evita las zonas calientes 🔥")
            delete_after(chat_id, msg_id, 10)
        else:
            edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")

# ----- CHICKEN ROAD V2 (señal dinámica por pasos) -----
def send_dynamic_chicken_v2(chat_id):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    # Этапы прогресса
    steps = [
        ("⚙️ Conectando al sistema Chicken Road...", 20),
        ("🐔 Escaneando el campo de juego...", 40),
        ("🧩 Analizando las celdas seguras...", 60),
        ("📊 Evaluando multiplicadores...", 75),
        ("🧠 Calculando el punto óptimo de salida...", 90),
        ("✅ Señal lista", 100)
    ]

    # Отправляем первое сообщение с прогресс-баром
    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    # Обновляем прогресс шаг за шагом
    for text, pct in steps[1:]:
        time.sleep(2.5)
        edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")

    # 🎯 ЛОГИКА Chicken Road
    safe_steps = random.randint(1, 5)  # количество безопасных шагов от 1 до 5

    # соответствие шагов и коэффициентов
    stop_x_table = {
        1: 1.12,
        2: 1.28,
        3: 1.47,
        4: 1.70,
        5: 1.98
    }

    stop_x = stop_x_table[safe_steps]  # выбираем коэффициент по шагу
    success = round(random.uniform(87, 95), 1)  # точность сигнала

    # Финальное сообщение
    final_text = (
        f"🐔 <b>SEÑAL CHICKEN ROAD</b>\n\n"
        f"🎮 Modo: <b>Medio</b>\n"
        f"🟩 Pasos seguros: <b>{safe_steps}</b>\n"
        f"📍 Coeficiente: <b>X{stop_x}</b>\n"
        f"🎯 Precisión estimada: <b>{success}%</b>\n\n"
        f"⚠️ No persigas multiplicadores altos\n🔥 Retira y espera la próxima ronda"
    )

    edit_message(chat_id, msg_id, final_text)

    # Автоудаление через 20 секунд
    delete_after(chat_id, msg_id, 20)

# ----- PENALTY -----
def send_dynamic_penalty(chat_id):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("⚙️ Conectando al sistema...", 15),
        ("⚽ Analizando al portero...", 35),
        ("🎯 Calculando la trayectoria óptima...", 60),
        ("🔥 Preparando el tiro perfecto...", 85),
        ("🏆 Señal lista", 100)
    ]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(2.5)
        if pct == 100:
            edit_message(chat_id, msg_id, "⚽ Señal lista — ¡dispara y marca gol! 🏆")
            delete_after(chat_id, msg_id, 10)
        else:
            edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")
            
# ----- PENALTY V2 -----
def send_dynamic_penalty_v2(chat_id):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("⚙️ Conectando al sistema Penalty...", 10),
        ("🧤 Analizando al portero...", 30),
        ("🎯 Calculando trayectoria del disparo...", 60),
        ("🛠️ Optimizando señal...", 85),
        ("⚽ Señal lista", 100)
    ]

    # первое сообщение
    first_text, pct = steps[0]
    msg_id = send_message(chat_id, f"{first_text}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    # прогресс
    for text, pct in steps[1:]:
        time.sleep(3)
        edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")
# поле 3x5
rows = 3
cols = 5
balls = random.randint(1, 2)  # рандомно 1 или 2 мяча

total_cells = rows * cols
ball_positions = random.sample(range(total_cells), balls)
grid = ["🟦"] * total_cells

# анимация появления мячей
for pos in ball_positions:
    time.sleep(0.6)
    grid[pos] = "⚽"
    field_text = "\n".join(
        [" ".join(grid[i*cols:(i+1)*cols]) for i in range(rows)]
    )
    edit_message(
        chat_id,
        msg_id,
        f"⚽ Generando señal Penalty...\n\n{field_text}"
    )

    success = round(random.uniform(90, 99), 1)

    final_text = (
        f"⚽ <b>SEÑAL PENALTY LISTA</b>\n"
        f"🎯 Precisión: {success}%\n"
        f"⚽ Balones favorables: {balls}\n\n"
        f"{field_text}\n\n"
        f"⚠️ No persigas multiplicadores altos
          🔥 Retira y espera la próxima ronda"
    )

    edit_message(chat_id, msg_id, final_text)
    delete_after(chat_id, msg_id, 25)


# ----- AVIATOR -----
def send_dynamic_aviator(chat_id):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("⚙️ Conectando al sistema...", 15),
        ("✈️ Escaneando los últimos coeficientes…", 35),
        ("📊 Analizando el comportamiento del avión…", 60),
        ("🧠 Predicción del coeficiente X óptimo…", 85),
        ("🔥 Señal lista", 100)
    ]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(3)
        if pct == 100:
            x = round(random.uniform(1.2, 3.3), 2)
            edit_message(chat_id, msg_id, f"✈️ Señal lista — retírate en X{x} 🚀")
            delete_after(chat_id, msg_id, 10)
        else:
            edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")
            
# ----- AVIATOR V2 (señal dinámica con salida X) -----
def send_dynamic_aviator_v2(chat_id):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("⚙️ Conectando al sistema Aviator...", 15),
        ("✈️ Escaneando vuelos recientes...", 35),
        ("📊 Analizando patrones de coeficientes...", 55),
        ("🧠 Calculando punto óptimo de salida...", 75),
        ("🔥 Optimizando señal...", 90),
        ("✅ Señal lista", 100)
    ]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    # progreso
    for text, pct in steps[1:]:
        time.sleep(2.5)
        edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")

    # 🎯 LÓGICA AVIATOR
    stop_x = round(random.uniform(1.30, 2.40), 2)
    success = round(random.uniform(88, 96), 1)

    final_text = (
        f"✈️ <b>SEÑAL AVIATOR</b>\n\n"
        f"📍 Retiro recomendado: <b>X{stop_x}</b>\n"
        f"🎯 Precisión estimada: <b>{success}%</b>\n\n"
        f"⚠️ No persigas multiplicadores altos\n"
        f"🔥 Retira y espera la próxima ronda"
    )

    edit_message(chat_id, msg_id, final_text)

    # auto eliminación
    delete_after(chat_id, msg_id, 20)


# ----- RABBIT ROAD -----
def send_dynamic_rabbit(chat_id):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("⚙️ Conectando al sistema...", 15),
        ("🥕 Escaneando los cultivos de zanahorias...", 35),
        ("✋ Analizando la aparición de manos atrapadoras...", 60),
        ("🧠 Calculando pasos seguros...", 85),
        ("✅ Señal lista", 100)
    ]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(2.5)
        if pct == 100:
            edit_message(chat_id, msg_id, "🐰 Señal lista — evita las manos atrapadoras, recoge la zanahoria y detente 🥕🔥")
            delete_after(chat_id, msg_id, 10)
        else:
            edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")
            
# ----- RABBIT ROAD V2 (динамический шаговый сигнал) -----
def send_dynamic_rabbit_v2(chat_id):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("⚙️ Conectando al sistema Rabbit Road...", 15),
        ("🥕 Escaneando las rutas del conejo...", 35),
        ("✋ Detectando manos atrapadoras...", 55),
        ("📊 Analizando multiplicadores seguros...", 75),
        ("🧠 Calculando punto óptimo de salida...", 90),
        ("✅ Señal lista", 100)
    ]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(2.5)
        edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")

    # 🎯 ЛОГИКА Rabbit Road
    safe_steps = random.randint(3, 6)        # сколько дорожек пройти
    stop_x = round(random.uniform(1.15, 1.35), 2)
    success = round(random.uniform(88, 96), 1)

    final_text = (
        f"🐰 <b>SEÑAL RABBIT ROAD</b>\n\n"
        f"🥕 Pasos seguros: <b>{safe_steps}</b>\n"
        f"📍 Salida recomendada: <b>X{stop_x}</b>\n"
        f"🎯 Precisión estimada: <b>{success}%</b>\n\n"
        f"⚠️ No fuerces después de la salida\n"
        f"🔥 Mejor retirar y reiniciar"
    )

    edit_message(chat_id, msg_id, final_text)

    # автоудаление через 20 сек
    delete_after(chat_id, msg_id, 20)


# ----- BALLOONIX -----
def send_dynamic_balloonix(chat_id):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("⚙️ Conectando al sistema BallooniX...", 15),
        ("🎈 Analizando el inflado del globo...", 35),
        ("📡 Escaneando patrones de explosión...", 60),
        ("🧠 Calculando punto óptimo de salida...", 85),
        ("🔥 Señal lista", 100)
    ]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(3)
        if pct == 100:
            x = round(random.uniform(1.3, 3.8), 2)
            edit_message(chat_id, msg_id, f"🎈 Señal BallooniX lista — retírate en X{x} 🚀")
            delete_after(chat_id, msg_id, 10)
        else:
            edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")
            
# ----- BALLOONIX V2 (señal dinámica con salida X) -----
def send_dynamic_balloonix_v2(chat_id):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("⚙️ Conectando al sistema BallooniX...", 15),
        ("🎈 Analizando el inflado del globo...", 35),
        ("📡 Escaneando patrones de explosión...", 55),
        ("🧠 Calculando punto óptimo de salida...", 75),
        ("🔥 Optimizando señal...", 90),
        ("✅ Señal lista", 100)
    ]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    # progreso
    for text, pct in steps[1:]:
        time.sleep(2.5)
        edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")

    # 🎯 LÓGICA BallooniX
    stop_x = round(random.uniform(1.35, 3.20), 2)
    success = round(random.uniform(88, 97), 1)

    final_text = (
        f"🎈 <b>SEÑAL BALLOONIX</b>\n\n"
        f"📍 Retiro recomendado: <b>X{stop_x}</b>\n"
        f"🎯 Precisión estimada: <b>{success}%</b>\n\n"
        f"⚠️ No esperes demasiado para retirar\n"
        f"🔥 Retira antes de la explosión y comienza de nuevo"
    )

    edit_message(chat_id, msg_id, final_text)

    # auto eliminación
    delete_after(chat_id, msg_id, 20)


# ================================
# 🌐 WEBHOOK-и для каждой игры
# ================================
@app.route("/webhook_mines", methods=["POST"])
def webhook_mines():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(target=send_dynamic_mines, args=(int(chat_id),), daemon=True).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_mines_v2", methods=["POST"])
def webhook_luckymines():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(target=send_dynamic_luckymines, args=(int(chat_id),), daemon=True).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_chicken", methods=["POST"])
def webhook_chicken():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(target=send_dynamic_chicken, args=(int(chat_id),), daemon=True).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_penalty", methods=["POST"])
def webhook_penalty():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(target=send_dynamic_penalty, args=(int(chat_id),), daemon=True).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_penalty_v2", methods=["POST"])
def webhook_penalty_v2():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_penalty_v2,
            args=(int(chat_id),),
            daemon=True
        ).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_aviator", methods=["POST"])
def webhook_aviator():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(target=send_dynamic_aviator, args=(int(chat_id),), daemon=True).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_aviator_v2", methods=["POST"])
def webhook_aviator_v2():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_aviator_v2,
            args=(int(chat_id),),
            daemon=True
        ).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_rabbit", methods=["POST"])
def webhook_rabbit():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(target=send_dynamic_rabbit, args=(int(chat_id),), daemon=True).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_balloonix", methods=["POST"])
def webhook_balloonix():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(target=send_dynamic_balloonix, args=(int(chat_id),), daemon=True).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_rabbit_v2", methods=["POST"])
def webhook_rabbit_v2():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_rabbit_v2,
            args=(int(chat_id),),
            daemon=True
        ).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_chicken_v2", methods=["POST"])
def webhook_chicken_v2():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_chicken_v2,
            args=(int(chat_id),),
            daemon=True
        ).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400
    
@app.route("/webhook_balloonix_v2", methods=["POST"])
def webhook_balloonix_v2():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_balloonix_v2,
            args=(int(chat_id),),
            daemon=True
        ).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400


# ================================
# 🏠 Home
# ================================
@app.route("/")
def home():
    return "HackBot is running", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
