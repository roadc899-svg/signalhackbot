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
    
    steps = [
        ("🧠 Подключение к системе...", 10),
        ("⚙️ Анализ аккаунта...", 25),
        ("💣 Сканирование мин...", 50),
        ("🧩 Обработка данных...", 75),
        ("✅ Доступ к HackBot открыт!", 100)
    ]
    
    messages = [{"text": f"{t} ({p}%)"} for t, p in steps]
    return jsonify({"dynamic_messages": messages, "user": user})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))