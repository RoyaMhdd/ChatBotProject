from django.urls import path
from .views import options_view, NewChatAPIView, chat_view
from .views import NewChatAPIView


urlpatterns = [
    path('options/', options_view, name='options'),
    path('<int:pk>/', chat_view, name='chat_page'),
    path('new-chat/', NewChatAPIView.as_view(), name='new_chat_api'),
]




