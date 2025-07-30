import io

from bot.utils.xls.base_xls import BaseXLS
from database.models.character import Character
from services.user_service import UserService

class GenerateNewMemberXLS(BaseXLS):
    HEADERS = [
        "ID користувача",
        "Нікнейм (@username)",
        "Ім'я персонажа",
        "Дата регістрації",
        "Сила персонажа",
        "Позиція",
        "Кількість грошей",
        "Досвід | Рівень",
        "Назва клубу",
        "Останнє тренування",
        "Запрошений (@username)",
        "VIP статус (до коли)",
        
    ]


    def __init__(self, members: list[Character]):
        super().__init__(members)
        self.current_sheet.title = "Нові гравці"
        self.header_setings()
        
    async def generate_xls(self) -> None:
        for member in self.members:
            
            user = await UserService.get_user(member.characters_user_id)
            referred_by = None
            
            if member.referal_user_id:
                referred_user = await UserService.get_user(member.referal_user_id)
                referred_by = f"@{referred_user.user_name}" if referred_user and referred_user.user_name else "Невідомо"

            vip_status = (
                f"Активний до {member.vip_pass_expiration_date.strftime('%Y-%m-%d %H:%M:%S')}"
                if member.vip_pass_is_active else "Неактивний"
            )
            try:
                last_traning = member.reminder.time_start_training.strftime('%Y-%m-%d %H:%M:%S') if member.reminder.time_start_training else "Немає даних"
            except:
                last_traning = "Немає даних"
            self.current_sheet.append([
                member.characters_user_id,
                f"@{user.user_name}" if user and user.user_name else "Невідомо",
                member.character_name,
                member.created_at,
                member.full_power,
                member.position_enum.value if member.position_enum else "Невідома",
                member.money,
                f"{member.exp} | {member.level} рівень",
                member.club.name_club if member.club else "Без клубу",
                last_traning,
                referred_by,
                vip_status,
            ])
            if user and user.user_name:
                telegram_link = f"https://t.me/{user.user_name}"
                row_index = self.current_sheet.max_row
                col_index = 5  # Колонка с ссылкой (Telegram)
                cell = self.current_sheet.cell(row=row_index, column=col_index)
                cell.hyperlink = telegram_link
                cell.style = "Hyperlink"

            
    def save_to_bytes(self) -> bytes:
        self.set_base_settings()
        with io.BytesIO() as output:
            self.workbook.save(output)
            output.seek(0)
            return output.read()