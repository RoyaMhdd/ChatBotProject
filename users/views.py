from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, OTP
import secrets
import requests

KAVENEGAR_API_KEY = "YOUR_KAVENEGAR_API_KEY"  # جایگزین با کلید واقعی

@csrf_exempt
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
    if not phonenumber or len(phonenumber) != 11 or not phonenumber.startswith('09'):
        return JsonResponse({"error": "Invalid phone number"}, status=400)

    user, _ = User.objects.get_or_create(phonenumber=phonenumber)
    OTP.objects.filter(user=user).delete()
    code = str(secrets.randbelow(9000) + 1000)
    OTP.objects.create(user=user, code=code)


    formatted_number = '+98' + phonenumber[1:]
    try:
        response = requests.get(
            f"https://api.kavenegar.com/v1/{KAVENEGAR_API_KEY}/verify/lookup.json",
            params={
                'receptor': formatted_number,
                'token': code,
                'template': 'verify-code'
            },
            timeout=10
        )
        if response.status_code != 200:
            print("Error", response.text)
    except Exception as e:
        print("No connection", e)

    
    return redirect(f'/verify/?phone={phonenumber}')

@csrf_exempt
def verify_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    phonenumber = request.POST.get('phonenumber')
    code = request.POST.get('code')

    if not phonenumber or not code:
        return JsonResponse({"error": "Invalid phone number"}, status=400)

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
        'status': 'success',
        'message': 'Welcome!',
        'user': {
            "phone_number": phonenumber,
            "name": f"{user.first_name} {user.last_name}".strip()
        }
    })
