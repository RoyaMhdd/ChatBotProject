from django.shortcuts import render

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
# from django.ratelimit.decorators import ratelimit
from .models import User, OTP
import secrets
import requests
from datetime import timedelta
KAVENEGAR_API_KEY = "6D505577634A39494C78553246313258754173306D4431642B6A614C5146574C6951594568513752494A633D"
# @ratelimit(key='ip', rate='5/m', method='POST', block=True)
def ratelimit(*args, **kwargs):
    def decorator(view_func):
        return view_func
    return decorator
@csrf_exempt

def Home(request):
    return render(request, 'home.html')


def send_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    else:
        phonenumber = request.POST.get('phonenumber')
        if not phonenumber or len(phonenumber)!=11 or not phonenumber.startswith('09'):
            return JsonResponse({"error": "Invalid phone number"}, status=400)
        user,_ = User.objects.get_or_create(phonenumber=phonenumber)
        OTP.objects.filter(user=user).delete()
        code=str(secrets.randbelow(9000)+1000)
        OTP.objects.create(user=user, code=code)

        try:
            response = requests.get(
                f"https://api.kavenegar.com/v1/{KAVENEGAR_API_KEY}/verify/lookup.json",
                params={
                    'receptor': phonenumber,
                    'token': code,
                    'template': 'verify-code'
                },
                timeout=10
            )

            if response.status_code != 200:
                print("Error", response.text)
        except Exception as e:
            print("No connection", e)  #


        return JsonResponse({'status': 'ok',"message": "OTP sent successfully"})


def verify_otp(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    phonenumber=request.POST.get('phonenumber')
    code=request.POST.get('code')
    if not phonenumber or not code:
        return JsonResponse({"error": "Invalid phone number"}, status=400)
    try:
        user=User.objects.get(phonenumber=phonenumber)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    otp = OTP.objects.filter(user=user, code=code).first()
    if not otp:
        return JsonResponse({"error": "Error"}, status=400)

    if not otp.is_valid():
        otp.delete()
        return JsonResponse({"error": "expired"}, status=400)

    otp.delete()
    return JsonResponse({'status': 'successfully verified',"message": 'welcome','user':{
        "phone number": phonenumber,
        "code": code,
        "name": f"{user.first_name} {user.last_name}".strip()}



    })










# Create your views here.
