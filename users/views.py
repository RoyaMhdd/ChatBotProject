from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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

    phonenumber = request.POST.get("phonenumber")

    # اعتبارسنجی شماره موبایل
    if not phonenumber or len(phonenumber) != 11 or not phonenumber.startswith("09"):
        return render(request, "home.html", {
            "error": "شماره موبایل نامعتبر است!"
        })

    # ایجاد کاربر در صورت عدم وجود
    user, _ = User.objects.get_or_create(phonenumber=phonenumber)

    # حذف کدهای قبلی
    OTP.objects.filter(user=user).delete()

    # تولید کد تصادفی ۴ رقمی
    code = str(secrets.randbelow(9000) + 1000)

    # ذخیره در دیتابیس
    OTP.objects.create(user=user, code=code)

    # ارسال پیامک
    try:
        response = requests.get(
            f"https://api.kavenegar.com/v1/{KAVENEGAR_API_KEY}/verify/lookup.json",
            params={
                "receptor": phonenumber,
                "token": code,
                "template": "verifyy"
            },
            timeout=10
        )

        result = response.json()

        if result["return"]["status"] != 200:
            print("❌ خطا در ارسال پیامک:", result)
            return JsonResponse({"error": "ارسال پیامک با خطا مواجه شد."}, status=500)

        print("✅ OTP sent:", code)

    except requests.RequestException as e:
        print("❌ خطای اتصال:", e)
        return JsonResponse({"error": "خطا در ارتباط با سرور پیامک."}, status=500)

    # انتقال به صفحه وارد کردن کد
    return redirect(f"/verify/?phone={phonenumber}")


# ------------------  بررسی OTP  ------------------

@csrf_exempt
@csrf_exempt
def verify_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    print("📥 POST DATA:", request.POST)

    phonenumber = request.POST.get("phonenumber")
    d1 = request.POST.get("digit1")
    d2 = request.POST.get("digit2")
    d3 = request.POST.get("digit3")
    d4 = request.POST.get("digit4")

    if not (phonenumber and d1 and d2 and d3 and d4):
        return JsonResponse({"error": "Invalid data"}, status=400)

    # 🔥 تبدیل درست RTL → LTR
    code = f"{d1}{d2}{d3}{d4}"[::-1]
    print("🔥 corrected final code:", code)

    try:
        user = User.objects.get(phonenumber=phonenumber)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    otp = OTP.objects.filter(user=user).order_by('-created_at').first()
    print("📌 LAST OTP:", otp)

    if not otp:
        return JsonResponse({"error": "No OTP found"}, status=404)

    if otp.code != code:
        print("❌ WRONG CODE")
        return JsonResponse({"error": "Invalid OTP"}, status=400)

    if not otp.is_valid():
        otp.delete()
        return JsonResponse({"error": "OTP expired"}, status=400)

    otp.delete()
    return redirect("dashboard")


def dashboard(request):
    return render(request, "main-page.html")
def new_chat(request):
    return render(request, "chatbar.html")
