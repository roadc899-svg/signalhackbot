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


V2_TEXTS = {
    "spanish": {
        "lucky_mines_steps": [
            ("⚙️ Conectando al sistema...", 10),
            ("🔍 Analizando la ubicación de las minas...", 30),
            ("🧠 Calculando probabilidad...", 60),
            ("🛠️ Optimizando la señal...", 85),
            ("💣 Señal lista", 100),
        ],
        "lucky_mines_generating": "💣 Generando Lucky Mines...",
        "lucky_mines_title": "💣 <b>SEÑAL LUCKY MINES</b>",
        "lucky_mines_success": "🎯 Éxito: {success}%",
        "lucky_mines_cells": "⭐ Celdas afortunadas: {lucky_cells}",
        "chicken_steps": [
            ("⚙️ Conectando al sistema Chicken Road...", 20),
            ("🐔 Escaneando el campo de juego...", 40),
            ("🧩 Analizando las celdas seguras...", 60),
            ("📊 Evaluando multiplicadores...", 75),
            ("🧠 Calculando el punto óptimo de salida...", 90),
            ("✅ Señal lista", 100),
        ],
        "chicken_title": "🐔 <b>SEÑAL CHICKEN ROAD</b>",
        "mode": "🎮 Modo: <b>Medio</b>",
        "safe_steps_green": "🟩 Pasos seguros: <b>{safe_steps}</b>",
        "safe_steps_carrot": "🥕 Pasos seguros: <b>{safe_steps}</b>",
        "coefficient": "📍 Coeficiente: <b>X{stop_x}</b>",
        "recommended_cashout": "📍 Retiro recomendado: <b>X{stop_x}</b>",
        "estimated_accuracy": "🎯 Precisión estimada: <b>{success}%</b>",
        "penalty_steps": [
            ("⚙️ Conectando al sistema Penalty...", 10),
            ("🧤 Analizando al portero...", 30),
            ("🎯 Calculando trayectoria del disparo...", 60),
            ("🛠️ Optimizando señal...", 85),
            ("⚽ Señal lista", 100),
        ],
        "penalty_generating": "⚽ Generando señal Penalty...",
        "penalty_title": "⚽ <b>SEÑAL PENALTY</b>",
        "penalty_accuracy": "🎯 Precisión: {success}%",
        "penalty_balls": "⚽ Balones favorables: {balls}",
        "aviator_steps": [
            ("⚙️ Conectando al sistema Aviator...", 15),
            ("✈️ Escaneando vuelos recientes...", 35),
            ("📊 Analizando patrones de coeficientes...", 55),
            ("🧠 Calculando punto óptimo de salida...", 75),
            ("🔥 Optimizando señal...", 90),
            ("✅ Señal lista", 100),
        ],
        "aviator_title": "✈️ <b>SEÑAL AVIATOR</b>",
        "rabbit_steps": [
            ("⚙️ Conectando al sistema Rabbit Road...", 15),
            ("🥕 Escaneando las rutas del conejo...", 35),
            ("✋ Detectando manos atrapadoras...", 55),
            ("📊 Analizando multiplicadores seguros...", 75),
            ("🧠 Calculando punto óptimo de salida...", 90),
            ("✅ Señal lista", 100),
        ],
        "rabbit_title": "🐰 <b>SEÑAL RABBIT ROAD</b>",
        "balloonix_steps": [
            ("⚙️ Conectando al sistema BallooniX...", 15),
            ("🎈 Analizando el inflado del globo...", 35),
            ("📡 Escaneando patrones de explosión...", 55),
            ("🧠 Calculando punto óptimo de salida...", 75),
            ("🔥 Optimizando señal...", 90),
            ("✅ Señal lista", 100),
        ],
        "balloonix_title": "🎈 <b>SEÑAL BALLOONIX</b>",
        "risk_warning": "⚠️ No persigas multiplicadores altos",
        "wait_next_round": "🔥 Retira y espera la próxima ronda",
    },
    "english": {
        "lucky_mines_steps": [
            ("⚙️ Connecting to the system...", 10),
            ("🔍 Analyzing mine locations...", 30),
            ("🧠 Calculating probability...", 60),
            ("🛠️ Optimizing the signal...", 85),
            ("💣 Signal ready", 100),
        ],
        "lucky_mines_generating": "💣 Generating Lucky Mines...",
        "lucky_mines_title": "💣 <b>LUCKY MINES SIGNAL</b>",
        "lucky_mines_success": "🎯 Success: {success}%",
        "lucky_mines_cells": "⭐ Lucky cells: {lucky_cells}",
        "chicken_steps": [
            ("⚙️ Connecting to the Chicken Road system...", 20),
            ("🐔 Scanning the game field...", 40),
            ("🧩 Analyzing safe cells...", 60),
            ("📊 Evaluating multipliers...", 75),
            ("🧠 Calculating the optimal cashout point...", 90),
            ("✅ Signal ready", 100),
        ],
        "chicken_title": "🐔 <b>CHICKEN ROAD SIGNAL</b>",
        "mode": "🎮 Mode: <b>Medium</b>",
        "safe_steps_green": "🟩 Safe steps: <b>{safe_steps}</b>",
        "safe_steps_carrot": "🥕 Safe steps: <b>{safe_steps}</b>",
        "coefficient": "📍 Coefficient: <b>X{stop_x}</b>",
        "recommended_cashout": "📍 Recommended cashout: <b>X{stop_x}</b>",
        "estimated_accuracy": "🎯 Estimated accuracy: <b>{success}%</b>",
        "penalty_steps": [
            ("⚙️ Connecting to the Penalty system...", 10),
            ("🧤 Analyzing the goalkeeper...", 30),
            ("🎯 Calculating shot trajectory...", 60),
            ("🛠️ Optimizing the signal...", 85),
            ("⚽ Signal ready", 100),
        ],
        "penalty_generating": "⚽ Generating Penalty signal...",
        "penalty_title": "⚽ <b>PENALTY SIGNAL</b>",
        "penalty_accuracy": "🎯 Accuracy: {success}%",
        "penalty_balls": "⚽ Favorable balls: {balls}",
        "aviator_steps": [
            ("⚙️ Connecting to the Aviator system...", 15),
            ("✈️ Scanning recent flights...", 35),
            ("📊 Analyzing coefficient patterns...", 55),
            ("🧠 Calculating the optimal cashout point...", 75),
            ("🔥 Optimizing the signal...", 90),
            ("✅ Signal ready", 100),
        ],
        "aviator_title": "✈️ <b>AVIATOR SIGNAL</b>",
        "rabbit_steps": [
            ("⚙️ Connecting to the Rabbit Road system...", 15),
            ("🥕 Scanning the rabbit paths...", 35),
            ("✋ Detecting trap hands...", 55),
            ("📊 Analyzing safe multipliers...", 75),
            ("🧠 Calculating the optimal cashout point...", 90),
            ("✅ Signal ready", 100),
        ],
        "rabbit_title": "🐰 <b>RABBIT ROAD SIGNAL</b>",
        "balloonix_steps": [
            ("⚙️ Connecting to the BallooniX system...", 15),
            ("🎈 Analyzing balloon inflation...", 35),
            ("📡 Scanning burst patterns...", 55),
            ("🧠 Calculating the optimal cashout point...", 75),
            ("🔥 Optimizing the signal...", 90),
            ("✅ Signal ready", 100),
        ],
        "balloonix_title": "🎈 <b>BALLOONIX SIGNAL</b>",
        "risk_warning": "⚠️ Do not chase high multipliers",
        "wait_next_round": "🔥 Cash out and wait for the next round",
    },
    "malay": {
        "lucky_mines_steps": [
            ("⚙️ Menyambung ke sistem...", 10),
            ("🔍 Menganalisis lokasi ranjau...", 30),
            ("🧠 Mengira kebarangkalian...", 60),
            ("🛠️ Mengoptimumkan isyarat...", 85),
            ("💣 Isyarat sedia", 100),
        ],
        "lucky_mines_generating": "💣 Menjana Lucky Mines...",
        "lucky_mines_title": "💣 <b>ISYARAT LUCKY MINES</b>",
        "lucky_mines_success": "🎯 Kejayaan: {success}%",
        "lucky_mines_cells": "⭐ Sel bertuah: {lucky_cells}",
        "chicken_steps": [
            ("⚙️ Menyambung ke sistem Chicken Road...", 20),
            ("🐔 Mengimbas medan permainan...", 40),
            ("🧩 Menganalisis sel selamat...", 60),
            ("📊 Menilai pengganda...", 75),
            ("🧠 Mengira titik keluar yang optimum...", 90),
            ("✅ Isyarat sedia", 100),
        ],
        "chicken_title": "🐔 <b>ISYARAT CHICKEN ROAD</b>",
        "mode": "🎮 Mod: <b>Sederhana</b>",
        "safe_steps_green": "🟩 Langkah selamat: <b>{safe_steps}</b>",
        "safe_steps_carrot": "🥕 Langkah selamat: <b>{safe_steps}</b>",
        "coefficient": "📍 Koefisien: <b>X{stop_x}</b>",
        "recommended_cashout": "📍 Pengeluaran disyorkan: <b>X{stop_x}</b>",
        "estimated_accuracy": "🎯 Ketepatan anggaran: <b>{success}%</b>",
        "penalty_steps": [
            ("⚙️ Menyambung ke sistem Penalty...", 10),
            ("🧤 Menganalisis penjaga gol...", 30),
            ("🎯 Mengira trajektori tendangan...", 60),
            ("🛠️ Mengoptimumkan isyarat...", 85),
            ("⚽ Isyarat sedia", 100),
        ],
        "penalty_generating": "⚽ Menjana isyarat Penalty...",
        "penalty_title": "⚽ <b>ISYARAT PENALTY</b>",
        "penalty_accuracy": "🎯 Ketepatan: {success}%",
        "penalty_balls": "⚽ Bola menguntungkan: {balls}",
        "aviator_steps": [
            ("⚙️ Menyambung ke sistem Aviator...", 15),
            ("✈️ Mengimbas penerbangan terkini...", 35),
            ("📊 Menganalisis corak koefisien...", 55),
            ("🧠 Mengira titik keluar yang optimum...", 75),
            ("🔥 Mengoptimumkan isyarat...", 90),
            ("✅ Isyarat sedia", 100),
        ],
        "aviator_title": "✈️ <b>ISYARAT AVIATOR</b>",
        "rabbit_steps": [
            ("⚙️ Menyambung ke sistem Rabbit Road...", 15),
            ("🥕 Mengimbas laluan arnab...", 35),
            ("✋ Mengesan tangan perangkap...", 55),
            ("📊 Menganalisis pengganda selamat...", 75),
            ("🧠 Mengira titik keluar yang optimum...", 90),
            ("✅ Isyarat sedia", 100),
        ],
        "rabbit_title": "🐰 <b>ISYARAT RABBIT ROAD</b>",
        "balloonix_steps": [
            ("⚙️ Menyambung ke sistem BallooniX...", 15),
            ("🎈 Menganalisis pengembangan belon...", 35),
            ("📡 Mengimbas corak letupan...", 55),
            ("🧠 Mengira titik keluar yang optimum...", 75),
            ("🔥 Mengoptimumkan isyarat...", 90),
            ("✅ Isyarat sedia", 100),
        ],
        "balloonix_title": "🎈 <b>ISYARAT BALLOONIX</b>",
        "risk_warning": "⚠️ Jangan kejar pengganda tinggi",
        "wait_next_round": "🔥 Keluarkan dan tunggu pusingan seterusnya",
    },
}


