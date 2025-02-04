# utils/openai_utils.py
import logging
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"), max_retries=2)


async def generate_response(

        input_text: str, context: list[dict] | None = None, model: str = "o3-mini-2025-01-31"
) -> str:
    """
        supported models:
            gpt-4o
            gpt-4o-mini
            o1
            o3-mini
            o1-mini
    """
    if context:
        context.insert(0, {
            "role": "system",
            "content": str("You are an experienced, helpful assistant named puzunich_bot."
                           "You understand the Russian language, but you should reply using Ukrainian, Polish, or English."
                           "You are a native speaker of Ukrainian, Polish, and English and can translate into any of these languages upon request."
                           "Try to reply using the same language as the question.")
        })
        context.append({"role": "user", "content": input_text})
    else:
        context = [
            {
                "role": "system",
                "content": str("You are an experienced, helpful assistant named puzunich_bot."
                               "You understand the Russian language, but you should reply using Ukrainian, Polish, or English."
                               "You are a native speaker of Ukrainian, Polish, and English and can translate into any of these languages upon request."
                               "Try to reply using the same language as the question.")
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
