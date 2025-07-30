from aiogram import Bot
from aiogram.enums import ChatMemberStatus

from database.models.character import Character

from config import MAIN_CHAT_GROUP_ID

from loader import bot

class ChannelTitelService:
    
    title: str = "[V.I.P]"
    _bot: Bot = bot
    _chat_id: int = MAIN_CHAT_GROUP_ID
    
    def __init__(self, character: Character) -> None:
        self.character = character
        
    async def get_title(self) -> None:
        user_in_chat = await self._check_user_in_group()
        if not user_in_chat:
            return
        await self._promote_to_admin()
        await self._set_title()
        
    async def _check_user_in_group(self) -> bool:
        chat_member = await bot.get_chat_member(
            chat_id=self._chat_id,
            user_id=self.character.characters_user_id
        )
        return chat_member.status in [
            ChatMemberStatus.MEMBER, 
            ChatMemberStatus.CREATOR, 
            ChatMemberStatus.ADMINISTRATOR
        ]
    
        
    async def _promote_to_admin(self) -> None:
        await bot.promote_chat_member(
            chat_id=self._chat_id,
            user_id=self.character.characters_user_id,
            is_anonymous = False,
            can_manage_chat = False,
            can_delete_messages = False,
            can_manage_video_chats = False,
            can_restrict_members = False,
            can_promote_members = False,
            can_change_info = False,
            can_invite_users = True,
            can_post_stories = False,
            can_edit_stories = False,
            can_delete_stories = False,
            can_post_messages = False,
            can_edit_messages = False,
            can_pin_messages = False,
            can_manage_topics = False
            )
            
    async def _downgrade_to_user(self) -> None:
        await bot.promote_chat_member(
            chat_id=self._chat_id,
            user_id=self.character.characters_user_id,
            can_invite_users=False
        )

        
    async def _set_title(self) -> None:
        await self._bot.set_chat_administrator_custom_title(
            chat_id=self._chat_id,
            user_id=self.character.characters_user_id,
            custom_title=self.title
        )
    
    