def get_v2_texts(language):
    return V2_TEXTS.get(language, V2_TEXTS["spanish"])

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
        ("⚙️ Conectando al sistema...", 10),
        ("🔍 Analizando la ubicación de las minas...", 30),
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


# ----- LUCKY MINES (обновлённая версия с синим полем и прогресс-баром) -----
def send_dynamic_luckymines(chat_id, language="spanish"):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    texts = get_v2_texts(language)
    steps = texts["lucky_mines_steps"]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(3)
        edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")

    size = 5
    lucky_cells = random.choice([2, 3])
    star_positions = random.sample(range(size * size), lucky_cells)
    grid = ["🟦"] * (size * size)

    for pos in star_positions:
        time.sleep(0.5)
        grid[pos] = "⭐"
        field_text = "\n".join(
            [" ".join(grid[i*size:(i+1)*size]) for i in range(size)]
        )
        edit_message(chat_id, msg_id, f"{texts['lucky_mines_generating']}\n\n{field_text}")

    success = round(random.uniform(90, 99), 1)
    final_text = (
        f"{texts['lucky_mines_title']}\n"
        f"{texts['lucky_mines_success'].format(success=success)}\n"
        f"{texts['lucky_mines_cells'].format(lucky_cells=lucky_cells)}\n\n"
        f"{field_text}\n\n"
        f"{texts['risk_warning']}\n{texts['wait_next_round']}"
    )
    edit_message(chat_id, msg_id, final_text)

    delete_after(chat_id, msg_id, 25)


