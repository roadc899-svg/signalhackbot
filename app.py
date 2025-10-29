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
# 🔰 Отправка и обновление сообщений
# ================================
def send_message(chat_id, text):
    """Отправка нового сообщения"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    r = requests.post(url, json=payload)
    return r.json().get("result", {}).get("message_id")

def edit_message(chat_id, message_id, text):
    """Редактирование существующего сообщения"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)

# ================================
# 🔰 Анимация установки
# ================================
def send_dynamic(chat_id):
    steps = [
        ("🧠 Подключение к системе...", 10),
        ("⚙️ Проверка регистрации...", 25),
        ("💣 Сканирование мин...", 50),
        ("🧩 Обработка данных...", 75),
        ("✅ Доступ к HackBot открыт!", 100)
    ]

    # отправляем первое сообщение
    first_step, pct = steps[0]
    bar = make_progress_bar(pct)
    message_id = send_message(chat_id, f"{first_step}\n{bar}")

    # редактируем его дальше
    for text, pct in steps[1:]:
        time.sleep(1.2)
        bar = make_progress_bar(pct)
        edit_message(chat_id, message_id, f"{text}\n{bar}")

    # 👇 если нужно вызвать Chatterfy Webhook после завершения (например, следующий блок)
    # requests.post("https://chatterfy.io/.../webhook", json={"chat_id": chat_id})

# ================================
# 🔰 Flask маршруты
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
        return jsonify({"ok": True, "status": "edit progress started"}), 200
    else:
        print("Ошибка chat_id:", chat_id)
        return jsonify({"ok": False, "error": f"invalid chat_id: {chat_id}"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
