from flask import Flask, request, jsonify
import os
import requests
import time
import threading

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Отправка сообщения пользователю
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    requests.post(url, json=payload)

# Динамическая последовательность
def send_dynamic(chat_id):
    steps = [
        "🧠 Подключение к системе... (10%)",
        "⚙️ Анализ аккаунта... (25%)",
        "💣 Сканирование мин... (50%)",
        "🧩 Обработка данных... (75%)",
        "✅ Доступ к HackBot открыт! (100%)"
    ]
    for step in steps:
        send_message(chat_id, step)
        time.sleep(1.5)

@app.route("/", methods=["GET"])
def home():
    return "OK", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print("Получен апдейт:", data)

    # Проверяем, есть ли chat_id
    chat_id = None
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
    elif "callback_query" in data:  # если кнопка
        chat_id = data["callback_query"]["message"]["chat"]["id"]

    if chat_id:
        threading.Thread(target=send_dynamic, args=(chat_id,)).start()
        return jsonify({"ok": True})
    else:
        return jsonify({"ok": False, "error": "chat_id not found"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
