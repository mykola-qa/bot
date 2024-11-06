import asyncio
import logging
from datetime import datetime, time, timedelta

from db.aiosqlite_db_operation import reset_bot_data_database


async def reset_database_periodically():
    while True:
        now = datetime.now()
        # Calculate the next occurrence of the target time
        target_time = time(hour=3, minute=0)  # Change to your desired reset time
        # Create a datetime for today at the target time
        today_target = datetime.combine(now.date(), target_time)
        # If the target time for today has already passed, schedule for the next day
        if now >= today_target:
            next_run = today_target + timedelta(days=1)
        else:
            next_run = today_target
        # Calculate the wait time
        wait_time = (next_run - now).total_seconds()
        logging.info(f"Database reset scheduled to run at {next_run.isoformat()}, which is in {wait_time} seconds.")

        # Wait until the scheduled time
        await asyncio.sleep(wait_time)

        # Perform the database reset
        await reset_bot_data_database()
