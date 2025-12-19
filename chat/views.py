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
from .Services.WordExporter import json_to_word
from django.http import FileResponse, Http404
import json


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



class ChatHistoryAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            user = request.user if hasattr(request.user, 'id') and request.user.id else None
            
            if user:
                conversations = Conversation.objects.filter(user=user).order_by('-updated_at')
            else:
                conversations = Conversation.objects.none()

            logger.info(f"Fetching chat history for user: {user}")

            conversation_list = []
            for conversation in conversations:
                first_message = conversation.messages.filter(
                    role=Message.ROLE_USER
                ).first()
                
                preview = first_message.content[:100] if first_message else "No messages"

                conversation_list.append({
                    "id": conversation.id,
                    "title": conversation.title,
                    "preview": preview,
                    "created_at": conversation.created_at.isoformat(),
                    "updated_at": conversation.updated_at.isoformat(),
                })

            return Response({
                "conversations": conversation_list,
                "count": len(conversation_list)
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Chat History API Error: {str(e)}", exc_info=True)
            return Response(
                {"error": f"خطای سرور: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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

            # Require an existing conversation (created during options step)
            if not conversation_id:
                logger.warning("No conversation_id provided in request")
                return Response(
                    {"error": "conversation_id is required. Please create a conversation first."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                if user:
                    conversation = Conversation.objects.get(id=conversation_id, user=user)
                else:
                    conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                logger.error(f"Conversation {conversation_id} not found")
                return Response(
                    {"error": "مکالمه یافت نشد."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # If this is the first user message for this conversation, update the title
            has_user_messages = conversation.messages.filter(role=Message.ROLE_USER).exists()
            if not has_user_messages:
                # set a concise title based on the user's first message
                new_title = (user_message[:10]+"...").strip()
                if new_title:
                    conversation.title = new_title
                    conversation.save(update_fields=['title', 'updated_at'])
                    logger.info(f"Updated conversation title to: {conversation.title}")

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

            # --- بارگذاری system prompt بر اساس نوع اختراع مکالمه ---
            try:
                invention_type = conversation.invention_type  # مثلا "process" یا "product" یا "hybrid"
                system_prompt = load_prompt(invention_type)
            except FileNotFoundError as e:
                logger.error(f"Prompt file not found: {str(e)}")
                return Response(
                    {"error": "برای این نوع اختراع، فایل پرامپت روی سرور تنظیم نشده است."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except ValueError as e:
                logger.error(f"Prompt config error: {str(e)}")
                return Response(
                    {"error": "پیکربندی پرامپت برای این نوع اختراع مشکل دارد."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except Exception as e:
                logger.error(f"Unexpected prompt loading error: {str(e)}", exc_info=True)
                return Response(
                    {"error": "در بارگذاری دستورالعمل سیستم خطایی رخ داد."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Build messages for OpenAI
            messages = [
                {"role": "system", "content": system_prompt}
            ]

            # اگر قبلاً فرم نهایی برای این مکالمه ذخیره شده، آن را به‌عنوان
            # آخرین خروجی مدل (assistant) به کانتکست اضافه می‌کنیم
            if conversation.last_form:
                messages.append({
                    "role": "assistant",
                    "content": conversation.last_form
                })

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

            # فرض: کل خروجی مدل، فرم فعلی اختراع (مثلاً JSON) است
            conversation.last_form = reply

            # Update conversation last_form and updated_at
            conversation.save(update_fields=['last_form', 'updated_at'])

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
        # Read requested chat type and normalize to model choices
        raw_type = (request.data.get("chat_type") or "").strip().lower()
        user = request.user if hasattr(request.user, "id") and request.user.id else None

        # Map frontend values to model choices. Frontend may send 'both' for hybrid.
        if raw_type == "both":
            invention_type = "hybrid"
        elif raw_type in {"process", "product", "hybrid"}:
            invention_type = raw_type or "process"
        else:
            # default to 'process' when not provided or unrecognized
            invention_type = "process"

        # Create conversation with selected invention_type
        conversation = Conversation.objects.create(
            user=user,
            invention_type=invention_type,
            title="چت جدید"
        )
        template_text = "سلام، روزت بخیر !\nمن آماده‌ام تا درباره‌ی اختراعت بشنوم."

        ai_msg = Message.objects.create(
            conversation=conversation,
            role=Message.ROLE_AI,
            content=template_text
        )

        return Response({
            "conversation_id": conversation.id,
            "invention_type": invention_type,
            "template_message": template_text,
            "ai_message_id": ai_msg.id,
        }, status=status.HTTP_201_CREATED)
    
class ConversationMessagesAPIView(APIView):
    """Retrieve all previous messages for a specific conversation"""
    permission_classes = [AllowAny]

    def get(self, request, conversation_id):
        try:
            user = request.user if hasattr(request.user, 'id') and request.user.id else None
            
            # Get the conversation
            if user:
                conversation = Conversation.objects.get(id=conversation_id, user=user)
            else:
                conversation = Conversation.objects.get(id=conversation_id)
            
            logger.info(f"Fetching messages for conversation {conversation_id}")
            
            # Get all messages ordered by creation time
            messages = conversation.messages.all().order_by('created_at').values(
                'id', 'role', 'content', 'created_at'
            )
            
            return Response({
                "conversation_id": conversation.id,
                "conversation_title": conversation.title,
                "invention_type": conversation.invention_type,
                "messages": list(messages)
            }, status=status.HTTP_200_OK)
        
        except Conversation.DoesNotExist:
            logger.error(f"Conversation {conversation_id} not found")
            return Response(
                {"error": "مکالمه یافت نشد."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Conversation Messages API Error: {str(e)}", exc_info=True)
            return Response(
                {"error": f"خطای سرور: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def chat_view(request, pk):
        conversation = get_object_or_404(Conversation, id=pk)
        return render(request, 'chatbar.html', {'conversation': conversation})


def download_last_ai_word(request, conversation_id):
    try:
        # گرفتن مکالمه
        conversation = Conversation.objects.get(id=conversation_id)

        # آخرین پیام AI
        last_ai_message = conversation.messages.filter(role='assistant').order_by('-created_at').first()
        if not last_ai_message:
            raise Http404("پیام AI یافت نشد.")

        # مسیر فایل Word
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        word_filename = f"invention_{conversation.id}.docx"
        word_filepath = os.path.join(settings.MEDIA_ROOT, word_filename)

        # تبدیل JSON به Word
        json_data = json.loads(last_ai_message.content)
        json_to_word(json_data, word_filepath)

        # ارسال فایل برای دانلود
        return FileResponse(open(word_filepath, 'rb'), as_attachment=True, filename=word_filename)

    except Conversation.DoesNotExist:
        raise Http404("مکالمه یافت نشد.")
    except Exception as e:
        raise Http404(f"خطا در ساخت فایل Word: {str(e)}")
