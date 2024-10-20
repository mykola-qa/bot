import aiosqlite


async def init_aiosqlite_db():
    async with aiosqlite.connect('bot_stats.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                user_id INTEGER PRIMARY KEY,
                interaction_count INTEGER DEFAULT 0,
                chat_gpt_requests_counter INTEGER DEFAULT 0
            )
        ''')
        await db.commit()


async def update_interaction_count(user_id, gpt_request=False):
    async with aiosqlite.connect('bot_stats.db') as db:
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
    async with aiosqlite.connect('bot_stats.db') as db:
        cursor = await db.execute('SELECT COUNT(*) FROM interactions')
        unique_users = (await cursor.fetchone())[0]

        cursor = await db.execute('SELECT SUM(interaction_count) FROM interactions')
        total_interactions = (await cursor.fetchone())[0] or 0

        cursor = await db.execute('SELECT SUM(chat_gpt_requests_counter) FROM interactions')
        total_gpt_requests = (await cursor.fetchone())[0] or 0

    return unique_users, total_interactions, total_gpt_requests


async def get_user_statistics(user_id):
    async with aiosqlite.connect('bot_stats.db') as db:
        cursor = await db.execute(
            'SELECT interaction_count, chat_gpt_requests_counter FROM interactions WHERE user_id = ?', (user_id,))
        row = await cursor.fetchone()

    if row:
        interaction_count, gpt_request_count = row
        return interaction_count, gpt_request_count
    else:
        return 0, 0
