import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

USE_MOCK = getattr(settings, "USE_MOCK", True)
OPENAI_API_KEY = getattr(settings, "OPENAI_API_KEY", None)

def ask_openai(messages):
    """
    اگر USE_MOCK = True باشد → پاسخ تستی
    اگر USE_MOCK = False و API Key موجود باشد → پاسخ واقعی
    """

    # حالت MOCK
    if USE_MOCK or not OPENAI_API_KEY:
        logger.info("Using mock response - USE_MOCK is enabled or API key missing")
        return "پاسخ تستی - لطفاً API key را تنظیم کنید."

    # حالت واقعی (OpenAI)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        reply = response.choices[0].message.content
        logger.info(f"OpenAI response successful - tokens used: {response.usage.total_tokens}")
        return reply
        
    except ImportError:
        logger.error("OpenAI package not installed. Run: pip install openai")
        return "خطا: کتابخانه OpenAI نصب نشده است."
    
    except Exception as e:
        logger.error(f"OpenAI API Error: {str(e)}")
        return f"خطا در ارتباط با OpenAI: {str(e)}"
