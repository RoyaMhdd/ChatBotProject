from django.urls import path
from . import views
from .views import ChatAPIView

urlpatterns = [

path("chat/", ChatAPIView.as_view()),
]