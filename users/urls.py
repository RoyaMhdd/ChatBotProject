from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name='home'),
    path('send-otp', views.send_otp, name='send_otp'),
    path('verify/', views.verify, name='verify_page'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    path("company-profile/", views.company_profile, name="company_profile"),
    path('user-profile/', views.user_profile, name='user_profile'),
    path('user-profile/main-page/', views.main_page, name='dashboard_main'),
    path('dashboard/main/', views.dashboard, name='dashboard_main'),
    path('new-chat/', views.new_chat, name='new_chat'),
    path("logout/", views.logout_view, name="logout")

]