# ----- CHICKEN ROAD -----
def send_dynamic_chicken(chat_id):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("⚙️ Conectando al sistema...", 20),
        ("🐔 Escaneando el campo...", 40),
        ("🧩 Analizando las celdas seguras...", 60),
        ("🧠 Verificando probabilidades...", 80),
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
            delete_after(chat_id, msg_id, 10)
        else:
            edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")

# ----- CHICKEN ROAD V2 (señal dinámica por pasos) -----
def send_dynamic_chicken_v2(chat_id, language="spanish"):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    texts = get_v2_texts(language)
    steps = texts["chicken_steps"]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(2.5)
        edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")

    safe_steps = random.randint(1, 5)
    stop_x_table = {
        1: 1.12,
        2: 1.28,
        3: 1.47,
        4: 1.70,
        5: 1.98
    }

    stop_x = stop_x_table[safe_steps]
    success = round(random.uniform(87, 95), 1)

    final_text = (
        f"{texts['chicken_title']}\n\n"
        f"{texts['mode']}\n"
        f"{texts['safe_steps_green'].format(safe_steps=safe_steps)}\n"
        f"{texts['coefficient'].format(stop_x=stop_x)}\n"
        f"{texts['estimated_accuracy'].format(success=success)}\n\n"
        f"{texts['risk_warning']}\n{texts['wait_next_round']}"
    )

    edit_message(chat_id, msg_id, final_text)
    delete_after(chat_id, msg_id, 20)

