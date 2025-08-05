from datetime import timedelta

MAX_EVENTS = 7
MIN_GAP = 20

MIN_DONATE_ENERGY_TO_BONUS_KOEF = 200
TIME_EVENT_DONATE_ENERGY = 30
KOEF_DONATE_ENERGY = 2
BASE_KOEF_ADD_POWER = 1
TIME_BLITZ_FIGHT = timedelta(minutes=5)

DONE_ENERGY_PHOTOS = [
    "blitz/blitz_match/photos/done_energy.jpg",
    "blitz/blitz_match/photos/done_energy_2.jpg",
    "blitz/blitz_match/photos/done_energy_3.jpg",
]

NO_GOAL_PHOTOS_PATCH = [
    "blitz/blitz_match/photos/no_goal_1.jpg",
    "blitz/blitz_match/photos/no_goal_2.jpg",
    "blitz/blitz_match/photos/no_goal_3.jpg",
    "blitz/blitz_match/photos/no_goal_4.jpg",
    "blitz/blitz_match/photos/no_goal_5.jpg",
]

GOAL_PHOTOS_PATCH = [
    "blitz/blitz_match/photos/goal_1.jpg",
    "blitz/blitz_match/photos/goal_2.jpg",
    "blitz/blitz_match/photos/goal_3.jpg",
    "blitz/blitz_match/photos/goal_4.jpg",
    "blitz/blitz_match/photos/goal_5.jpg",
]

MVP_PHOTO_PATCH = "blitz/blitz_match/photos/mvp.jpg"
DONATE_ENERGY_PATCH_PHOTOS = [
    "blitz/blitz_match/photos/notification_send_energy_11.png",
    "blitz/blitz_match/photos/notification_send_energy_22.png",
]
SEND_INFO_CHARACTERS_PATCH_PHOTOS = [
    "blitz/blitz_match/photos/send_info_character_1.jpg",
    "blitz/blitz_match/photos/send_info_character_2.jpg",
    "blitz/blitz_match/photos/send_info_character_3.jpg",
]
END_MATCH_PHOTOS_PATCH = [
    "blitz/blitz_match/photos/end_match_1.jpg",
    "blitz/blitz_match/photos/end_match_2.jpg",
    "blitz/blitz_match/photos/end_match_3.jpg",
]

START_MATCH_PHOTO_PATCH = "blitz/blitz_match/photos/start_match_photo.jpg"
START_BLITZ_PHOTO = "blitz/blitz_match/photos/start_blitz.png"
END_BLITZ_PHOTO = "blitz/blitz_match/photos/end_blitz.png"
TEAM_BLITZ_PHOTO = "blitz/blitz_match/photos/team.png"
SMALL_BOX_BLITZ_PHOTO = "blitz/blitz_match/photos/small_blitz_box.jpg"
MEDIUM_BOX_BLITZ_PHOTO = "blitz/blitz_match/photos/medium_blitz_box.jpg"
BLITZ_STAGES_PATCH = [
    "blitz/blitz_match/photos/1v8.png",
    "blitz/blitz_match/photos/1v4.png",
    "blitz/blitz_match/photos/1v2.jpg",
    "blitz/blitz_match/photos/final.jpg",
]
REGISTER_BLITZ_PHOTO = "blitz/blitz_match/photos/reg_blitz.jpg"
STAGE_MAP = {
    16: "1/16 фіналу",
    8: "1/8 фіналу",
    4: "1/4 фіналу",
    2: "1/2 фіналу",
    1: "ФІНАЛУ 🏆",
    0: "Матч за 3-є місце"
}
