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
# 🔰 Generador de barra de progreso
# ================================
def make_progress_bar(percent: int, length: int = 20) -> str:
    filled = int(length * percent / 100)
    empty = length - filled
    return f"[{'█' * filled}{'▒' * empty}] {percent}%"

# ================================
# 🔰 Envío y edición de mensajes
# ================================
def send_message(chat_id, text):
    """Envía un nuevo mensaje"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    r = requests.post(url, json=payload)
    return r.json().get("result", {}).get("message_id")

def edit_message(chat_id, message_id, text):
    """Edita un mensaje existente"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)

# ================================
# 🔰 Animación de carga (15 segundos)
# ================================
def send_dynamic(chat_id):
    steps = [
        ("⚙️ Conectando al sistema 1xBet...", 10),
        ("🔍 Analizando el patrón de minas...", 25),
        ("🧠 Procesando los datos del servidor...", 50),
        ("🛠️ Preparando y optimizando la señal...", 75),
        ("✅ Señal lista", 100)
    ]

    # enviar primer mensaje
    first_step, pct = steps[0]
    bar = make_progress_bar(pct)
    message_id = send_message(chat_id, f"{first_step}\n{bar}")

    # actualizar el mensaje dinámicamente
    for text, pct in steps[1:]:
        time.sleep(3)  # ⏳ cada paso dura 3 segundos
        bar = make_progress_bar(pct)
        if pct == 100:
            success = round(random.uniform(85.0, 95.0), 1)
            edit_message(chat_id, message_id, f"✅ Señal lista — probabilidad de éxito: {success}%")
        else:
            edit_message(chat_id, message_id, f"{text}\n{bar}")

# ================================
# 🔰 Rutas Flask
# ================================
@app.route("/", methods=["GET"])
def home():
    return "OK", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    print("Solicitud recibida:", data)

    chat_id = str(data.get("chat_id", "")).replace("{", "").replace("}", "").strip()

    if chat_id.isdigit():
        threading.Thread(target=send_dynamic, args=(int(chat_id),), daemon=True).start()
        return jsonify({"ok": True, "status": "progreso iniciado"}), 200
    else:
        print("Error en chat_id:", chat_id)
        return jsonify({"ok": False, "error": f"chat_id inválido: {chat_id}"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
