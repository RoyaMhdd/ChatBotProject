from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta

from users.decorator import login_required
from .models import User, OTP
import secrets
import requests


# API KEY کاوه نگار
KAVENEGAR_API_KEY = "476C4D54596B6744474A4A314A72746634424774556D373174337430317A392F34685054774543783759493D"


# ------------------  صفحه اصلی  ------------------

def Home(request):
    return render(request, 'home.html')


# ------------------  صفحه وارد کردن OTP  ------------------

def verify(request):
    phone_number = request.GET.get('phone', '')

    response = render(request, 'code.html', {
        'phone_number': phone_number
    })

    # جلوگیری از کش شدن صفحه
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    return response


# ------------------  ارسال OTP  ------------------

@csrf_exempt
def send_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    phone_number = request.POST.get("phone_number", "")

    # normalize common formats: +98917, 0098917, 98917 -> 0917
    raw = ''.join(ch for ch in phone_number if ch.isdigit())
    if raw.startswith('98') and len(raw) == 12:
        raw = '0' + raw[2:]
    elif raw.startswith('0098'):
        raw = '0' + raw[4:]
    elif raw.startswith('9') and len(raw) == 10:
        raw = '0' + raw

    phone_number = raw

    # اعتبارسنجی شماره موبایل (local format)
    if not phone_number or len(phone_number) != 11 or not phone_number.startswith("09"):
        return render(request, "home.html", {
            "error": "شماره موبایل نامعتبر است!"
        })

    # ایجاد کاربر در صورت عدم وجود
    user, _ = User.objects.get_or_create(phone_number=phone_number)

    # حذف کدهای قبلی و ایجاد کد جدید با زمان انقضا
    OTP.objects.filter(user=user).delete()
    # code = str(secrets.randbelow(9000) + 1000)
    code ="0000"
    expires_at = timezone.now() + timedelta(minutes=5)
    OTP.objects.create(user=user, code=code, expires_at=expires_at)

    # ارسال پیامک
    # try:
    #     response = requests.get(
    #         f"https://api.kavenegar.com/v1/{KAVENEGAR_API_KEY}/verify/lookup.json",
    #         params={
    #             "receptor": phone_number,
    #             "token": code,
    #             "template": "verifyy"
    #         },
    #         timeout=10
    #     )

    #     result = response.json()

    #     if result["return"]["status"] != 200:
    #         print(" خطا در ارسال پیامک:", result)
    #         return JsonResponse({"error": "ارسال پیامک با خطا مواجه شد."}, status=500)

    #     print(" OTP sent:", code)

    # except requests.RequestException as e:
    #     print(" خطای اتصال:", e)
    #     return JsonResponse({"error": "خطا در ارتباط با سرور پیامک."}, status=500)

    # انتقال به صفحه وارد کردن کد
    return redirect(f"/verify/?phone={phone_number}")


# ------------------  بررسی OTP  ------------------

@csrf_exempt
def verify_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    print("POST DATA:", request.POST)

    phone_number = request.POST.get("phone_number")
    d1 = request.POST.get("digit1")
    d2 = request.POST.get("digit2")
    d3 = request.POST.get("digit3")
    d4 = request.POST.get("digit4")

    if not (phone_number and d1 and d2 and d3 and d4):
        return JsonResponse({"error": "Invalid data"}, status=400)

    #  تبدیل درست RTL → LTR
    code = f"{d1}{d2}{d3}{d4}"[::-1]
    print("corrected final code:", code)

    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    otp = OTP.objects.filter(user=user).order_by('-created_at').first()
    print("LAST OTP:", otp)

    if not otp:
        return JsonResponse({"error": "No OTP found"}, status=404)

    if otp.code != code:
        print("WRONG CODE")
        return JsonResponse({"error": "Invalid OTP"}, status=400)

    if not otp.is_valid():
        otp.delete()
        return JsonResponse({"error": "OTP expired"}, status=400)

    otp.delete()
    
    token = secrets.token_hex(32)
    user.token = token
    user.save()

    request.session["auth_token"] = token
    request.session.set_expiry(timedelta(days=7))

    return redirect("dashboard")


@login_required
def dashboard(request):
    return render(request, "main-page.html", {"user": request.user})

@login_required
def new_chat(request):
    return render(request, "chatbar.html")

def logout_view(request):
    if request.user:
        request.user.token = None
        request.user.save()

    request.session.flush()
    return redirect("home")
