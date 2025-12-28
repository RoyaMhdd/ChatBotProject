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
from .Services.WordExporter import  claims_to_word, description_to_word, summary_to_word
from django.http import FileResponse, Http404, JsonResponse
import json
import zipfile
from django.http import FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt

import os
import json
import zipfile
from django.http import FileResponse, Http404, HttpResponse
from django.conf import settings
from .models import Conversation




logger = logging.getLogger(__name__)

def load_prompt(invention_type: str, details: bool) -> str:
    """
    فایل پرامپت را بر اساس invention_type و details می‌خواند.

    details=False  => non_generative
    details=True   => generative
    """

    valid_types = {"process", "product", "hybrid"}
    if invention_type not in valid_types:
        raise ValueError(
            f"Invalid invention_type: {invention_type}. Must be one of {sorted(valid_types)}"
        )

    suffix = "generative" if details else "non_generative"
    filename = f"{invention_type}_{suffix}.txt"

    prompts_dir = os.path.join(settings.BASE_DIR, "prompts")
    filepath = os.path.join(prompts_dir, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Prompt file not found: {filepath} "
            f"(expected filename: {filename} in prompts dir: {prompts_dir})"
        )

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception as e:
        raise RuntimeError(f"Error reading prompt file {filepath}: {e}")

    if not content:
        raise ValueError(f"Prompt file is empty: {filepath}")

    return content


class ChatHistoryAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            user = request.user if hasattr(request.user, 'id') and request.user.id else None
            
            # Only return conversations owned by this user that have at least one user-sent message
            if user:
                conversations = (
                    Conversation.objects
                    .filter(user=user, messages__role=Message.ROLE_USER)
                    .distinct()
                    .order_by('-updated_at')
                )
            else:
                conversations = Conversation.objects.none()

            logger.info(f"Fetching chat history for user: {user}")

            conversation_list = []
            for conversation in conversations:
                
                conversation_list.append({
                    "id": conversation.id,
                    "title": conversation.title,
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
                details = conversation.details
                system_prompt = load_prompt(invention_type, details)
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

            # Try to extract a title provided by the AI (expected to be in the JSON response)
            new_title = None
            parsed = None
            try:
                parsed = json.loads(reply)
            except json.JSONDecodeError:
                parsed = None
            except Exception as e:
                parsed = None
                logger.warning(f"Error parsing AI reply JSON: {e}")

            def _safe_get(d, *path):
                cur = d
                for p in path:
                    if not isinstance(cur, dict):
                        return None
                    cur = cur.get(p)
                return cur

            if isinstance(parsed, dict):
                # Check common top-level keys
                for key in ('title', 'conversation_title', 'invention_title', 'name', 'subject'):
                    val = parsed.get(key)
                    if val and isinstance(val, str) and val.strip():
                        new_title = val.strip()
                        break

                # Check nested patent_content.invention_title
                if not new_title:
                    inv = _safe_get(parsed, 'patent_content', 'invention_title')
                    if inv and isinstance(inv, str) and inv.strip():
                        new_title = inv.strip()

                # Check abstract text
                if not new_title:
                    abs_text = _safe_get(parsed, 'patent_content', 'abstract', 'text') or _safe_get(parsed, 'abstract', 'text')
                    if abs_text and isinstance(abs_text, str) and abs_text.strip():
                        new_title = abs_text.strip().splitlines()[0][:100]

                # Check first independent claim
                if not new_title:
                    claims = _safe_get(parsed, 'patent_content', 'claims', 'independent_claims') or _safe_get(parsed, 'claims', 'independent_claims')
                    if isinstance(claims, list) and claims:
                        first_claim = claims[0]
                        if isinstance(first_claim, str) and first_claim.strip():
                            new_title = first_claim.strip()[:100]

                # As a last resort, pick the first non-empty top-level string field
                if not new_title:
                    for k, v in parsed.items():
                        if isinstance(v, str) and v.strip():
                            new_title = v.strip().splitlines()[0][:100]
                            break

            # Fallback to using the first non-empty line of the reply (covers non-JSON replies)
            if not new_title and isinstance(reply, str):
                first_line = next((line.strip() for line in reply.splitlines() if line.strip()), None)
                if first_line:
                    new_title = first_line[:100]

            # Apply the title if found (truncate to 100 chars)
            if new_title:
                conversation.title = new_title[:100]
                conversation.save(update_fields=['last_form', 'title', 'updated_at'])
                logger.info(f"Updated conversation title to: {conversation.title}")
            else:
                # No title found — just save last_form and updated_at
                conversation.title = "چت جدید"
                conversation.save(update_fields=['last_form', 'title', 'updated_at'])

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


class UpdateConversationTitleAPIView(APIView):
    """Update the title for a conversation (owner-only when conversation.user is set)"""
    permission_classes = [AllowAny]

    def post(self, request, conversation_id):
        try:
            new_title = (request.data.get("title") or "").strip()
            if new_title == "":
                return Response({"error": "title is required."}, status=status.HTTP_400_BAD_REQUEST)

            user = request.user if hasattr(request.user, 'id') and request.user.id else None

            try:
                if user:
                    conversation = Conversation.objects.get(id=conversation_id, user=user)
                else:
                    conversation = Conversation.objects.get(id=conversation_id)
            except Conversation.DoesNotExist:
                return Response({"error": "مکالمه یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

            conversation.title = new_title
            conversation.save(update_fields=['title', 'updated_at'])
            return Response({"conversation_id": conversation.id, "title": conversation.title}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Update Conversation Title Error: {str(e)}", exc_info=True)
            return Response({"error": f"خطای سرور: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def chat_view(request, pk):
        conversation = get_object_or_404(Conversation, id=pk)
        return render(request, 'chatbar.html', {'conversation': conversation})

def download_invention_zip(request, conversation_id):
    # 1. گرفتن مکالمه (بدون کرش)
    conversation = get_object_or_404(Conversation, id=conversation_id)

    # 2. آخرین پیام AI
    last_ai = conversation.messages.filter(
        role='assistant'
    ).order_by('-created_at').first()

    if not last_ai:
        return HttpResponse("پیام AI وجود ندارد", status=400)

    if not last_ai.content or not last_ai.content.strip():
        return HttpResponse("محتوای پیام AI خالی است", status=400)

    # 3. پارس JSON (اینجا مشکل اصلی شما بود)
    try:
        patent_json = safe_json_load(last_ai.content)

    except json.JSONDecodeError as e:
        # لاگ برای شما (اختیاری)
        print("JSON ERROR:", e)
        print("CONTENT:", last_ai.content[:500])

        return HttpResponse(
            "فرمت داده اختراع نامعتبر است (JSON خراب)",
            status=422
        )

    # 4. آماده‌سازی مسیرها
    base_dir = os.path.join(settings.MEDIA_ROOT, f"invention_{conversation.id}")
    os.makedirs(base_dir, exist_ok=True)

    p1 = os.path.join(base_dir, "01_خلاصه_اختراع.docx")
    p2 = os.path.join(base_dir, "02_توضیح_اختراع.docx")
    p3 = os.path.join(base_dir, "03_ادعانامه.docx")

    # 5. ساخت فایل‌های Word (هرکدام ایزوله)
    try:
        summary_to_word(patent_json, p1)
    except Exception as e:
        print("SUMMARY ERROR:", e)
        open(p1, "wb").close()

    try:
        description_to_word(patent_json, p2)
    except Exception as e:
        print("DESCRIPTION ERROR:", e)
        open(p2, "wb").close()

    try:
        claims_to_word(patent_json, p3)
    except Exception as e:
        print("CLAIMS ERROR:", e)
        open(p3, "wb").close()

    # 6. ساخت ZIP (بدون کرش)
    zip_path = os.path.join(settings.MEDIA_ROOT, f"invention_{conversation.id}.zip")
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for path in (p1, p2, p3):
                if os.path.exists(path):
                    zipf.write(path, os.path.basename(path))
    except Exception as e:
        print("ZIP ERROR:", e)
        return HttpResponse("خطا در ساخت فایل ZIP", status=500)

    # 7. ارسال فایل
    try:
        return FileResponse(
            open(zip_path, "rb"),
            as_attachment=True,
            filename=f"invention_{conversation.id}.zip"
        )
    except Exception as e:
        print("RESPONSE ERROR:", e)
        return HttpResponse("خطا در ارسال فایل", status=500)

@csrf_exempt
def set_creativity(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    creativity = data.get("creativity")
    if creativity is None:
        return JsonResponse({"error": "creativity missing"}, status=400)


    if isinstance(creativity, bool):
        details_value = creativity
    elif isinstance(creativity, str):
        if creativity.lower() in ["flexible", "true", "1"]:
            details_value = True
        elif creativity.lower() in ["limited", "false", "0"]:
            details_value = False
        else:
            return JsonResponse({"error": "Invalid creativity value"}, status=400)
    elif isinstance(creativity, int):
        details_value = bool(creativity)
    else:
        return JsonResponse({"error": "Invalid creativity type"}, status=400)

    # گرفتن آخرین conversation
    user = request.user if hasattr(request.user, "id") and request.user.id else None

    if user:
        conversation = Conversation.objects.filter(user=user).order_by("-created_at").first()
    else:
        conversation = Conversation.objects.order_by("-created_at").first()

    if not conversation:
        return JsonResponse({"error": "No active conversation"}, status=404)

    conversation.details = details_value
    conversation.save(update_fields=["details"])

    return JsonResponse({
        "success": True,
        "details": conversation.details
    })

import json

def safe_json_load(text: str) -> dict:
    if not isinstance(text, str) or not text.strip():
        return {}

    # تبدیل اعداد فارسی و عربی به انگلیسی
    trans = str.maketrans(
        "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
        "01234567890123456789"
    )
    safe_text = text.translate(trans)

    try:
        return json.loads(safe_text)
    except json.JSONDecodeError:
        # تحت هیچ شرایطی کرش نمی‌کنه
        return {}
