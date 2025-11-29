import os
from django.conf import settings

USE_MOCK = getattr(settings, "USE_MOCK", True)
OPENAI_API_KEY = getattr(settings, "OPENAI_API_KEY", None)

def ask_openai(messages):
    """
    اگر USE_MOCK = True باشد → پاسخ تستی
    اگر USE_MOCK = False و API Key موجود باشد → پاسخ واقعی
    """

    # حالت MOCK
    if USE_MOCK or not OPENAI_API_KEY:
        return "  پاسخ تستی ."

    # حالت واقعی (OpenAI)
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message["content"]
