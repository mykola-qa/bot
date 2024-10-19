# utils/telegram_utils.py
import logging
from collections import deque

from telethon.sync import TelegramClient

from db.enabled_chats import enabled_chats


def get_all_enabled_bot_users() -> deque:
    ids = deque()
    for key, _ in enabled_chats["persons"].items():
        ids.append(key)
    return ids


def split_message(message: str, max_length: int = 4096):
    # Split the message into chunks of up to max_length characters
    return [message[i : i + max_length] for i in range(0, len(message), max_length)]


async def send_telegram_message(client, chat_id, text):
    # Your logic for sending messages via Telethon goes here
    # Use client.send_message(chat_id, text) or similar methods
    pass


async def get_photos_from_group(
    client, group_invite_link: str = "https://t.me/+BXJwXURH7VxiYjFi"
):
    # Getting information about yourself
    me = await client.get_me()

    # "me" is a user object. You can pretty-print
    # any Telegram object with the "stringify" method:
    print(me.stringify())

    # When you print something, you see a representation of it.
    # You can access all attributes of Telegram objects with
    # the dot operator. For example, to get the username:
    username = me.username
    print(username)
    print(me.phone)

    # You can print all the dialogs/conversations that you are part of:
    # async for dialog in client.iter_dialogs():
    #     print(dialog.name, 'has ID', dialog.id)

    # You can send messages to yourself...
    # await client.send_message('me', 'Hello, myself!')
    # get chat id
    channel = await client.get_entity("https://t.me/+BXJwXURH7VxiYjFi")
    print(channel)
    # ...to some chat ID
    # await client.send_message(channel, 'Testing Telethon!')
    # ...to your contacts
    # await client.send_message('+380632557207', 'Hello, friend!')
    # ...or even to any username
    # await client.send_message('@vladislava_romeiko', 'Testing Telethon!')

    # You can, of course, use markdown in your messages:
    # message = await client.send_message(
    #     'me',
    #     'This message has **bold**, `code`, __italics__ and '
    #     'a [nice website](https://example.com)!',
    #     link_preview=False
    # )

    # Sending a message returns the sent message object, which you can use
    # print(message.raw_text)

    # You can reply to messages directly if you have a message object
    # await message.reply('Cool!')

    # Or send files, songs, documents, albums...
    # await client.send_file('me', r'C:\Users\mrv\OneDrive\Pictures\Screenshots\Screenshot 2023-09-15 221114.png')

    # You can print the message history of any chat:
    counter = 3
    # async for message in client.iter_messages('me'):
    # async for message in client.iter_messages(channel):
    async for message in client.iter_messages("@vladislava_romeiko"):
        print(message)
        # await asyncio.sleep(60)
        print(message.id, message.text)

        # You can download media from messages, too!
        # The method will return the path where the file was saved.
        # if message.photo:
        if message.document:
            path = await message.download_media()
            print("File saved to", path)  # printed after download is done
            counter -= 1
        if not counter:
            break


async def get_photo_from_message(client):
    # Getting information about yourself
    me = await client.get_me()

    # "me" is a user object. You can pretty-print
    # any Telegram object with the "stringify" method:
    print(me.stringify())

    # When you print something, you see a representation of it.
    # You can access all attributes of Telegram objects with
    # the dot operator. For example, to get the username:
    username = me.username
    print(username)
    print(me.phone)

    # You can print all the dialogs/conversations that you are part of:
    # async for dialog in client.iter_dialogs():
    #     print(dialog.name, 'has ID', dialog.id)

    # You can send messages to yourself...
    # await client.send_message('me', 'Hello, myself!')
    # get chat id
    channel = await client.get_entity("https://t.me/+BXJwXURH7VxiYjFi")
    print(channel)
    # ...to some chat ID
    # await client.send_message(channel, 'Testing Telethon!')
    # ...to your contacts
    # await client.send_message('+380632557207', 'Hello, friend!')
    # ...or even to any username
    # await client.send_message('@vladislava_romeiko', 'Testing Telethon!')

    # You can, of course, use markdown in your messages:
    # message = await client.send_message(
    #     'me',
    #     'This message has **bold**, `code`, __italics__ and '
    #     'a [nice website](https://example.com)!',
    #     link_preview=False
    # )

    # Sending a message returns the sent message object, which you can use
    # print(message.raw_text)

    # You can reply to messages directly if you have a message object
    # await message.reply('Cool!')

    # Or send files, songs, documents, albums...
    # await client.send_file('me', r'C:\Users\mrv\OneDrive\Pictures\Screenshots\Screenshot 2023-09-15 221114.png')

    # You can print the message history of any chat:
    counter = 3
    # async for message in client.iter_messages('me'):
    # async for message in client.iter_messages(channel):
    async for message in client.iter_messages("@vladislava_romeiko"):
        print(message)
        # await asyncio.sleep(60)
        print(message.id, message.text)

        # You can download media from messages, too!
        # The method will return the path where the file was saved.
        # if message.photo:
        if message.document:
            path = await message.download_media()
            print("File saved to", path)  # printed after download is done
            counter -= 1
        if not counter:
            break


async def get_ids_from_contact(client: TelegramClient, entity: str):
    # Getting information about yourself
    user = await client.get_entity(entity=entity)
    logging.info(user)
    logging.info(user.id)
    logging.info(user.username)
