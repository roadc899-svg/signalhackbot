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
# 🔰 Хранение ID последнего сообщения
# ================================
last_messages = {}   # { chat_id: message_id }


# ================================
# 🔰 Функция для поиска chat_id в JSON
# ================================
def extract_chat_id(payload):
    """Recursively search for chat_id in JSON structure"""

    # Если список
    if isinstance(payload, list):
        for item in payload:
            cid = extract_chat_id(item)
            if cid:
                return cid
        return None

    # Если словарь
    if isinstance(payload, dict):

        # Прямые ключи
        for key in ["chat_id", "telegram_id"]:
            if key in payload and str(payload[key]).isdigit():
                return payload[key]

        # Ищем внутри
        for key, value in payload.items():
            cid = extract_chat_id(value)
            if cid:
                return cid

    return None


# ================================
# 🔰 Telegram: отправка сообщения
# ================================
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    r = requests.post(url, json=payload)
    return r.json().get("result", {}).get("message_id")


# ================================
# 🔰 Telegram: редактирование сообщения
# ================================
def edit_message(chat_id, message_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)


# ================================
# 🔰 Telegram: удаление сообщения
# ================================
def delete_message(chat_id, message_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage"
    payload = {"chat_id": chat_id, "message_id": message_id}
    requests.post(url, json=payload)


# ================================
# 🔰 Генератор прогресс-бара
# ================================
def make_progress_bar(percent: int, length: int = 20) -> str:
    filled = int(length * percent / 100)
    empty = length - filled
    return f"[{'█' * filled}{'▒' * empty}] {percent}%"


# ================================
# 🔰 Анимация загрузки + автоудаление прошлого сообщения
# ================================
def send_dynamic(chat_id):

    # Удаляем предыдущее сообщение, если было
    if chat_id in last_messages:
        try:
            delete_message(chat_id, last_messages[chat_id])
        except Exception as e:
            print("Error deleting previous message:", e)

    steps = [
        ("⚙️ Conectando al sistema 1xBet...", 10),
        ("🔍 Analizando el patrón de minas...", 25),
        ("🧠 Procesando los datos del servidor...", 50),
        ("🛠️ Preparando y optimizando la señal...", 75),
        ("✅ Señal lista", 100)
    ]

    # Отправляем первое сообщение
    first_step, pct = steps[0]
    bar = make_progress_bar(pct)
    message_id = send_message(chat_id, f"{first_step}\n{bar}")

    # Сохраняем ID последнего сообщения
    last_messages[chat_id] = message_id

    # Анимация
    for text, pct in steps[1:]:
        time.sleep(3)
        bar = make_progress_bar(pct)

        if pct == 100:
            success = round(random.uniform(85.0, 95.0), 1)
            edit_message(chat_id, message_id,
                         f"✅ Señal lista — probabilidad de éxito: {success}%")
        else:
            edit_message(chat_id, message_id, f"{text}\n{bar}")


# ================================
# 🔰 Webhook для SendPulse
# ================================
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print("RAW JSON:", data)

    chat_id = extract_chat_id(data)
    print("CHAT ID DETECTADO:", chat_id)

    if chat_id:
        threading.Thread(target=send_dynamic,
                         args=(int(chat_id),),
                         daemon=True).start()
        return jsonify({"ok": True}), 200

    return jsonify({"ok": False, "error": "chat_id not found"}), 400


# ================================
# 🔰 Home
# ================================
@app.route("/", methods=["GET"])
def home():
    return "HackBot is running", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
