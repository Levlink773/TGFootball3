from asyncio import Lock

import aiofiles
import json
from typing import Union
from aiogram.types import FSInputFile

JSON_FILE_PATH = "photos_info.json"
file_lock = Lock()

async def get_photo(patch_to_photo: str) -> Union[bool, FSInputFile | str]:
    async with file_lock:
        try:
            async with aiofiles.open(JSON_FILE_PATH, "r", encoding="utf-8") as file:
                raw = await file.read()
                data = json.loads(raw)
        except FileNotFoundError:
            data = []
        except json.JSONDecodeError:
            data = []

    if not isinstance(data, list):
        data = []

    for entry in data:
        if patch_to_photo in entry:
            return True, entry[patch_to_photo]

    return False, FSInputFile(patch_to_photo)


async def save_photo_id(patch_to_photo: str, photo_id: str) -> None:
    async with file_lock:
        try:
            async with aiofiles.open(JSON_FILE_PATH, "r", encoding="utf-8") as file:
                raw = await file.read()
                data = json.loads(raw)
        except FileNotFoundError:
            data = []
        except json.JSONDecodeError:
            data = []

        if not isinstance(data, list):
            data = []

        for entry in data:
            if patch_to_photo in entry:
                entry[patch_to_photo] = photo_id
                break
        else:
            data.append({patch_to_photo: photo_id})

        async with aiofiles.open(JSON_FILE_PATH, "w", encoding="utf-8") as file:
            await file.write(json.dumps(data, ensure_ascii=False, indent=4))