from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, OTP
import secrets
import requests

# API KEY کاوه نگار
KAVENEGAR_API_KEY = "476C4D54596B6744474A4A314A72746634424774556D373174337430317A392F34685054774543783759493D"


def Home(request):
    return render(request, 'home.html')


def verify(request):
    phone_number = request.GET.get('phone', '')
    return render(request, 'code.html', {'phone_number': phone_number})


@csrf_exempt
def send_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    phonenumber = request.POST.get('phonenumber')

    # اعتبارسنجی شماره
    if not phonenumber or len(phonenumber) != 11 or not phonenumber.startswith('09'):
       return render(request, "home.html", {
        "error": "شماره موبایل نامعتبر است!"
    })

    # ساخت یا دریافت کاربر
    user, _ = User.objects.get_or_create(phonenumber=phonenumber)

    # حذف OTP های قبلی
    OTP.objects.filter(user=user).delete()

    # ساخت کد چهاررقمی
    code = str(secrets.randbelow(9000) + 1000)

    # ذخیره در دیتابیس
    OTP.objects.create(user=user, code=code)

    # در حالت تست فنی، باید شماره 09 باشد
    receptor_number = phonenumber

    try:
        # ارسال پیامک
        response = requests.get(
            f"https://api.kavenegar.com/v1/{KAVENEGAR_API_KEY}/verify/lookup.json",
            params={
                "receptor": receptor_number,
                "token": code,
                "template": "verifyy"
            },
            timeout=10
        )

        result = response.json()

        if result["return"]["status"] != 200:
            print("❌ خطا در ارسال OTP:", result)
            return JsonResponse({"error": "ارسال پیامک با خطا مواجه شد."}, status=500)

        print("✅ OTP sent successfully:", code)

    except requests.RequestException as e:
        print("❌ خطای ارتباط با کاوه‌نگار:", e)
        return JsonResponse({"error": "عدم ارتباط با سرور پیامک."}, status=500)

    return redirect(f"/verify/?phone={phonenumber}")


@csrf_exempt
def verify_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    phonenumber = request.POST.get("phonenumber")
    code = request.POST.get("code")

    if not phonenumber or not code:
        return JsonResponse({"error": "Invalid data"}, status=400)

    try:
        user = User.objects.get(phonenumber=phonenumber)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    otp = OTP.objects.filter(user=user, code=code).first()

    if not otp:
        return JsonResponse({"error": "Invalid OTP"}, status=400)

    if not otp.is_valid():
        otp.delete()
        return JsonResponse({"error": "OTP expired"}, status=400)

    otp.delete()

    return JsonResponse({
        "status": "success",
        "message": "Welcome!",
        "user": {
            "phone_number": phonenumber,
            "name": f"{user.first_name} {user.last_name}".strip()
        }
    })
