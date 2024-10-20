# utils/telegram_utils.py
import logging
from collections import deque

from telethon.sync import TelegramClient

from db.enabled_users import users


def get_all_enabled_bot_users() -> deque:
    ids = deque()
    for key, _ in users.items():
        ids.append(key)
    return ids


def split_message(message: str, max_length: int = 4096):
    # Split the message into chunks of up to max_length characters
    return [message[i: i + max_length] for i in range(0, len(message), max_length)]


async def get_ids_from_contact(client: TelegramClient, entity: str):
    # Getting information about yourself
    user = await client.get_entity(entity=entity)
    logging.info(user)
    logging.info(user.id)
    logging.info(user.username)
