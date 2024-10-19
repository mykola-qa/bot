# handlers/bot_handler.py
import logging
import os

from dotenv import load_dotenv
from telethon import events

from db.mongo_db_operation import MongoDBClient
from utils.openai_utils import generate_response
from utils.telegram_utils import get_all_enabled_bot_users, split_message

user_data = {}

load_dotenv()
TELEGRAM_BOT_NAME = os.getenv("TELEGRAM_BOT_NAME")


def register_bot_handlers(client):
    @client.on(events.NewMessage(pattern="/start"))
    async def handle_start_bot_message(event):
        logging.info(
            f"Received start bot message: {event.message.message}, chat id: {event.chat_id}"
        )
        # Fetch the sender's details to check the username
        sender = await event.get_sender()
        sender_name = sender.username if sender.username else sender.id
        ids_with_enabled_bot = get_all_enabled_bot_users()
        # Send initial bot message in private chat
        if not event.is_private:
            pass
        elif not user_data.get(sender.id) and sender.id in ids_with_enabled_bot:
            await event.reply(
                f"Hello, {sender_name}! Bot is started. Ask anything. Send '/stop' to disable me.",
            )
            user_data[sender.id] = True
            logging.info(f"{sender_name} has enabled bot.")
        elif user_data.get(sender.id):
            logging.info(
                f"""Bot is already enabled. 
                /start command from {sender_name} is ignored."""
            )
            await event.reply(
                f"Hello, {sender_name}! Bot was already started. Ask anything. Send '/stop' to disable me.",
            )

    @client.on(events.NewMessage(pattern="/stop"))
    async def handle_stop_bot_message(event):
        # Print the incoming message
        logging.info(
            f"Received stop bot message: {event.message.message}, chat id: {event.chat_id}"
        )
        # Fetch the sender's details to check the username
        sender = await event.get_sender()
        ids_with_enabled_bot = get_all_enabled_bot_users()
        if not event.is_private:
            pass
        elif sender.id in ids_with_enabled_bot:
            logging.info(
                f"{sender.username if sender.username else sender.id} has disabled bot."
            )
            # Send initial bot message
            await event.reply(
                f"{sender.username if sender.username else sender.id}, bot is stopped. Bye-bye...",
            )
            db = MongoDBClient()
            db.connect()
            await db.delete_data_from_db_by_user_id(user_id=sender.id)
            user_data[sender.id] = False

    @client.on(events.NewMessage)
    async def handle_requests_to_bot(event):
        # Fetch the sender's details to check the username
        sender = await event.get_sender()
        ids_with_enabled_bot = get_all_enabled_bot_users()
        if event.raw_text.startswith("/start") or event.raw_text.startswith("/stop"):
            pass
        elif not event.is_private:
            pass
        elif user_data.get(sender.id) and sender.id in ids_with_enabled_bot:
            # Getting user context
            db = MongoDBClient()
            db.connect()
            messages = await db.get_context_by_user_id(user_id=sender.id)
            logging.info(messages)
            # Respond to the message
            response_by_ai = await generate_response(
                input_text=event.message.message, context=messages
            )
            await db.save_message(
                user_id=sender.id, message=event.message.message, assistant=False
            )
            await db.save_message(
                user_id=sender.id, message=response_by_ai, assistant=True
            )
            if len(response_by_ai) > 4096:
                responses = split_message(response_by_ai)
                logging.info(responses)
                for message in responses:
                    await event.reply(message)
            else:
                await event.reply(response_by_ai)

    @client.on(events.NewMessage)
    async def handle_personal_requests_to_bot(event):
        # Fetch the sender's details to check the username
        sender = await event.get_sender()
        ids_with_enabled_bot = get_all_enabled_bot_users()
        if TELEGRAM_BOT_NAME in event.raw_text and sender.id in ids_with_enabled_bot:
            # Getting user context
            db = MongoDBClient()
            db.connect()
            messages = await db.get_context_by_user_id(user_id=sender.id)
            logging.info(messages)
            # Respond to the message
            response_by_ai = await generate_response(
                input_text=event.message.message, context=messages
            )
            await db.save_message(
                user_id=sender.id, message=event.message.message, assistant=False
            )
            await db.save_message(
                user_id=sender.id, message=response_by_ai, assistant=True
            )
            if len(response_by_ai) > 4096:
                responses = split_message(response_by_ai)
                logging.info(responses)
                for message in responses:
                    await event.reply(message)
            else:
                await event.reply(response_by_ai)
