def send_dynamic_luckymines(chat_id):
    if chat_id in last_messages:
        delete_message(chat_id, last_messages[chat_id])

    steps = [
        ("⚙️ Conectando al sistema...", 10),
        ("🔍 Analizando la ubicación de las minas...", 30),
        ("🧠 Calculando probabilidad...", 60),
        ("🛠️ Optimizando la señal...", 85),
        ("💣 Señal lista", 100)
    ]

    # Отправляем первое сообщение с прогресс-баром
    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    # Обновление прогресса
    for text, pct in steps[1:]:
        time.sleep(3)
        edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")

    # Настройки поля
    size = 5
    lucky_cells = 3  # только 3 звезды
    star_positions = random.sample(range(size * size), lucky_cells)
    grid = ["🟦"] * (size * size)

    # Анимация появления звезд перед финальным сообщением
    for pos in star_positions:
        time.sleep(0.5)
        grid[pos] = "⭐"
        field_text = "\n".join(
            [" ".join(grid[i*size:(i+1)*size]) for i in range(size)]
        )
        edit_message(chat_id, msg_id, f"💎 Generando Lucky Mines...\n\n{field_text}")

    # Финальное сообщение с шансом успеха
    success = round(random.uniform(90, 99), 1)
    final_text = (
        f"💎 <b>Señal Lucky lista</b>\n"
        f"🎯 Éxito: {success}%\n"
        f"⭐ Celdas afortunadas: {lucky_cells}\n\n"
        f"{field_text}\n\n"
        f"⚠️ ¡Juega con suerte!"
    )
    edit_message(chat_id, msg_id, final_text)

    # Удаление через 25 секунд
    delete_after(chat_id, msg_id, 25)
