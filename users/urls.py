from django.urls import path
from . import views
urlpatterns = [

    path('', views.Home, name='home'),
    path('home/', views.Home),
    path('Home/', views.Home),
    path('sendotp/',views.send_otp,name='send_otp'),
    path('verify/',views.verify_otp,name='verify_otp'),
]
