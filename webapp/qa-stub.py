#!/usr/bin/env python3
"""QA stub API for local visual verification of the webapp (no real DB).
Run: python3 qa-stub.py  (port 8765). Pair with webapp/.env.local VITE_API_URL.
"""
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

F = {
    "/api/player": {
        "user_id": 1, "name": "Андрій Шевчук", "position": "Півзахисник", "gender": "MAN",
        "exp": 120, "level": 7, "money": 25740, "energy": 120,
        "stats": {"technique": 86, "kicks": 81, "ball_selection": 78, "speed": 89, "endurance": 84},
        "full_power": 1876, "vip_active": True, "tier": 1,
        "club": {"id": 1, "name": "London United Lions", "league": "Вища ліга"},
    },
    "/api/tutorial": {"completed": False},
    "/api/tutorial/complete": {"completed": True},
    "/api/matches": {
        "blitz": {"next": {"start_at": "2026-07-22T15:00:00", "participants": 12, "max_players": 150,
                            "registered": False, "can_register": True},
                   "schedule": [{"time": "15:00"}, {"time": "19:00"}]},
        "leagues": [{"type": "league", "name": "Ліга", "is_active": True, "day_start": 1, "day_end": 28,
                     "next_match": {"match_id": 1, "opponent_club_name": "Madrid Rovers Wolves",
                                     "time_to_start": "2026-07-22T21:00:00", "registered": False}}],
    },
    "/api/shop": {
        "me": {"money": 25740, "energy": 120, "level": 7, "owned_items": []},
        "items": [
            {"id": 1, "name": "Футболка початківця", "price": 15, "level_required": 1,
             "stats": {"technique": 1, "kicks": 1, "ball_selection": 0, "speed": 0, "endurance": 1}},
            {"id": 2, "name": "Бутси Футбольний Гранд", "price": 1940, "level_required": 8,
             "stats": {"technique": 9, "kicks": 8, "ball_selection": 6, "speed": 9, "endurance": 8}},
        ],
        "luxe_items": [
            {"id": 3, "name": "Футболка Легенда Ліги [S]", "price": 3267, "level_required": 4,
             "stats": {"technique": 12, "kicks": 11, "ball_selection": 10, "speed": 12, "endurance": 11}},
        ],
        "boxes": [
            {"key": "small_box", "name_lootbox": "Маленький бокс футболіста", "min_energy": 50, "max_energy": 100,
             "min_money": 5, "max_money": 15, "min_exp": 1, "max_exp": 5, "price": 75},
            {"key": "large_box", "name_lootbox": "Преміум бокс", "min_energy": 250, "max_energy": 400,
             "min_money": 30, "max_money": 50, "min_exp": 10, "max_exp": 15, "price": 245},
        ],
        "energy": [{"amount": 100, "price_uah": 100}, {"amount": 300, "price_uah": 270}],
        "coins": [{"key": "s", "name": "S", "coins": 500, "price_uah": 100},
                   {"key": "l", "name": "L", "coins": 2000, "price_uah": 350}],
        "vip": [{"key": "m", "duration_days": 30, "price_uah": 199}],
        "change_position_price": 150, "training_key_price_uah": 49,
    },
    "/api/training": {
        "in_training": True,
        "training": {"stats": "Швидкість", "seconds_left": 1800},
        "training_keys": 2,
        "trainer": {"joined_today": False, "today_score": 0, "session_ended": False},
        "education": {"can_claim": False, "seconds_left": 7200},
        "energy": 120,
    },
    "/api/leagues": {"leagues": [{"type": "league", "name": "🏆 Вища ліга", "is_active": True,
        "day_start": 1, "day_end": 28, "match_hour": 21,
        "standings": [
            {"club_id": 1, "club_name": "London United Lions", "goal_difference": 12, "points": 24},
            {"club_id": 2, "club_name": "Madrid Rovers Wolves", "goal_difference": -3, "points": 15},
            {"club_id": 3, "club_name": "Paris Galaxy Dragons", "goal_difference": 5, "points": 19},
        ]}]},
    "/api/hall-of-fame": {
        "power": {"top": [{"user_id": 1, "name": "Андрій", "position": "ПЗ", "value": 1876}], "me": {"place": 1, "value": 1876}},
        "level": {"top": [], "me": None}, "mvp": {"top": [], "me": None}, "bombers": {"top": [], "me": None},
        "positions": {"mf": {"label": "Півзахисники", "top": [], "me": None}},
    },
    "/api/settings": {"bot_buttons_enabled": False},
    "/api/training/start": {"started": True, "stat": "speed", "minutes": 30, "energy_cost": 10,
                             "chance": 40, "ends_at": "2026-07-22T18:00:00"},
    "/api/education/claim": {"claimed": True, "exp": 3, "coins": 12, "energy": 64},
    "/api/trainer/session": {"window": {"open_at": "2026-07-22T13:00:00", "end_at": "2026-07-22T14:00:00", "is_open": True},
                              "in_session": False, "step": 0, "total_steps": 10, "score": 0,
                              "direction": None, "directions": ["↖️", "⬆️", "↗️", "⬅️", "➡️", "↙️", "⬇️", "↘️"],
                              "done": False, "stat_points": None, "stat_claimed": False},
    "/api/trainer/join": {"joined": True, "resumed": False, "step": 1, "score": 0, "direction": "⬆️"},
    "/api/trainer/answer": {"correct": True, "points": 7, "score": 21, "step": 4, "done": False,
                             "direction": "↙️", "stat_points": None, "energy": None},
    "/api/trainer/pick-stat": {"claimed": True, "stat": "speed", "points": 3},
    "/api/team": {
        "chat_url": "https://t.me/tgfootballchat",
        "club": {
            "id": 1, "name": "London United Lions", "league": "Вища ліга",
            "description": "Найкращий клуб гри", "total_power": 12401.5,
            "members_count": 10, "max_members": 11, "is_owner": False, "invite_only": False,
            "stadium_name": "Лев Арена", "chat_url": "https://t.me/tgfootballchat",
            "members": [
                {"user_id": 1, "name": "Андрій Шевчук", "full_power": 1876, "level": 7, "position": "Півзахисник", "gender": "MAN", "is_me": True},
                {"user_id": 2, "name": "Олег Кузнецов", "full_power": 1650, "level": 6, "position": "Захисник", "gender": "MAN", "is_me": False},
                {"user_id": 3, "name": "Іван Петренко", "full_power": 1432, "level": 6, "position": "Воротар", "gender": "MAN", "is_me": False},
                {"user_id": 4, "name": "Марія Коваль", "full_power": 1390, "level": 5, "position": "Нападник", "gender": "WOMAN", "is_me": False},
                {"user_id": 5, "name": "Тарас Бондар", "full_power": 1350, "level": 5, "position": "Півзахисник", "gender": "MAN", "is_me": False},
                {"user_id": 6, "name": "Сергій Мельник", "full_power": 1280, "level": 5, "position": "Захисник", "gender": "MAN", "is_me": False},
                {"user_id": 7, "name": "Олена Ткаченко", "full_power": 1170, "level": 4, "position": "Нападник", "gender": "WOMAN", "is_me": False},
                {"user_id": 8, "name": "Дмитро Савчук", "full_power": 1050, "level": 4, "position": "Півзахисник", "gender": "MAN", "is_me": False},
                {"user_id": 9, "name": "Павло Руденко", "full_power": 980, "level": 3, "position": "Захисник", "gender": "MAN", "is_me": False},
                {"user_id": 10, "name": "Юрій Козак", "full_power": 940, "level": 3, "position": "Воротар", "gender": "MAN", "is_me": False},
            ],
        },
        "infrastructure": {"points": 340, "objects": [
            {"type": "TRAINING_BASE", "label": "🏋‍♂ Тренувальна база", "level": 2, "bonus": 5, "next_cost": 500},
            {"type": "TRAINING_CENTER", "label": "📚 Навчальний центр", "level": 1, "bonus": 5, "next_cost": 250},
            {"type": "SPORTS_MEDICINE", "label": "🏥 Спортивна медицина", "level": 0, "bonus": 0, "next_cost": 100},
        ]},
    },
    "/api/team/join-list": {"clubs": [
        {"id": 5, "name": "Paris Galaxy Dragons", "league": "Ліга новачків", "members_count": 8,
         "max_members": 11, "total_power": 8200.1, "invite_only": False},
        {"id": 6, "name": "Berlin Royals Bears", "league": "Ліга новачків", "members_count": 11,
         "max_members": 11, "total_power": 9100.0, "invite_only": True},
    ]},
    "/api/team/join": {"joined": True, "club_id": 5, "club_name": "Paris Galaxy Dragons"},
    "/api/team/leave": {"left": True},
    "/api/statistics": {
        "career": {"trainings": 42, "match_registrations": 18, "goals": 9, "blitz_played": 6,
                    "blitz_semifinals": 2, "blitz_finals": 1, "blitz_wins": 1,
                    "mvp_2_plus": 3, "mvp_25_plus": 1, "mvp_3_plus": 0},
        "month": {"matches": 7, "goals": 4, "mvp_score": 5.4},
        "progress": {"level": 7, "exp": 120, "full_power": 1876.2, "money": 25740},
    },
}


