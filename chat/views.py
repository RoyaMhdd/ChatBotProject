from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

# -------------------------------
# سوئیچ حالت Mock یا واقعی
# -------------------------------
USE_MOCK = True  # True = فقط Mock, False = OpenAI

if not USE_MOCK:
    import openai
    import os
    from mysite.settings import OPENAI_API_KEY
    openai.api_key = OPENAI_API_KEY

# تابع Mock
def mock_chat_response(user_message):
    return f"این پاسخ شبیه‌سازی شده به: {user_message}"

# view اصلی
@csrf_exempt
def chat_api(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Method not allowed"}, status=405)

    # خواندن داده‌ها
    if request.content_type == "application/json":
        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    else:
        data = request.POST

    user_message = data.get("message")
    if not user_message:
        return JsonResponse({"error": "No message provided"}, status=400)

    # حالت Mock یا OpenAI
    if USE_MOCK:
        ai_message = mock_chat_response(user_message)
    else:
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": user_message}],
                temperature=0.2
            )
            ai_message = response.choices[0].message.content
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"reply": ai_message})

# Create your views here.
