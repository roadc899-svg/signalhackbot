from flask import Flask, request, jsonify
import os
import requests
import time
import threading

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Укажи в Render → Environment → BOT_TOKEN

def send_message(chat_id, text):
    """Отправка текста пользователю в Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    requests.post(url, json=payload)

def send_dynamic(chat_id):
    """Динамическая анимация сообщений"""
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
    print("Получен запрос:", data)

    # Извлекаем chat_id из тела запроса
    chat_id = data.get("chat_id")

    if chat_id:
        threading.Thread(target=send_dynamic, args=(chat_id,), daemon=True).start()
        return jsonify({"ok": True, "status": "dynamic message sent"}), 200
    else:
        return jsonify({"ok": False, "error": "chat_id not found"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
