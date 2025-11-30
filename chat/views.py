from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
import logging

from .service import ask_openai
from .models import Conversation, Message

import os
from django.conf import settings


logger = logging.getLogger(__name__)

def load_prompt(invention_type: str) -> str:
    """
    یک فایل پرامپت را بر اساس نوع اختراع (process/product/hybrid) می‌خواند.
    اگر فایل پیدا نشود یا خالی باشد، خطا raise می‌کند.
    """

    # نوع‌های مجاز
    valid_types = {"process", "product", "hybrid"}
    if invention_type not in valid_types:
        # نوع اختراع اشتباه یا ناشناخته
        raise ValueError(f"Invalid invention_type: {invention_type}")

    # نام فایل بر اساس نوع اختراع
    filename = f"{invention_type}.txt"  # مثلاً process.txt

    # مسیر پوشه prompts (در کنار manage.py)
    prompts_dir = os.path.join(settings.BASE_DIR, "prompts")
    filepath = os.path.join(prompts_dir, filename)

    # اگر فایل وجود نداشت
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Prompt file not found: {filepath}")

    # خواندن محتوا
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception as e:
        # هر خطای غیرمنتظره هنگام خواندن فایل
        raise RuntimeError(f"Error reading prompt file: {str(e)}")

    if not content:
        # فایل خالی
        raise ValueError(f"Prompt file is empty: {filepath}")

    return content


class ChatAPIView(APIView):
    # Temporarily allow any user for testing - change to IsAuthenticated later
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            logger.info(f"Chat request received from user: {request.user}")
            logger.info(f"Request data: {request.data}")
            
            user_message = request.data.get("message", "").strip()
            conversation_id = request.data.get("conversation_id")

            if not user_message:
                logger.warning("Empty message received")
                return Response(
                    {"error": "پیام نباید خالی باشد."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get user - can be None for anonymous users or actual user object
            user = request.user if hasattr(request.user, 'id') and request.user.id else None
            
            logger.info(f"Processing message for user: {user}")

            # Get existing conversation or create new one
            if conversation_id:
                try:
                    if user:
                        conversation = Conversation.objects.get(
                            id=conversation_id,
                            user=user
                        )
                    else:
                        conversation = Conversation.objects.get(id=conversation_id)
                except Conversation.DoesNotExist:
                    logger.error(f"Conversation {conversation_id} not found")
                    return Response(
                        {"error": "مکالمه یافت نشد."},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # Create new conversation
                conversation = Conversation.objects.create(
                    user=user,
                    title=user_message[:50]
                )
                logger.info(f"Created new conversation: {conversation.id}")

            # Save user message to database
            user_msg = Message.objects.create(
                conversation=conversation,
                role=Message.ROLE_USER,
                content=user_message
            )
            logger.info(f"Saved user message: {user_msg.id}")

            # Build message history for context (last 10 messages)
            # Map DB roles to OpenAI roles
            role_map = {
                Message.ROLE_USER: "user",
                Message.ROLE_AI: "assistant"
            }

            # Build message history for context (last 10 messages)
            raw_history = list(
                conversation.messages.filter(
                    role__in=[Message.ROLE_USER, Message.ROLE_AI]
                )
                .order_by('created_at')
                .values_list('role', 'content')
            )[-10:]

            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            for role, content in raw_history:
                messages.append({
                    "role": role_map[role],
                    "content": content
                })

            # Get AI response
            reply = ask_openai(messages)
            logger.info(f"Got OpenAI response")

            # Save AI response to database
            ai_msg = Message.objects.create(
                conversation=conversation,
                role=Message.ROLE_AI,
                content=reply
            )
            logger.info(f"Saved AI message: {ai_msg.id}")

            # Update conversation updated_at
            conversation.save(update_fields=['updated_at'])

            logger.info(f"Message saved successfully for conversation {conversation.id}")

            return Response({
                "reply": reply,
                "message_id": user_msg.id,
                "ai_message_id": ai_msg.id,
                "conversation_id": conversation.id,
                "conversation_title": conversation.title
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Chat API Error: {str(e)}", exc_info=True)
            return Response(
                {"error": f"خطای سرور: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def options_view(request):
    return render(request, "options.html")


class NewChatAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        chat_type = request.data.get("chat_type", "")
        user = request.user if hasattr(request.user, "id") and request.user.id else None

        conversation = Conversation.objects.create(user=user, title="چت جدید")

        template_text = "نوع چت مورد نظر را انتخاب کنید."

        ai_msg = Message.objects.create(
            conversation=conversation,
            role=Message.ROLE_AI,
            content=template_text
        )

        return Response({
            "conversation_id": conversation.id,
            "template_message": template_text,
            "ai_message_id": ai_msg.id,
        }, status=200)
def chat_view(request, pk):
        conversation = get_object_or_404(Conversation, id=pk)
        return render(request, 'chatbar.html', {'conversation': conversation})