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

# ================================
# 🗃 Храним последние сообщения по каждому чату
# ================================
last_messages = {}  # { chat_id: message_id }

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

    def run_steps():
        for text, pct in steps[1:]:
            time.sleep(2)
            if pct == 100:
                success = round(random.uniform(90, 99), 1)
                lucky_cells = 3
                size = 5
                total_cells = size * size
                star_positions = random.sample(range(total_cells), lucky_cells)

                # создаём поле из 🟦
                field = ["🟦"] * total_cells

                base_text = f"💎 <b>Señal Lucky lista</b>\n🎯 Éxito: {success}%\n⭐ Celdas afortunadas: {lucky_cells}\n\n"

                # функция для генерации текста поля
                def field_text():
                    return "\n".join(
                        [" ".join(field[i*size:(i+1)*size]) for i in range(size)]
                    )

                # отправляем начальное сообщение с пустым полем
                edit_message(chat_id, msg_id, f"{base_text}{field_text()}\n\n⚠️ ¡Juega con suerte!")

                # анимация появления звезд
                def reveal_stars():
                    for pos in star_positions:
                        field[pos] = "⭐"
                        updated_text = f"{base_text}{field_text()}\n\n⚠️ ¡Juega с suerte!"
                        edit_message(chat_id, msg_id, updated_text)
                        time.sleep(0.5)

                threading.Thread(target=reveal_stars, daemon=True).start()

                # удалить сообщение через 25 секунд
                delete_after(chat_id, msg_id, 25)

            else:
                edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")

    threading.Thread(target=run_steps, daemon=True).start()


# ----- Остальные игры (Chicken, Penalty, Aviator, Rabbit, BallooniX) -----
# Аналогично, как выше: прогресс + edit_message + delete_after
# Пример для Chicken:
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

                # Здесь можно добавить анимацию звёзд, если нужно
                # threading.Thread(target=reveal_stars_animation, args=(chat_id, msg_id, size, star_positions, 0.5), daemon=True).start()
                
                delete_after(chat_id, msg_id, 25)
            else:
                edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")

    threading.Thread(target=run_steps, daemon=True).start()


# ----- Остальные игры (Chicken, Penalty, Aviator, Rabbit, BallooniX) -----
# Аналогично, как выше: прогресс + edit_message + delete_after
# Пример для Chicken:
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

@app.route("/webhook_luckymines", methods=["POST"])
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

# ================================
# 🏠 Home
# ================================
@app.route("/")
def home():
    return "HackBot is running", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
