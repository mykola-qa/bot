# utils/openai_utils.py
import logging
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"), max_retries=2)

AVAILABLE_MODELS = ['gpt-4o', 'gpt-4o-mini', 'o1-mini', 'gpt-5-mini']

async def generate_response(

        input_text: str, context: list[dict] | None = None, model: str = "gpt-4o"
) -> str:
    """
        supported models:
            gpt-4o
            gpt-4o-mini
            o1
            o1-mini
            gpt-4.5-preview
            gpt-5-mini
    """
    if context:
        context.append({"role": "user", "content": input_text})
    else:
        context = [
            {
                "role": "user",
                "content": input_text
            },
        ]
    logging.info(context)
    model = "gpt-4o"
    chat_completion = await client.chat.completions.create(
        model=model, messages=context
    )
    logging.info(chat_completion.choices[0].message.content)
    return chat_completion.choices[0].message.content
