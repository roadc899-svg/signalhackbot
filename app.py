from flask import Flask, request, jsonify
import os
import requests
import time
import threading

app = Flask(__name__)

# ================================
# 🔰 Токен Telegram
# ================================
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ================================
# 🔰 Генератор прогресс-бара
# ================================
def make_progress_bar(percent: int, length: int = 20) -> str:
    filled = int(length * percent / 100)
    empty = length - filled
    return f"[{'█' * filled}{'▒' * empty}] {percent}%"

# ================================
# 🔰 Отправка сообщения
# ================================
def send_message(chat_id, text):
    """Отправка текста пользователю в Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Ошибка отправки:", e)

# ================================
# 🔰 Эмуляция загрузки (анимация)
# ================================
def send_dynamic(chat_id):
    """Пошаговая динамическая загрузка"""
    steps = [
        ("🧠 Подключение к системе...", 10),
        ("⚙️ Проверка регистрации...", 25),
        ("💣 Сканирование мин...", 50),
        ("🧩 Обработка данных...", 75),
        ("✅ Доступ к HackBot открыт!", 100)
    ]

    for text, pct in steps:
        bar = make_progress_bar(pct)
        send_message(chat_id, f"{text}\n{bar}")
        time.sleep(1.2)  # пауза между шагами

    # здесь можно вызвать следующий webhook в Chatterfy (если нужно):
    # requests.post("https://api.chatterfy.io/.../webhook", json={"chat_id": chat_id})

# ================================
# 🔰 Главная и Webhook
# ================================
@app.route("/", methods=["GET"])
def home():
    return "OK", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print("Получен запрос:", data)

    chat_id = str(data.get("chat_id", "")).replace("{", "").replace("}", "").strip()

    if chat_id.isdigit():
        threading.Thread(target=send_dynamic, args=(int(chat_id),), daemon=True).start()
        return jsonify({"ok": True, "status": "dynamic message started"}), 200
    else:
        print("Ошибка chat_id:", chat_id)
        return jsonify({"ok": False, "error": f"invalid chat_id: {chat_id}"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
