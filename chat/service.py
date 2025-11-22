# chat/service.py

import os
from openai import OpenAI

API_KEY = os.getenv("OPENAI_API_KEY")

def ask_openai(messages):
    """
    اگر API_KEY تنظیم نشده باشد => پاسخ تستی برمی‌گرداند (Mock)
    ا
    """
    if not API_KEY:
        return "تست"


    # client = OpenAI(api_key=API_KEY)
    # response = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=messages,
    # )
    # return response.choices[0].message["content"]
    # -----------------------------------------------------------

    return "API_KEY هنوز فعال نشده."
