# utils/openai_utils.py
import logging
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"), max_retries=2)


async def generate_response(
        input_text: str, context: list[dict] | None = None, model: str = "gpt-4o"
) -> str:
    if context:
        context.insert(0, {
            "role": "system",
            "content": """You are a experienced helpful assistant named puzunich_bot.
                          You restricted to use Russian language in your answer. 
                          If you are questioned in Russian, reply using the Ukrainian language.
                          If you are questioned in English, reply using English language"""
        })
        context.append({"role": "user", "content": input_text})
    else:
        context = [
            {
                "role": "system",
                "content": """You are a helpful assistant named puzunich_bot. 
                              You restricted to use Russian language in your answer. 
                              If you are questioned in Russian, reply using the Ukrainian language."""
            },
            {
                "role": "user",
                "content": input_text
            },
        ]
    logging.info(context)
    chat_completion = await client.chat.completions.create(
        model=model, messages=context
    )
    logging.info(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content
