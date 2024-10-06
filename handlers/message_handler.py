# handlers/message_handler.py
import logging

from telethon import events


def register_handlers(client):
    @client.on(events.NewMessage)
    async def handle_new_message(event):
        sender = await event.get_sender()
        logging.info(
            f"Received message: {event.message.message} from {sender.username if sender.username else sender.id}.")
