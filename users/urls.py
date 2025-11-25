from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='home'),
    path('send-otp', views.send_otp, name='send_otp'),
    path('verify/', views.verify, name='verify_page'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('new-chat/', views.new_chat, name='new_chat'),
    path("logout/", views.logout_view, name="logout")

]
