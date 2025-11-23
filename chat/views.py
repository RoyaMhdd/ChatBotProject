from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .service import ask_openai

SYSTEM_PROMPT = """
تو یک متخصص ثبت اختراع هستی. به زبان ساده و دقیق، راهنمایی تخصصی ثبت اختراع بده.
"""

class ChatAPIView(APIView):

    def post(self, request):
        user_message = request.data.get("message")
       

        if not user_message:
            return Response({"error": "پیام نباید خالی باشد."}, status=400)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        reply = ask_openai(messages)

        return Response({"reply": reply}, status=200)