# ----- PENALTY -----
def send_dynamic_penalty(chat_id):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("⚙️ Conectando al sistema...", 15),
        ("⚽ Analizando al portero...", 35),
        ("🎯 Calculando la trayectoria óptima...", 60),
        ("🔥 Preparando el tiro perfecto...", 85),
        ("🏆 Señal lista", 100)
    ]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(2.5)
        if pct == 100:
            edit_message(chat_id, msg_id, "⚽ Señal lista — ¡dispara y marca gol! 🏆")
            delete_after(chat_id, msg_id, 10)
        else:
            edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")
            
# ----- PENALTY V2 -----
def send_dynamic_penalty_v2(chat_id, language="spanish"):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    texts = get_v2_texts(language)
    steps = texts["penalty_steps"]

    first_text, pct = steps[0]
    msg_id = send_message(chat_id, f"{first_text}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(3)
        edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")

    rows = 3
    cols = 5
    balls = random.randint(1, 2)

    total_cells = rows * cols
    ball_positions = random.sample(range(total_cells), balls)
    grid = ["🟦"] * total_cells

    for pos in ball_positions:
        time.sleep(0.6)
        grid[pos] = "⚽"
        field_text = "\n".join(
            [" ".join(grid[i*cols:(i+1)*cols]) for i in range(rows)]
        )
        edit_message(chat_id, msg_id, f"{texts['penalty_generating']}\n\n{field_text}")

    success = round(random.uniform(90, 99), 1)
    final_text = (
        f"{texts['penalty_title']}\n"
        f"{texts['penalty_accuracy'].format(success=success)}\n"
        f"{texts['penalty_balls'].format(balls=balls)}\n\n"
        f"{field_text}\n\n"
        f"{texts['risk_warning']}\n{texts['wait_next_round']}"
    )
    edit_message(chat_id, msg_id, final_text)
    delete_after(chat_id, msg_id, 25)



# ----- AVIATOR -----
def send_dynamic_aviator(chat_id):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("⚙️ Conectando al sistema...", 15),
        ("✈️ Escaneando los últimos coeficientes…", 35),
        ("📊 Analizando el comportamiento del avión…", 60),
        ("🧠 Predicción del coeficiente X óptimo…", 85),
        ("🔥 Señal lista", 100)
    ]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(3)
        if pct == 100:
            x = round(random.uniform(1.2, 3.3), 2)
            edit_message(chat_id, msg_id, f"✈️ Señal lista — retírate en X{x} 🚀")
            delete_after(chat_id, msg_id, 10)
        else:
            edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")
            
