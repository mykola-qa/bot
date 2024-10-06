# telegram-bot.py
import asyncio
import logging
import os

from dotenv import load_dotenv
from telethon import TelegramClient

from handlers.bot_handler import register_bot_handlers
from handlers.message_handler import register_handlers

# Load environment variables from .env
load_dotenv()
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID"))
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")

# Configure logging
logging.basicConfig(level=logging.INFO)

client = TelegramClient('telethon', api_id=TELEGRAM_API_ID, api_hash=TELEGRAM_API_HASH)


async def main():
    # Register the event handlers
    register_handlers(client)
    register_bot_handlers(client)
    await client.start(phone=PHONE_NUMBER)
    logging.info("Client is running...")
    await client.run_until_disconnected()


if __name__ == '__main__':
    asyncio.run(main())
