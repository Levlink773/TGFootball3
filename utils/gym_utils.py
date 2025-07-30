from database.models.club import Club

def get_text_training_facilities(club: Club) -> str:
    options_text = (
        "1️⃣ 100 енергії - Усилення на 10%\n"
        "2️⃣ 200 енергії - Усилення на 15%\n"
        "3️⃣ 300 енергії - Усилення на 20%\n"
        "4️⃣ 400 енергії - Усилення на 25%\n"
        "5️⃣ 500 енергії - Усилення на 30%\n"
    )

    if club.koef_energy == 1.0:
        boost_status = "Ваша команда енергія не підвищена."
    else:
        boost_percentage_value = int((club.koef_energy - 1) * 100)
        boost_status = f"Поточне посилення команди: {boost_percentage_value}%"

    total_energy_collected = club.energy_applied

    if total_energy_collected > 500:
        max_energy = 500
    elif total_energy_collected > 400:
        max_energy = 500
    elif total_energy_collected > 300:
        max_energy = 400
    elif total_energy_collected > 200:
        max_energy = 300
    elif total_energy_collected > 100:
        max_energy = 200
    else:
        max_energy = 100

    progress_text = f"🟢 Зібрано енергії: {int(total_energy_collected)}/{max_energy}"

    text = f"""
💪 Виберіть, скільки енергії хочете пожертвувати своїй команді

АБО

👉 Впишіть кількість енергії, або виберіть один з варіантів нижче:

{options_text}

🎮 {boost_status}

{progress_text}

Ваша пожертва допоможе вашій команді стати сильнішим! 💥
    """
    
    return text