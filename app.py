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
            delete_after(chat_id, msg_id, 10)
        else:
            edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")


# ----- LUCKY MINES -----
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

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(3)
        edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")

    size = 5
    lucky_cells = random.choice([2, 3])
    star_positions = random.sample(range(size * size), lucky_cells)
    grid = ["🟦"] * (size * size)

    for pos in star_positions:
        time.sleep(0.5)
        grid[pos] = "⭐"
        field_text = "\n".join([" ".join(grid[i*size:(i+1)*size]) for i in range(size)])
        edit_message(chat_id, msg_id, f"💣 Generando Lucky Mines...\n\n{field_text}")

    success = round(random.uniform(90, 99), 1)
    final_text = (
        f"💣 <b>Señal Lucky Mines lista</b>\n"
        f"🎯 Éxito: {success}%\n"
        f"⭐ Celdas afortunadas: {lucky_cells}\n\n"
        f"{field_text}\n\n"
        f"⚠️ No persigas multiplicadores altos\n🔥 Retira y espera la próxima ronda"
    )
    edit_message(chat_id, msg_id, final_text)
    delete_after(chat_id, msg_id, 25)


# ----- CHICKEN ROAD V2 -----
def send_dynamic_chicken_v2(chat_id):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("⚙️ Conectando al sistema Chicken Road...", 20),
        ("🐔 Escaneando el campo de juego...", 40),
        ("🧩 Analizando las celdas seguras...", 60),
        ("📊 Evaluando multiplicadores...", 75),
        ("🧠 Calculando el punto óptimo de salida...", 90),
        ("✅ Señal lista", 100)
    ]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(2.5)
        edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")

    safe_steps = random.randint(1, 5)
    stop_x_table = {1: 1.12, 2: 1.28, 3: 1.47, 4: 1.70, 5: 1.98}
    stop_x = stop_x_table[safe_steps]
    success = round(random.uniform(87, 95), 1)

    final_text = (
        f"🐔 <b>SEÑAL CHICKEN ROAD</b>\n\n"
        f"🎮 Modo: <b>Medio</b>\n"
        f"🟩 Pasos seguros: <b>{safe_steps}</b>\n"
        f"📍 Coeficiente: <b>X{stop_x}</b>\n"
        f"🎯 Precisión estimada: <b>{success}%</b>\n\n"
        f"⚠️ No persigas multiplicadores altos\n🔥 Retira y espera la próxima ronda"
    )
    edit_message(chat_id, msg_id, final_text)
    delete_after(chat_id, msg_id, 20)


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

    first_text, pct = steps[0]
    msg_id = send_message(chat_id, f"{first_text}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(3)
        edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")

    rows, cols = 3, 5
    balls = random.randint(1, 2)
    total_cells = rows * cols
    ball_positions = random.sample(range(total_cells), balls)
    grid = ["🟦"] * total_cells

    for pos in ball_positions:
        time.sleep(0.6)
        grid[pos] = "⚽"
        field_text = "\n".join([" ".join(grid[i*cols:(i+1)*cols]) for i in range(rows)])
        edit_message(chat_id, msg_id, f"⚽ Generando señal Penalty...\n\n{field_text}")

    success = round(random.uniform(90, 99), 1)
    final_text = (
        f"⚽ <b>SEÑAL PENALTY LISTA</b>\n"
        f"🎯 Precisión: {success}%\n"
        f"⚽ Balones favorables: {balls}\n\n"
        f"{field_text}\n\n"
        f"⚠️ No persigas multiplicadores altos\n🔥 Retira y espera la próxima ronda"
    )
    edit_message(chat_id, msg_id, final_text)
    delete_after(chat_id, msg_id, 25)


# ================================
# 🌐 WEBHOOK-и
# ================================
@app.route("/webhook_mines_v2", methods=["POST"])
def webhook_luckymines():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(target=send_dynamic_luckymines, args=(int(chat_id),), daemon=True).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_chicken_v2", methods=["POST"])
def webhook_chicken_v2():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(target=send_dynamic_chicken_v2, args=(int(chat_id),), daemon=True).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_penalty_v2", methods=["POST"])
def webhook_penalty_v2():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(target=send_dynamic_penalty_v2, args=(int(chat_id),), daemon=True).start()
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
