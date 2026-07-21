from aiogram.filters.callback_data import CallbackData

class SelectClubToJoin(CallbackData, prefix="select_club"):
    club_id: int
    
class SelectClubToView(CallbackData, prefix="view_club"):
    club_id: int
    
class JoinToClub(CallbackData, prefix = "join_to_club"):
    club_id: int
    
class LeaveThisClub(CallbackData, prefix = "leave_club"):
    club_id: int
    
class TransferOwner(CallbackData, prefix="transfer_owner"):
    user_id_new_owner: int
    
class DeleteClub(CallbackData, prefix="delete_club"):
    club_id: int
    
class SelectSchema(CallbackData, prefix="select_shema"):
    select_schema: str
    
class ViewCharatcerClub(CallbackData, prefix= "view_character_club"):
    club_id: int
    
class KickMember(CallbackData, prefix = "kick_member"):
    character_id: int
    
class SelectPhotoStadion(CallbackData, prefix = "select_photo_stadion"):
    patch_to_photo: str
    
class ApprovedPhotoStadion(CallbackData, prefix = "aproved_photo_stadion"):
    patch_to_photo: str
    
class InvoiceClubCallback(CallbackData, prefix = "functional_invite_club"):
    club_id: int
    is_approved: bool
    character_id: int
