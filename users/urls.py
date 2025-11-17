from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='home'),
    path('sendotp', views.send_otp, name='send_otp'),
    path('verify/', views.verify, name='verify_page'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('dashbord/',views.dashboard, name='dashboard'),
    path('new-chat/', views.new_chat, name='new_chat')



]
