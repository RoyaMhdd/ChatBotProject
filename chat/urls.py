from django.urls import path
from .views import options_view, NewChatAPIView, chat_view, ChatHistoryAPIView
from .views import ChatAPIView
urlpatterns = [
    path('options/', options_view, name='options'),
    path('<int:pk>/', chat_view, name='chat_page'),
    path('new-chat/', NewChatAPIView.as_view(), name='new_chat_api'),
    path('history/', ChatHistoryAPIView.as_view(), name='chat-history'),

    # مسیر صحیح ChatAPIView
    path('chat/', ChatAPIView.as_view(), name='chat-api'),
]

