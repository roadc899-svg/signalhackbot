from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "OK", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json() or {}
    user = data.get("user", {}).get("name", "друг")

    # Полное сообщение, которое Chatterfy сразу отобразит
    message = f"""
👋 Привет, {user}!

🧠 Подключение к системе... (10%)
⚙️ Анализ аккаунта... (25%)
💣 Сканирование мин... (50%)
🧩 Обработка данных... (75%)
✅ Доступ к HackBot открыт! (100%)
"""

    # Возвращаем только одно текстовое поле — Chatterfy сразу его покажет
    return jsonify({"text": message})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