# ----- AVIATOR V2 (señal dinámica con salida X) -----
def send_dynamic_aviator_v2(chat_id, language="spanish"):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    texts = get_v2_texts(language)
    steps = texts["aviator_steps"]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(2.5)
        edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")

    stop_x = round(random.uniform(1.20, 1.98), 2)
    success = round(random.uniform(88, 96), 1)

    final_text = (
        f"{texts['aviator_title']}\n\n"
        f"{texts['recommended_cashout'].format(stop_x=stop_x)}\n"
        f"{texts['estimated_accuracy'].format(success=success)}\n\n"
        f"{texts['risk_warning']}\n{texts['wait_next_round']}"
    )

    edit_message(chat_id, msg_id, final_text)

    delete_after(chat_id, msg_id, 20)


# ----- RABBIT ROAD -----
def send_dynamic_rabbit(chat_id):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("⚙️ Conectando al sistema...", 15),
        ("🥕 Escaneando los cultivos de zanahorias...", 35),
        ("✋ Analizando la aparición de manos atrapadoras...", 60),
        ("🧠 Calculando pasos seguros...", 85),
        ("✅ Señal lista", 100)
    ]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(2.5)
        if pct == 100:
            edit_message(chat_id, msg_id, "🐰 Señal lista — evita las manos atrapadoras, recoge la zanahoria y detente 🥕🔥")
            delete_after(chat_id, msg_id, 10)
        else:
            edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")
            
# ----- RABBIT ROAD V2 (динамический шаговый сигнал) -----
def send_dynamic_rabbit_v2(chat_id, language="spanish"):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    texts = get_v2_texts(language)
    steps = texts["rabbit_steps"]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(2.5)
        edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")

    safe_steps = random.randint(1, 5)

    stop_x_table = {
        1: 1.08,
        2: 1.21,
        3: 1.37,
        4: 1.56,
        5: 1.78
    }
    stop_x = stop_x_table[safe_steps]
    success = round(random.uniform(88, 96), 1)

    final_text = (
        f"{texts['rabbit_title']}\n\n"
        f"{texts['mode']}\n"
        f"{texts['safe_steps_carrot'].format(safe_steps=safe_steps)}\n"
        f"{texts['coefficient'].format(stop_x=stop_x)}\n"
        f"{texts['estimated_accuracy'].format(success=success)}\n\n"
        f"{texts['risk_warning']}\n{texts['wait_next_round']}"
    )

    edit_message(chat_id, msg_id, final_text)
    delete_after(chat_id, msg_id, 20)



# ----- BALLOONIX -----
def send_dynamic_balloonix(chat_id):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("⚙️ Conectando al sistema BallooniX...", 15),
        ("🎈 Analizando el inflado del globo...", 35),
        ("📡 Escaneando patrones de explosión...", 60),
        ("🧠 Calculando punto óptimo de salida...", 85),
        ("🔥 Señal lista", 100)
    ]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(3)
        if pct == 100:
            x = round(random.uniform(1.3, 1.98), 2)
            edit_message(chat_id, msg_id, f"🎈 Señal BallooniX lista — retírate en X{x} 🚀")
            delete_after(chat_id, msg_id, 10)
        else:
            edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")
            
# ----- BALLOONIX V2 (señal dinámica con salida X) -----
def send_dynamic_balloonix_v2(chat_id, language="spanish"):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    texts = get_v2_texts(language)
    steps = texts["balloonix_steps"]

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(2.5)
        edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")

    stop_x = round(random.uniform(1.2, 1.98), 2)
    success = round(random.uniform(88, 97), 1)

    final_text = (
        f"{texts['balloonix_title']}\n\n"
        f"{texts['recommended_cashout'].format(stop_x=stop_x)}\n"
        f"{texts['estimated_accuracy'].format(success=success)}\n\n"
        f"{texts['risk_warning']}\n{texts['wait_next_round']}"
    )

    edit_message(chat_id, msg_id, final_text)

    delete_after(chat_id, msg_id, 20)


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

