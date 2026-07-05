import random
from typing import List

from sqlalchemy.orm import selectinload

from database.models.character import Character
from database.models.reminder_character import ReminderCharacter
from database.models.item import Item
from database.models.statistics import Statistics
from database.models.user_bot import UserBot, STATUS_USER_REGISTER

from database.session import get_session
from sqlalchemy import select, update, or_, delete
from config import CONST_ENERGY, CONST_VIP_ENERGY
from datetime import datetime, timedelta
from enum import Enum

from constants import PositionCharacter

from logging_config import logger
from stats.stat_enum import StatisticsType
from stats.tier import TIER_LIST


class CharacterService:
    @classmethod
    async def get_all_characters(cls) -> list[Character]:
        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    select(Character)
                )
                all_characters_not_bot = result.unique().scalars().all()
                return all_characters_not_bot

    @classmethod
    async def get_all_characters_where_end_training(clc) -> list[Character]:
        months_ago = datetime.now() - timedelta(days=30)
        async for session in get_session():
            stmt = (
                select(Character)
                .where(Character.is_bot == False)
                .join(Character.owner)  # join по foreign key characters_user_id
                .where(UserBot.status_register == STATUS_USER_REGISTER.END_TRAINING)
                .join(ReminderCharacter)
                .where(
                    or_(
                        ReminderCharacter.education_reward_date >= months_ago,
                        ReminderCharacter.time_to_join_club >= months_ago
                    )
                )
                .options(
                    selectinload(Character.owner),
                    selectinload(Character.club),
                    selectinload(Character.reminder),
                    selectinload(Character.t_shirt),
                    selectinload(Character.shorts),
                    selectinload(Character.gaiters),
                    selectinload(Character.boots),
                )
            )
            result = await session.execute(stmt)
            return list(result.scalars().all())

    @classmethod
    async def get_all_users_not_bot(cls) -> list[Character]:
        two_months_ago = datetime.now() - timedelta(days=60)
        async for session in get_session():
            async with session.begin():
                stmt = (
                    select(Character)
                    .where(Character.is_bot == False)
                    .join(ReminderCharacter)
                    .where(
                        or_(
                            ReminderCharacter.education_reward_date >= two_months_ago,
                            ReminderCharacter.time_to_join_club >= two_months_ago
                        )
                    )
                )
                result = await session.execute(stmt)
                all_characters_not_bot = result.unique().scalars().all()
                return all_characters_not_bot

    @classmethod
    async def get_all_characters_not_bot(cls) -> list[Character]:
        # Hall-of-fame boards: ALL real players, no recent-activity gate.
        # get_all_users_not_bot() is scoped to users active in the last 60 days
        # (correct for notifications/newsletters, which share it) — a fame board
        # should rank the whole real playerbase, not just recently-active ones.
        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    select(Character).where(Character.is_bot == False)
                )
                return result.unique().scalars().all()

    @classmethod
    async def get_character(cls, character_user_id: int) -> Character:
        async for session in get_session():
            async with session.begin():
                # One character per user is enforced by a UNIQUE constraint on
                # characters_user_id. The order_by + limit(1) is a safety net so a
                # stray duplicate can NEVER crash rendering again — previously this
                # used scalar_one_or_none() which raised MultipleResultsFound and
                # took down every club view (create team / Моя команда / club list).
                result = await session.execute(
                    select(Character)
                    .where(Character.characters_user_id == character_user_id)
                    .order_by(
                        Character.club_id.isnot(None).desc(),
                        Character.exp.desc(),
                        Character.money.desc(),
                        Character.id.asc(),
                    )
                    .limit(1)
                )
                return result.scalars().first()

    @classmethod
    async def get_character_by_id(cls, character_id: int) -> Character:
        async for session in get_session():
            async with session.begin():
                result = await session.execute(
                    select(Character).where(Character.id == character_id)
                )
                current_character = result.scalar_one_or_none()
                return current_character

    @classmethod
    async def create_character(cls, character_obj: Character) -> Character:
        character_obj.gender = character_obj.gender.value
        character_obj.position = character_obj.position.value

        async for session in get_session():
            async with session.begin():
                # get-or-create: never insert a second character for a user_id.
                # This, plus the DB UNIQUE constraint on characters_user_id, is the
                # root-cause fix for the duplicate-character pileup. Rows without a
                # user_id (bots/orphans) are exempt — UNIQUE allows multiple NULLs.
                uid = character_obj.characters_user_id
                if uid is not None:
                    existing = await session.execute(
                        select(Character)
                        .where(Character.characters_user_id == uid)
                        .order_by(
                            Character.club_id.isnot(None).desc(),
                            Character.exp.desc(),
                            Character.id.asc(),
                        )
                        .limit(1)
                    )
                    found = existing.scalars().first()
                    if found is not None:
                        return found
                session.add(character_obj)
                await session.flush()
                return character_obj

    @classmethod
    async def update_character_characteristic(cls, character_id: int, type_characteristic: str,
                                              amount_add_points: int) -> Character:
        async for session in get_session():
            async with session as sess:
                try:
                    stmt = (
                        update(Character)
                        .where(Character.id == character_id)
                        .values({type_characteristic: getattr(Character, type_characteristic) + amount_add_points})
                    )
                    await sess.execute(stmt)
                    await sess.commit()
                except Exception as E:
                    logger.error(
                        f"Ошибка при изменении характеристики у персонажа с ID {character_id}. "
                        f"Характеристика: '{type_characteristic}', добавленные очки: {amount_add_points}. "
                        f"Текст ошибки: {E}"
                    )

    @classmethod
    async def update_training_params(cls, character_obj: Character, characteristic: str,
                                     training_time: datetime) -> Character:
        async for session in get_session():
            async with session.begin():
                try:
                    session.add(character_obj)
                except:
                    pass
                merged_obj = await session.merge(character_obj)
                setattr(merged_obj, 'training_characteristic', characteristic)
                setattr(merged_obj, 'time_character_training', training_time)
                await session.commit()
                return merged_obj

    @classmethod
    async def consume_energy(cls, character_id: int, energy_consumed: int) -> Character:
        async for session in get_session():
            async with session.begin():
                character = await session.get(Character, character_id)
                if character:
                    character.current_energy -= energy_consumed
                    await session.flush()

    @classmethod
    async def edit_character_energy(
            cls,
            character_id: int,
            amount_energy: int) -> Character:
        async for session in get_session():
            async with session.begin():
                character = await session.get(Character, character_id)
                if character:
                    character.current_energy = (character.current_energy or 0) + amount_energy
                    await session.flush()

    @classmethod
    async def update_character_club_id(cls, character: Character, club_id: int):
        async for session in get_session():
            async with session.begin():
                try:
                    session.add(character)
                except:
                    pass
                character.club_id = club_id
                if not character.is_bot:
                    character.reminder.time_to_join_club = datetime.now()
                merged_obj = await session.merge(character)
                await session.commit()
                return merged_obj

    @classmethod
    async def update_energy_for_non_bots(cls):
        async for session in get_session():
            async with session.begin():
                try:
                    stmt = (
                        update(Character)
                        .where(Character.is_bot == False)
                        .where(Character.current_energy <= CONST_ENERGY)
                        .values(current_energy=CONST_ENERGY)
                    )
                    stmt_vip = (
                        update(Character)
                        .where(Character.is_bot == False)
                        .where(Character.vip_pass_expiration_date > datetime.now())
                        .where(Character.current_energy <= CONST_VIP_ENERGY)
                        .values(current_energy=CONST_VIP_ENERGY)
                    )
                    await session.execute(stmt)
                    await session.execute(stmt_vip)
                    await session.commit()
                except Exception as e:
                    raise e

    @classmethod
    async def get_character_how_update_energy(cls) -> list[Character]:
        async for session in get_session():
            async with session.begin():
                try:
                    result = await session.execute(
                        select(Character)
                        .where(Character.is_bot == False)
                        .where(Character.current_energy <= CONST_ENERGY)
                        .where(Character.vip_pass_expiration_date <= datetime.now())
                    )
                    all_characters_not_bot = result.unique().scalars().all()
                    return all_characters_not_bot
                except Exception as e:
                    raise e

    @classmethod
    async def leave_club(cls, character: Character):
        async for session in get_session():
            async with session.begin():
                try:
                    character.club_id = None
                    session.add(character)
                    merged_obj = await session.merge(character)
                    await session.commit()
                    return merged_obj
                except Exception as e:
                    await session.rollback()
                    raise e

    @classmethod
    async def update_money_character(cls, character_id: int, amount_money_adjustment: int):
        async for session in get_session():
            async with session.begin():
                stmt = (
                    update(Character)
                    .where(Character.id == character_id)
                    .values(money=Character.money + amount_money_adjustment)
                )
                await session.execute(stmt)
                await session.commit()

    @classmethod
    async def add_exp_character(cls, character_id: int, amount_exp_add: int):
        async for session in get_session():
            async with session.begin():
                stmt_select = select(Character).where(Character.id == character_id)
                result = await session.execute(stmt_select)
                character = result.scalar_one()

                character.exp += amount_exp_add

                session.add(character)
                await session.commit()

    @classmethod
    async def update_character_education_time(cls, character: Character, amount_add_time: timedelta):
        async for session in get_session():
            async with session.begin():
                try:
                    session.add(character)
                except:
                    pass
                character.reminder.education_reward_date = datetime.now() + amount_add_time
                merged_obj = await session.merge(character)
                await session.commit()
                return merged_obj

    @classmethod
    async def equip_item(cls, character_obj: Character, item_obj: Item) -> Character:
        category_field_map = {
            'T_SHIRT': 't_shirt_id',
            'SHORTS': 'shorts_id',
            'GAITERS': 'gaiters_id',
            'BOOTS': 'boots_id'
        }
        item_category = item_obj.category.value.upper() if isinstance(item_obj.category,
                                                                      Enum) else item_obj.category.upper()
        field_name = category_field_map.get(item_category)

        async for session in get_session():
            async with session.begin():
                try:
                    session.add(character_obj)
                except:
                    pass

                merged_character = await session.merge(character_obj)
                setattr(merged_character, field_name, item_obj.id)
                await session.commit()

                return merged_character

    @classmethod
    async def edit_status_reward_by_referal(cls, character_user_id: int):
        async for session in get_session():
            async with session.begin():
                stmt = (
                    update(Character)
                    .where(Character.characters_user_id == character_user_id)
                    .values(referral_award_is_received=True)
                )
                await session.execute(stmt)
                await session.commit()

    @classmethod
    async def get_my_referals(cls, character_user_id: int):
        async for session in get_session():
            async with session.begin():
                try:
                    result = await session.execute(
                        select(Character)
                        .where(Character.referal_user_id == character_user_id))
                    all_characters_not_bot = result.unique().scalars().all()
                    return all_characters_not_bot
                except Exception as e:
                    raise e

    @classmethod
    async def change_position(
            cls,
            character_id: Character,
            position: str
    ):
        async for session in get_session():
            async with session.begin():
                stmt = (
                    update(Character)
                    .where(Character.id == character_id)
                    .values(position=position)
                )
                await session.execute(stmt)
                await session.commit()

    @classmethod
    async def add_trainin_key(
            cls,
            character_id: int,
    ):
        async for session in get_session():
            async with session.begin():
                stmt = (
                    update(Character)
                    .where(Character.id == character_id)
                    .values(training_key=Character.training_key + 1)
                )
                await session.execute(stmt)
                await session.commit()

    @classmethod
    async def remove_training_key(
            cls,
            character_id: int,
    ):
        async for session in get_session():
            async with session.begin():
                stmt = (
                    update(Character)
                    .where(Character.id == character_id)
                    .values(training_key=Character.training_key - 1)
                )
                await session.execute(stmt)
                await session.commit()

    @classmethod
    async def get_characters_by_position(
            cls,
            position: PositionCharacter
    ) -> list[Character]:

        async for session in get_session():
            async with session.begin():
                stmt = (
                    select(Character)
                    .where(Character.position == position.value)
                    .where(Character.is_bot == False)
                )

                result = await session.execute(stmt)
                characters = result.unique().scalars().all()
                return characters

    @classmethod
    async def update_get_new_member_bonus(
            cls,
            character_id: int,
    ):
        async for session in get_session():
            async with session.begin():
                stmt = (
                    update(Character)
                    .where(Character.id == character_id)
                    .values(time_get_member_bonus=datetime.now())
                )
                await session.execute(stmt)
                await session.commit()

    @classmethod
    async def anulate_statistics(cls, char_id: int):
        async for session in get_session():
            async with session.begin():
                try:
                    stmt_select = select(Character).where(Character.id == char_id)
                    result = await session.execute(stmt_select)
                    char: Character = result.scalar_one_or_none()

                    char.count_go_to_gym = 0
                    char.count_play_blitz = 0
                    char.count_rich_final_looser_blitz = 0
                    char.count_rich_semi_final_blitz = 0
                    char.count_rich_final_winner_blitz = 0
                    char.count_goal_on_match = 0
                    char.count_register_on_match = 0
                    char.count_mvp_two_and_more = 0
                    char.count_mvp_two_half_and_more = 0
                    char.count_mvp_three_and_more = 0

                    stmt = delete(Statistics).where(Statistics.character_id == char_id)
                    await session.execute(stmt)
                except Exception as e:
                    raise e

    @classmethod
    async def add_count_play_blitz_user(cls, char_id: int, amount: int):
        async for session in get_session():
            async with session.begin():
                stmt_select = select(Character).where(Character.id == char_id)
                result = await session.execute(stmt_select)
                char: Character = result.scalar_one()
                if char.count_play_blitz:
                    char.count_play_blitz += amount
                else:
                    char.count_play_blitz = amount
                session.add(char)
                await session.commit()

    @classmethod
    async def add_count_go_to_gym(cls, char_id: int, amount: int):
        async for session in get_session():
            async with session.begin():
                stmt_select = select(Character).where(Character.id == char_id)
                result = await session.execute(stmt_select)
                char: Character = result.scalar_one()
                if char.count_go_to_gym:
                   char.count_go_to_gym += amount
                else:
                    char.count_go_to_gym = amount

                session.add(char)
                await session.commit()

    @classmethod
    async def add_count_register_on_match(cls, char_id: int, amount: int):
        async for session in get_session():
            async with session.begin():
                stmt_select = select(Character).where(Character.id == char_id)
                result = await session.execute(stmt_select)
                char: Character = result.scalar_one()
                if char.count_register_on_match:
                    char.count_register_on_match += amount
                else:
                    char.count_register_on_match = amount

                session.add(char)
                await session.commit()

    @classmethod
    async def add_count_rich_final_winner_blitz(cls, char_id: int, amount: int):
        async for session in get_session():
            async with session.begin():
                stmt_select = select(Character).where(Character.id == char_id)
                result = await session.execute(stmt_select)
                char: Character = result.scalar_one()
                if char.count_rich_final_winner_blitz:
                    char.count_rich_final_winner_blitz += amount
                else:
                    char.count_rich_final_winner_blitz = amount

                session.add(char)
                await session.commit()

    @classmethod
    async def add_count_mvp_three_and_more(cls, char_id: int, amount: int):
        async for session in get_session():
            async with session.begin():
                stmt_select = select(Character).where(Character.id == char_id)
                result = await session.execute(stmt_select)
                char: Character = result.scalar_one()
                if char.count_mvp_three_and_more:
                    char.count_mvp_three_and_more += amount
                else:
                    char.count_mvp_three_and_more = amount

                session.add(char)
                await session.commit()

    @classmethod
    async def add_count_mvp_two_half_and_more(cls, char_id: int, amount: int):
        async for session in get_session():
            async with session.begin():
                stmt_select = select(Character).where(Character.id == char_id)
                result = await session.execute(stmt_select)
                char: Character = result.scalar_one()
                if char.count_mvp_two_half_and_more:
                    char.count_mvp_two_half_and_more += amount
                else:
                    char.count_mvp_two_half_and_more = amount

                session.add(char)
                await session.commit()

    @classmethod
    async def add_count_mvp_two_and_more(cls, char_id: int, amount: int):
        async for session in get_session():
            async with session.begin():
                stmt_select = select(Character).where(Character.id == char_id)
                result = await session.execute(stmt_select)
                char: Character = result.scalar_one()
                if char.count_mvp_two_and_more:
                    char.count_mvp_two_and_more += amount
                else:
                    char.count_mvp_two_and_more = amount

                session.add(char)
                await session.commit()

    @classmethod
    async def add_count_rich_final_looser_blitz(cls, char_id: int, amount: int):
        async for session in get_session():
            async with session.begin():
                stmt_select = select(Character).where(Character.id == char_id)
                result = await session.execute(stmt_select)
                char: Character = result.scalar_one()
                if char.count_rich_final_looser_blitz:
                    char.count_rich_final_looser_blitz += amount
                else:
                    char.count_rich_final_looser_blitz = amount
                session.add(char)
                await session.commit()

    @classmethod
    async def add_count_rich_semi_final_blitz(cls, char_id: int, amount: int):
        async for session in get_session():
            async with session.begin():
                stmt_select = select(Character).where(Character.id == char_id)
                result = await session.execute(stmt_select)
                char: Character = result.scalar_one()
                if char.count_rich_semi_final_blitz:
                    char.count_rich_semi_final_blitz += amount
                else:
                    char.count_rich_semi_final_blitz = amount
                session.add(char)
                await session.commit()

    @classmethod
    async def add_count_goal(cls, char_id: int, amount: int):
        async for session in get_session():
            async with session.begin():
                stmt_select = select(Character).where(Character.id == char_id)
                result = await session.execute(stmt_select)
                char: Character = result.scalar_one()
                if char.count_goal_on_match:
                    char.count_goal_on_match += amount
                else:
                    char.count_goal_on_match = amount
                session.add(char)
                await session.commit()

    @classmethod
    async def edit_tier_cipher(cls, char_id: int, tier_cip: str):
        async for session in get_session():
            async with session.begin():
                stmt_select = select(Character).where(Character.id == char_id)
                result = await session.execute(stmt_select)
                char: Character = result.scalar_one()

                char.tier_cipher = tier_cip

                session.add(char)
                await session.commit()

    @staticmethod
    async def generate_new_tier_cipher(char_id: int) -> None:
        """Сгенерировать новый cipher и сохранить в БД."""
        async for session in get_session():
            stmt_select = select(Character).where(Character.id == char_id)
            result = await session.execute(stmt_select)
            char: Character = result.scalar_one()

            choices = []
            for tier in TIER_LIST:
                stats_list = tier[1]
                idx = random.randint(1, len(stats_list))  # индексы с 1
                choices.append(str(idx))
            char.tier_cipher = ",".join(choices)

            session.add(char)
            await session.commit()

    @staticmethod
    def decrypt_tier_cipher(cipher: str) -> List[StatisticsType]:
        """
        Декодировать cipher (например, "1,3,2") в список StatisticsType.
        """
        if not cipher:
            return []

        parts = cipher.split(",")
        result: List[StatisticsType] = []

        for tier_idx, choice_str in enumerate(parts):
            try:
                choice = int(choice_str)
                stats_list = TIER_LIST[tier_idx][1]  # список заданий конкретного tier
                if 1 <= choice <= len(stats_list):
                    result.append(stats_list[choice - 1])
            except Exception as e:
                print(f"Ошибка при расшифровке tier_cipher: {e}")

        return result