# telegram-bot.py
import asyncio
import logging
import os

from dotenv import load_dotenv
from telethon import TelegramClient

from db.aiosqlite_db_operation import init_aiosqlite_db
from handlers.bot_handler import register_bot_handlers
from handlers.message_handler import register_handlers
from utils.telegram_utils import get_ids_from_contact

# Load environment variables from .env
load_dotenv()
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# Configure logging
logging.basicConfig(level=logging.INFO)

user_client = TelegramClient("telethon", api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH)
bot_client = TelegramClient("telethon_bot", TELEGRAM_API_ID, TELEGRAM_API_HASH)


async def main():
    # Register the event handlers
    register_handlers(user_client)
    register_bot_handlers(bot_client)

    # Start user client
    await user_client.start(phone=PHONE_NUMBER)
    logging.info("Client is running...")

    # Start bot client
    await bot_client.start(bot_token=TELEGRAM_BOT_TOKEN)
    logging.info("Bot client is running...")

    # Run both clients concurrently
    await asyncio.gather(user_client.run_until_disconnected(), bot_client.run_until_disconnected())
    # await user_client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(init_aiosqlite_db())
    asyncio.run(main())