@app.route("/webhook_mines_v2", methods=["POST"])
@app.route("/webhook_mines_v2_spanish", methods=["POST"])
def webhook_luckymines():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(target=send_dynamic_luckymines, args=(int(chat_id), "spanish"), daemon=True).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_mines_v2_english", methods=["POST"])
def webhook_luckymines_english():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(target=send_dynamic_luckymines, args=(int(chat_id), "english"), daemon=True).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_mines_v2_malay", methods=["POST"])
def webhook_luckymines_malay():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(target=send_dynamic_luckymines, args=(int(chat_id), "malay"), daemon=True).start()
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

@app.route("/webhook_penalty_v2", methods=["POST"])
@app.route("/webhook_penalty_v2_spanish", methods=["POST"])
def webhook_penalty_v2():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_penalty_v2,
            args=(int(chat_id), "spanish"),
            daemon=True
        ).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_penalty_v2_english", methods=["POST"])
def webhook_penalty_v2_english():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_penalty_v2,
            args=(int(chat_id), "english"),
            daemon=True
        ).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_penalty_v2_malay", methods=["POST"])
def webhook_penalty_v2_malay():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_penalty_v2,
            args=(int(chat_id), "malay"),
            daemon=True
        ).start()
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

@app.route("/webhook_aviator_v2", methods=["POST"])
@app.route("/webhook_aviator_v2_spanish", methods=["POST"])
def webhook_aviator_v2():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_aviator_v2,
            args=(int(chat_id), "spanish"),
            daemon=True
        ).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_aviator_v2_english", methods=["POST"])
def webhook_aviator_v2_english():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_aviator_v2,
            args=(int(chat_id), "english"),
            daemon=True
        ).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_aviator_v2_malay", methods=["POST"])
def webhook_aviator_v2_malay():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_aviator_v2,
            args=(int(chat_id), "malay"),
            daemon=True
        ).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_rabbit", methods=["POST"])
def webhook_rabbit():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(target=send_dynamic_rabbit, args=(int(chat_id),), daemon=True).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_balloonix", methods=["POST"])
def webhook_balloonix():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(target=send_dynamic_balloonix, args=(int(chat_id),), daemon=True).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_rabbit_v2", methods=["POST"])
@app.route("/webhook_rabbit_v2_spanish", methods=["POST"])
def webhook_rabbit_v2():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_rabbit_v2,
            args=(int(chat_id), "spanish"),
            daemon=True
        ).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_rabbit_v2_english", methods=["POST"])
def webhook_rabbit_v2_english():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_rabbit_v2,
            args=(int(chat_id), "english"),
            daemon=True
        ).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_rabbit_v2_malay", methods=["POST"])
def webhook_rabbit_v2_malay():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_rabbit_v2,
            args=(int(chat_id), "malay"),
            daemon=True
        ).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_chicken_v2", methods=["POST"])
@app.route("/webhook_chicken_v2_spanish", methods=["POST"])
def webhook_chicken_v2():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_chicken_v2,
            args=(int(chat_id), "spanish"),
            daemon=True
        ).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_chicken_v2_english", methods=["POST"])
def webhook_chicken_v2_english():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_chicken_v2,
            args=(int(chat_id), "english"),
            daemon=True
        ).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_chicken_v2_malay", methods=["POST"])
def webhook_chicken_v2_malay():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_chicken_v2,
            args=(int(chat_id), "malay"),
            daemon=True
        ).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_balloonix_v2", methods=["POST"])
@app.route("/webhook_balloonix_v2_spanish", methods=["POST"])
def webhook_balloonix_v2():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_balloonix_v2,
            args=(int(chat_id), "spanish"),
            daemon=True
        ).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_balloonix_v2_english", methods=["POST"])
def webhook_balloonix_v2_english():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_balloonix_v2,
            args=(int(chat_id), "english"),
            daemon=True
        ).start()
        return jsonify(ok=True)
    return jsonify(error="chat_id not found"), 400

@app.route("/webhook_balloonix_v2_malay", methods=["POST"])
def webhook_balloonix_v2_malay():
    data = request.get_json(force=True)
    chat_id = extract_chat_id(data)
    if chat_id:
        threading.Thread(
            target=send_dynamic_balloonix_v2,
            args=(int(chat_id), "malay"),
            daemon=True
        ).start()
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
