from aiogram import Router, F
from aiogram.types import  CallbackQuery

from datetime import datetime

from database.models.character import Character

from services.club_service import ClubService
from services.character_service import CharacterService
from services.match_character_service import MatchCharacterService
from services.club_shemas_service import SchemaSerivce


from bot.callbacks.league_callbacks import  JoinToFight, ViewCharacterRegisteredInMatch
from bot.keyboards.gym_keyboard import alert_leave_from_gym


from match.core.manager import ClubMatchManager


join_to_fight_router = Router()



@join_to_fight_router.callback_query(JoinToFight.filter())
async def join_to_match(query: CallbackQuery, callback_data: JoinToFight, character: Character):
    if character.reminder.character_in_training:
        return await query.message.answer(
            text = "Ваш персонаж на тренуванні, ви не можете взяти участь у матчі",
            reply_markup = alert_leave_from_gym() 
        )
    
    match_data = ClubMatchManager.get_match(
        match_id=callback_data.match_id
    )
    if not match_data:
        return await query.answer("Не зміг знайти матч", show_alert= True)
    
    
    current_time = datetime.now()
    if current_time > match_data.start_time:
        await query.answer(
            text="❌ Даний матч уже закінчився"
        )
        return await query.message.delete()
    
    if not character.club_id:
        return await query.message.answer("❌ У цього персонажа немає команди")
    
    
    character_in_match = await MatchCharacterService.get_character_in_match(
        match_id = match_data.match_id,
        club_id  = character.club_id,
        character_id = character.id,
        group_id = match_data.group_id
    )
    
    if character_in_match:
        return  await query.answer("❌ Ваш персонаж уже й так бере участь у цьому матчі")
    
    character_is_join_schema = await SchemaSerivce.character_is_enough_room(
        club=character.club,
        match_id=match_data.match_id,
        my_character=character
    )
    if not character_is_join_schema:
        return await query.answer("Для вас уже немає місця за схемою", show_alert=True)
    

        
    await MatchCharacterService.add_character_in_match(
        match_id = match_data.match_id,
        club_id  = character.club_id,
        group_id = match_data.group_id,
        character_id = character.id,
    )
    await CharacterService.add_count_register_on_match(character.id, 1)
    await query.message.answer(text = "✅ <b>Ваш персонаж був доданий на матч</b>")
    await query.message.edit_reply_markup(reply_markup=None)


       
        

@join_to_fight_router.callback_query(ViewCharacterRegisteredInMatch.filter())
async def join_to_match(query: CallbackQuery, callback_data: ViewCharacterRegisteredInMatch, character: Character):
    character_club_in_match = await MatchCharacterService.get_charaters_club_in_match(
        match_id=callback_data.match_id,
        club_id=character.club_id
    )
    
    if not character_club_in_match:
        return await query.message.answer("На даний матч <b>ніхто з команди ще не зареєструвався</b>")
    
    total_power = 0
    text = "🏆 <b>На матч зареєструвались</b>:\n\n"
    for match_character in character_club_in_match:
        character = await CharacterService.get_character_by_id(match_character.character_id)
        text += f"👤 {character.character_name} <b>[{character.full_power:.2f}]</b> [<b>{character.acronym_position}</b>]\n"
        total_power += character.full_power
        
    text += f"\n💪 <b>Загальна сила персонажей</b> {total_power:.2f}"
    
    await query.message.answer(text)