# Stateful inventory stub: equip/unequip/sell mutate INV so the flow is testable.
INV = {
    "items": [
        {"id": 11, "name": "Футболка початківця", "category": "T_SHIRT", "price": 15,
         "sell_price": 5, "level_required": 1,
         "stats": {"technique": 1, "kicks": 1, "endurance": 1}},
        {"id": 12, "name": "Бутси Футбольний Гранд", "category": "BOOTS", "price": 1940,
         "sell_price": 582, "level_required": 8,
         "stats": {"technique": 9, "kicks": 8, "ball_selection": 6, "speed": 9, "endurance": 8}},
        {"id": 13, "name": "Гетри Профі", "category": "GAITERS", "price": 300,
         "sell_price": 90, "level_required": 3, "stats": {"speed": 3, "endurance": 2}},
    ],
    "equipped": {"t_shirt_id": 11, "shorts_id": None, "gaiters_id": None, "boots_id": None},
    "sell_percent": 30,
    "money": 25740,
}
_FIELD = {"T_SHIRT": "t_shirt_id", "SHORTS": "shorts_id", "GAITERS": "gaiters_id", "BOOTS": "boots_id"}


def _inventory_route(path, payload):
    if path == "/api/inventory":
        return INV
    if path == "/api/inventory/equip":
        item = next((i for i in INV["items"] if i["id"] == payload.get("item_id")), None)
        if item:
            INV["equipped"][_FIELD[item["category"]]] = item["id"]
        return {"ok": True, "item": item}
    if path == "/api/inventory/unequip":
        INV["equipped"][_FIELD.get(payload.get("category"), "t_shirt_id")] = None
        return {"ok": True}
    if path == "/api/inventory/sell":
        item = next((i for i in INV["items"] if i["id"] == payload.get("item_id")), None)
        if item:
            for f, v in INV["equipped"].items():
                if v == item["id"]:
                    INV["equipped"][f] = None
            INV["items"] = [i for i in INV["items"] if i["id"] != item["id"]]
            INV["money"] += item["sell_price"]
            return {"ok": True, "sold_for": item["sell_price"], "money": INV["money"]}
        return {"ok": False}
    return None


class H(BaseHTTPRequestHandler):
    def _send(self):
        path = self.path.split("?")[0]
        payload = {}
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            try:
                payload = json.loads(self.rfile.read(length))
            except Exception:
                payload = {}
        body = _inventory_route(path, payload)
        if body is None:
            body = F.get(path)
        self.send_response(200 if body is not None else 404)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
        self.wfile.write(json.dumps(body or {"detail": "not found"}).encode())

    do_GET = do_POST = _send

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def log_message(self, *a):
        pass


HTTPServer(("127.0.0.1", 8765), H).serve_forever()
