from datetime import timedelta

MAX_EVENTS = 7
MIN_GAP = 20

MIN_DONATE_ENERGY_TO_BONUS_KOEF = 600
TIME_EVENT_DONATE_ENERGY = 30
KOEF_DONATE_ENERGY = 0.4
BASE_KOEF_ADD_POWER = 0.2
TIME_BLITZ_FIGHT = timedelta(minutes=5)

DONE_ENERGY_PHOTOS = [
    "blitz_match/photos/done_energy.jpg",
    "blitz_match/photos/done_energy_2.jpg",
    "blitz_match/photos/done_energy_3.jpg",
]

NO_GOAL_PHOTOS_PATCH = [
    "blitz_match/photos/no_goal_1.jpg",
    "blitz_match/photos/no_goal_2.jpg",
    "blitz_match/photos/no_goal_3.jpg",
    "blitz_match/photos/no_goal_4.jpg",
    "blitz_match/photos/no_goal_5.jpg",
]

GOAL_PHOTOS_PATCH = [
    "blitz_match/photos/goal_1.jpg",
    "blitz_match/photos/goal_2.jpg",
    "blitz_match/photos/goal_3.jpg",
    "blitz_match/photos/goal_4.jpg",
    "blitz_match/photos/goal_5.jpg",
]

MVP_PHOTO_PATCH = "blitz_match/photos/mvp.jpg"
DONATE_ENERGY_PATCH_PHOTOS = [
    "blitz_match/photos/notification_send_energy_11.jpg",
    "blitz_match/photos/notification_send_energy_22.jpg",
]
SEND_INFO_CHARACTERS_PATCH_PHOTOS = [
    "blitz_match/photos/send_info_character_1.jpg",
    "blitz_match/photos/send_info_character_2.jpg",
    "blitz_match/photos/send_info_character_3.jpg",
]
END_blitz_match_PHOTOS_PATCH = [
    "blitz_match/photos/end_blitz_match_1.jpg",
    "blitz_match/photos/end_blitz_match_2.jpg",
    "blitz_match/photos/end_blitz_match_3.jpg",
]

START_blitz_match_PHOTO_PATCH = "blitz_match\photos\start_blitz_match_photo.jpg"

STAGE_MAP = {
    16: "1/16 фіналу",
    8: "1/8 фіналу",
    4: "1/4 фіналу",
    2: "1/2 фіналу",
    1: "ФІНАЛУ 🏆",
    0: "Матч за 3-є місце"
}
