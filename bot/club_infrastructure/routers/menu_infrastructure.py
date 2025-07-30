from aiogram import Router
from aiogram.types import CallbackQuery

from bot.club_infrastructure.callbacks.infrastructure_callbacks import SelectMenuInfrastructure
from bot.club_infrastructure.constans import START_PHOTO_INFRASTUCTURE
from bot.club_infrastructure.keyboards.menu_infrastructure import menu_infrastructure
from bot.club_infrastructure.filters.get_club_and_infrastructure import GetClubAndInfrastructure

from database.models.club_infrastructure import ClubInfrastructure

start_menu_infrastructure_router = Router()

starter_text = """
<b>🏟 Інфраструктурний модуль клубу</b>
<b>Кількість очок</b> : <b><u>{count_club_points}</u></b> 🎖

Розвинена інфраструктура допомагає команді досягати нових висот. Вкладайте ресурси в розвиток клубу, покращуйте гравців та збільшуйте шанси на перемогу!  

Доступні об’єкти інфраструктури:

🏋‍♂ <b>Тренувальна база</b> – покращує якість тренувань, збільшуючи шанс їх успішного проведення.  
📚 <b>Навчальний центр</b> – розвиває гравців та підвищує їх рівень, збільшуючи винагороди за навчання.  
🏆 <b>Преміальний фонд</b> – мотивує команду, збільшуючи нагороди за перемоги в матчах.  
🏟 <b>Стадіон</b> – розвиває клубну інфраструктуру, залучаючи більше фанатів та збільшуючи дохід.  
🏥 <b>Спортивна медицина</b> – прискорює відновлення гравців, зменшуючи час між тренуваннями.  
🌟 <b>Академія талантів</b> – готує молодих гравців, підвищуючи базову силу команди.  

Розвивайте інфраструктуру та ведіть свій клуб до слави! ⚽🔥
"""


@start_menu_infrastructure_router.callback_query(
    SelectMenuInfrastructure.filter(),
    GetClubAndInfrastructure()
)
async def start_command_handler(
    query: CallbackQuery,
    callback_data: SelectMenuInfrastructure,
    club_infrastructure: ClubInfrastructure

):
    await query.message.answer_photo(
        photo = START_PHOTO_INFRASTUCTURE,
        caption = starter_text.format(
            count_club_points = club_infrastructure.points
        ),
        reply_markup = menu_infrastructure(
            is_owner = callback_data.character_is_owner
        )
    )   
    
    
    