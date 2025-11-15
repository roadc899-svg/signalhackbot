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
        ("⚙️ Conectando al sistema 1xBet...", 10),
        ("🔍 Analizando el patrón de minas...", 30),
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


# ----- CHICKEN ROAD -----
def send_dynamic_chicken(chat_id):

    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("🐔 Escaneando el mapa...", 20),
        ("🚗 Analizando rutas seguras...", 45),
        ("🧠 Cálculo de zonas peligrosas...", 70),
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

            # 🔥 удалить через 10 секунд
            delete_after(chat_id, msg_id, 10)

        else:
            edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")


# ----- PENALTY -----
def send_dynamic_penalty(chat_id):

    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("⚽ Analizando portero...", 20),
        ("🎯 Calculando trayectoria óptima...", 55),
        ("🔥 Preparando disparo perfecto...", 85),
        ("🏆 Señal lista", 100)
    ]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(2.5)
        if pct == 100:
            edit_message(chat_id, msg_id, "⚽ Señal lista — ¡dispara y marca gol! 🏆")

            # 🔥 удалить финальное через 10 сек
            delete_after(chat_id, msg_id, 10)

        else:
            edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")


# ----- AVIATOR -----
def send_dynamic_aviator(chat_id):

    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("✈️ Escaneando historial…", 15),
        ("📊 Analizando volatilidad…", 40),
        ("🧠 Predicción de X optimo…", 75),
        ("🔥 Señal lista", 100)
    ]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(3)
        if pct == 100:
            x = round(random.uniform(1.5, 3.8), 2)
            edit_message(chat_id, msg_id, f"✈️ Señal lista — retírate en X{x} 🚀")

            # 🔥 удалить сигнал через 10 сек
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


@app.route("/webhook_aviator", methods=["POST"])
def webhook_aviator():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(target=send_dynamic_aviator, args=(int(chat_id),), daemon=True).start()
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
