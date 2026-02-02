# ----- LUCKY MINES (обновлённая версия с синим полем и прогресс-баром) -----
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

    first, pct = steps[0]
    msg_id = send_message(chat_id, f"{first}\n{make_progress_bar(pct)}")
    last_messages[chat_id] = msg_id

    for text, pct in steps[1:]:
        time.sleep(3)
        if pct == 100:
            # финальные параметры
            success = round(random.uniform(90, 99), 1)
            lucky_cells = random.randint(4, 7)
            size = 5
            star_positions = random.sample(range(size * size), lucky_cells)

            # создаём синее поле
            empty_field = ["🟦"] * (size * size)
            field_text = "\n".join(
                [" ".join(empty_field[i*size:(i+1)*size]) for i in range(size)]
            )

            final_text = (
                f"💎 <b>Señal Lucky lista</b>\n"
                f"🎯 Éxito: {success}%\n"
                f"⭐ Celdas afortunadas: {lucky_cells}\n\n"
                f"{field_text}\n\n"
                f"⚠️ ¡Juega con suerte!"
            )

            edit_message(chat_id, msg_id, final_text)

            # запускаем анимацию появления звезд на синем поле
            threading.Thread(
                target=reveal_stars_animation,
                args=(chat_id, msg_id, size, star_positions, 0.5),
                daemon=True
            ).start()

            # удалить финальное сообщение через 25 секунд
            delete_after(chat_id, msg_id, 25)
        else:
            edit_message(chat_id, msg_id, f"{text}\n{make_progress_bar(pct)}")


# Анимация звезд для Lucky Mines (синее поле)
def reveal_stars_animation(chat_id, message_id, size, star_positions, delay=0.5):
    total = size * size
    grid = ["🟦"] * total

    for pos in star_positions:
        time.sleep(delay)
        grid[pos] = "⭐"

        rows = []
        for i in range(size):
            row = grid[i*size:(i+1)*size]
            rows.append(" ".join(row))

        field_text = "\n".join(rows)
        edit_message(chat_id, message_id, f"💎 <b>Señal Lucky lista</b>\n\n{field_text}")
