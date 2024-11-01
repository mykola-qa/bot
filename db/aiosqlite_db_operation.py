import logging

import aiosqlite


async def init_aiosqlite_db():
    async with aiosqlite.connect('sql_lite_db/bot_stats.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                user_id INTEGER PRIMARY KEY,
                interaction_count INTEGER DEFAULT 0,
                chat_gpt_requests_counter INTEGER DEFAULT 0
            )
        ''')
        await db.commit()
    async with aiosqlite.connect('sql_lite_db/bot_data.db') as db:
        await db.execute('''
              CREATE TABLE IF NOT EXISTS messages (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT NOT NULL,
                  message TEXT NOT NULL,
                  assistant BOOLEAN NOT NULL
              )
          ''')
        await db.commit()


async def update_interaction_count(user_id, gpt_request=False):
    async with aiosqlite.connect('sql_lite_db/bot_stats.db') as db:
        cursor = await db.execute(
            'SELECT interaction_count, chat_gpt_requests_counter FROM interactions WHERE user_id = ?', (user_id,))
        row = await cursor.fetchone()

        if row:
            # Update counts
            new_interaction_count = row[0] + 1
            new_gpt_count = row[1] + (1 if gpt_request else 0)
            await db.execute(
                'UPDATE interactions SET interaction_count = ?, chat_gpt_requests_counter = ? WHERE user_id = ?',
                (new_interaction_count, new_gpt_count, user_id))
        else:
            # Insert new user
            await db.execute(
                'INSERT INTO interactions (user_id, interaction_count, chat_gpt_requests_counter) VALUES (?, ?, ?)',
                (user_id, 1, 1 if gpt_request else 0))
        await db.commit()


async def get_statistics():
    async with aiosqlite.connect('sql_lite_db/bot_stats.db') as db:
        cursor = await db.execute('SELECT COUNT(*) FROM interactions')
        unique_users = (await cursor.fetchone())[0]

        cursor = await db.execute('SELECT SUM(interaction_count) FROM interactions')
        total_interactions = (await cursor.fetchone())[0] or 0

        cursor = await db.execute('SELECT SUM(chat_gpt_requests_counter) FROM interactions')
        total_gpt_requests = (await cursor.fetchone())[0] or 0

    return unique_users, total_interactions, total_gpt_requests


async def get_user_statistics(user_id):
    async with aiosqlite.connect('sql_lite_db/bot_stats.db') as db:
        cursor = await db.execute(
            'SELECT interaction_count, chat_gpt_requests_counter FROM interactions WHERE user_id = ?', (user_id,))
        row = await cursor.fetchone()

    if row:
        interaction_count, gpt_request_count = row
        return interaction_count, gpt_request_count
    else:
        return 0, 0


async def save_message(user_id: str, message: str, assistant: bool) -> None:
    async with aiosqlite.connect('sql_lite_db/bot_data.db') as db:
        await db.execute(
            'INSERT INTO messages (user_id, message, assistant) VALUES (?, ?, ?)',
            (user_id, message, assistant)
        )
        await db.commit()
    logging.info(f"Message {user_id}{message[:10]}... is saved to db.")


async def get_context_by_user_id(user_id: str) -> list:
    async with aiosqlite.connect('sql_lite_db/bot_data.db') as db:
        cursor = await db.execute(
            'SELECT message, assistant FROM messages WHERE user_id = ? ORDER BY id DESC LIMIT 30', (user_id,))
        rows = await cursor.fetchall()

    messages = []
    for row in rows:
        role = 'assistant' if row[1] else 'user'
        messages.append({"role": role, "content": row[0]})

    logging.info(f"Amount of messages - {len(messages)} was collected as context for {user_id} conversation.")
    return messages


async def delete_data_from_db_by_user_id(user_id: str):
    async with aiosqlite.connect('sql_lite_db/bot_data.db') as db:
        cursor = await db.execute(
            'DELETE FROM messages WHERE user_id = ?', (user_id,))
        deleted_count = cursor.rowcount
        await db.commit()
    logging.info(f"Deleted {deleted_count} entries.")


async def reset_bot_data_database():
    async with aiosqlite.connect('sql_lite_db/bot_data.db') as db:
        # Drop the table if it exists
        await db.execute("DROP TABLE IF EXISTS messages")

        # Recreate the table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                assistant BOOLEAN NOT NULL
            )
        ''')

        # Commit changes
        await db.commit()

    logging.info("Context database (bot_data.db) has been reset.")
