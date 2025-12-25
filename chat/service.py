
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def ask_openai(messages):
    if settings.USE_MOCK or not settings.OPENAI_API_KEY:
        logger.info("Using mock response - USE_MOCK is enabled or API key missing")
        return "پاسخ تستی - لطفاً API key را تنظیم کنید."

    try:
        from openai import OpenAI
        # تعیین Timeout روی کلاینت
        client = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=60)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=4000
        )

        reply = response.choices[0].message.content
        finish_reason = response.choices[0].finish_reason
        logger.info(f"OpenAI response successful, finish reason: {finish_reason}")
        return reply

    except ImportError:
        logger.error("OpenAI package not installed. Run: pip install openai")
        return "خطا: کتابخانه OpenAI نصب نشده است."

    except Exception as e:
        logger.error(f"OpenAI API Error: {str(e)}")
        return f"خطا در ارتباط با OpenAI: {str(e)}"

