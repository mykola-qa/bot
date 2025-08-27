# handlers/bot_handler.py
import logging
import os

from db.aiosqlite_db_operation import update_interaction_count, get_statistics, get_user_statistics, \
    delete_data_from_db_by_user_id, get_context_by_user_id, save_message, get_user_state, set_user_state, \
    set_user_model_type, get_user_model_type
from db.enabled_users import users
from dotenv import load_dotenv
from telethon import events
from utils.openai_utils import generate_response, AVAILABLE_MODELS
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
        await update_interaction_count(sender.id)
        sender_name = sender.username if sender.username else sender.id
        ids_with_enabled_bot = get_all_enabled_bot_users()
        # Use the database for checking user state
        user_state = await get_user_state(sender.id)
        # Send initial bot message in private chat
        if not event.is_private:
            pass
        elif not user_state and sender.id in ids_with_enabled_bot:
            await event.reply(
                f"Hello, {sender_name}! Bot is started. Ask anything."
                "Send '/stop' to disable me, send '/reset' to reset context.",
            )
            await set_user_state(sender.id, True)
            logging.info(f"{sender_name} has enabled bot.")
        elif user_state:
            logging.info(
                f"Bot is already enabled, /start command from {sender_name} is ignored."
            )
            await event.reply(
                f"Hello, {sender_name}! Bot was already started. Ask anything."
                "Send '/stop' to disable me, send '/reset' to reset context.",
            )

    @client.on(events.NewMessage(pattern="/stop"))
    async def handle_stop_bot_message(event):
        # Print the incoming message
        logging.info(
            f"Received stop bot message: {event.message.message}, chat id: {event.chat_id}"
        )
        # Fetch the sender's details to check the username
        sender = await event.get_sender()
        await update_interaction_count(sender.id)
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
            await delete_data_from_db_by_user_id(user_id=sender.id)
            await set_user_state(sender.id, False)

    @client.on(events.NewMessage(pattern="/reset"))
    async def handle_reset_bot_message(event):
        logging.info(
            f"Received reset bot command: {event.message.message}, chat id: {event.chat_id}"
        )
        sender = await event.get_sender()
        await update_interaction_count(sender.id)
        ids_with_enabled_bot = get_all_enabled_bot_users()
        if not event.is_private:
            pass
        elif sender.id in ids_with_enabled_bot:
            logging.info(
                f"{sender.username if sender.username else sender.id} has reset context."
            )
            await delete_data_from_db_by_user_id(user_id=sender.id)
            await event.reply(
                f"{sender.username if sender.username else sender.id}, context is reset.",
            )

    @client.on(events.NewMessage(pattern="/model"))
    async def handle_model_bot_message(event):
        logging.info(
            f"Received model bot command: {event.message.message}, chat id: {event.chat_id}"
        )
        sender = await event.get_sender()
        await update_interaction_count(sender.id)
        ids_with_enabled_bot = get_all_enabled_bot_users()
        msg = event.raw_text
        if not event.is_private:
            pass
        elif sender.id in ids_with_enabled_bot:
            model_type = msg.split('/model')[1].strip()
            if model_type in AVAILABLE_MODELS:
                logging.info(
                    f"{sender.username if sender.username else sender.id} has set {model_type}."
                )
                await set_user_model_type(user_id=sender.id, model_type=model_type)
                await event.reply(
                    f"{sender.username if sender.username else sender.id}, {model_type} is set.",
                )
            elif model_type:
                await event.reply(
                    f"{sender.username if sender.username else sender.id}, {model_type} is not supported.",
                )
            else:
                await event.reply(
                    f"{sender.username if sender.username else sender.id}, {AVAILABLE_MODELS} are supported.\n"
                    f"Example: /model o1-mini",
                )

    @client.on(events.NewMessage)
    async def handle_requests_to_bot(event):
        sender = await event.get_sender()
        ids_with_enabled_bot = get_all_enabled_bot_users()
        user_state = await get_user_state(sender.id)
        msg = event.raw_text
        if msg.startswith("/start") or msg.startswith("/stop") or msg.startswith("/stats") or msg.startswith("/reset") or msg.startswith("/model"):
            pass
        elif not event.is_private:
            pass
        elif user_state and sender.id in ids_with_enabled_bot:
            # Getting user context
            messages = await get_context_by_user_id(user_id=sender.id)
            logging.info(messages)
            model_type = await get_user_model_type(user_id=sender.id)
            logging.info(f'Model type for user {sender.id} - {model_type}')
            # Respond to the message
            response_by_ai = await generate_response(
                input_text=event.message.message, context=messages, model=model_type
            )
            if len(response_by_ai) > 4096:
                responses = split_message(response_by_ai)
                logging.info(responses)
                for message in responses:
                    await event.reply(message)
            else:
                await event.reply(response_by_ai)
            await update_interaction_count(sender.id, gpt_request=True)
            await save_message(
                user_id=sender.id, message=event.message.message, assistant=False
            )
            await save_message(
                user_id=sender.id, message=response_by_ai, assistant=True
            )

    @client.on(events.NewMessage)
    async def handle_personal_requests_to_bot(event):
        # Fetch the sender's details to check the username
        sender = await event.get_sender()
        ids_with_enabled_bot = get_all_enabled_bot_users()
        if not event.is_private and TELEGRAM_BOT_NAME in event.raw_text and sender.id in ids_with_enabled_bot:
            # Getting user context
            messages = await get_context_by_user_id(user_id=sender.id)
            model_type = await get_user_model_type(user_id=sender.id)
            logging.info(messages)
            # Respond to the message
            response_by_ai = await generate_response(
                input_text=event.message.message, context=messages, model=model_type
            )
            if len(response_by_ai) > 4096:
                responses = split_message(response_by_ai)
                logging.info(responses)
                for message in responses:
                    await event.reply(message)
            else:
                await event.reply(response_by_ai)
            await update_interaction_count(sender.id, gpt_request=True)
            await save_message(
                user_id=sender.id, message=event.message.message, assistant=False
            )
            await save_message(
                user_id=sender.id, message=response_by_ai, assistant=True
            )

    @client.on(events.NewMessage(pattern='/stats'))
    async def stats(event):
        if event.is_private:
            # Fetch global statistics
            unique_users, total_interactions, total_gpt_requests = await get_statistics()

            # Compile the stats message
            stats_message = (
                f"Global Statistics:\n"
                f"Total interactions: {total_interactions}\n"
                f"Unique users: {unique_users}\n"
                f"Total GPT requests: {total_gpt_requests}\n\n"
                f"User-specific Statistics:\n"
            )

            sender = await event.get_sender()
            if sender.id == tuple(users.keys())[0]:
                # Fetch and append statistics for each user in enabled_chats
                for user_id, username in users.items():
                    user_interactions, user_gpt_requests = await get_user_statistics(user_id)
                    stats_message += (
                        f"{username} (ID: {user_id}):\n"
                        f"- Interactions: {user_interactions}\n"
                        f"- GPT Requests: {user_gpt_requests}\n\n"
                    )

            await event.respond(stats_message)
