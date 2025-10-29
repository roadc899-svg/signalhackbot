from flask import Flask, request, jsonify
import os
import requests
import time
import threading

app = Flask(__name__)

# ================================
# 🔰 Токен Telegram из Render Environment
# ================================
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ================================
# 🔰 Шаги загрузки с прогрессом
# ================================
LOADING_STEPS = [
    ("Conexión al sistema...", 0),
    ("Verificación de registro...", 12),
    ("Verificación de depósito...", 25),
    ("Análisis del historial de apuestas...", 40),
    ("Conexión de la cuenta a Lucky Mines...", 55),
    ("Recolección de datos del algoritmo de ubicación de minas...", 70),
    ("Creación de la primera señal...", 88),
    ("✅ Acceso al hackbot concedido.", 100),
]

# ================================
# 🔰 Генератор прогресс-бара
# ================================
def make_progress_bar(percent: int, length: int = 20) -> str:
    filled = int(length * percent / 100)
    empty = length - filled
    return f"[{'█' * filled}{'▒' * empty}] {percent}%"

# ================================
# 🔰 Отправка сообщений в Telegram
# ================================
def send_message(chat_id, text):
    """Отправляет сообщение пользователю"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Ошибка отправки:", e)

# ================================
# 🔰 Динамическая установка (анимация)
# ================================
def send_dynamic(chat_id):
    """Пошаговая анимация загрузки с прогресс-баром"""
    msg = None

    # Первое сообщение
    first_step, pct = LOADING_STEPS[0]
    bar = make_progress_bar(pct)
    msg = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": f"{first_step}\n{bar}"},
    ).json()

    message_id = msg.get("result", {}).get("message_id")

    # Обновляем прогресс
    for text, pct in LOADING_STEPS[1:]:
        time.sleep(1.5)
        bar = make_progress_bar(pct)
        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                json={
                    "chat_id": chat_id,
                    "message_id": message_id,
                    "text": f"{text}\n{bar}" if pct < 100 else text,
                },
            )
        except Exception as e:
            print("Ошибка при обновлении:", e)

    # ✅ После завершения можно вызвать SendPulse webhook
    print(f"✅ Установка завершена для chat_id={chat_id}")
    # тут можно добавить запрос в SendPulse API или webhook:
    # requests.post("https://api.sendpulse.com/webhook/...", json={"chat_id": chat_id})

# ================================
# 🔰 Flask Webhook
# ================================
@app.route("/", methods=["GET"])
def home():
    return "OK", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print("Получен запрос:", data)

    chat_id = str(data.get("chat_id", "")).strip()

    if chat_id.isdigit():
        threading.Thread(target=send_dynamic, args=(int(chat_id),), daemon=True).start()
        return jsonify({"ok": True, "status": "dynamic message started"}), 200
    else:
        return jsonify({"ok": False, "error": "invalid chat_id"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
