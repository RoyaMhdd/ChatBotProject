from django.urls import path
from .views import (
    options_view,
    NewChatAPIView,
    chat_view,
    ChatHistoryAPIView,
    ChatAPIView,
    ConversationMessagesAPIView,
    download_last_ai_word
)

urlpatterns = [
    # Options page (type selection)
    path('options/', options_view, name='options'),

    # Create a new conversation (called from options page)
    path('new-chat/', NewChatAPIView.as_view(), name='new_chat_api'),

    # Chat page (rendered template)
    path('<int:pk>/', chat_view, name='chat_page'),

    # Chat API endpoint (send/receive messages)
    path('api/chat/', ChatAPIView.as_view(), name='chat_api'),

    # Chat history (optional)
    path('api/history/', ChatHistoryAPIView.as_view(), name='chat_history'),

    # Get previous messages for a specific conversation
    path('api/messages/<int:conversation_id>/', ConversationMessagesAPIView.as_view(), name='conversation_messages'),

    path('conversation/<int:conversation_id>/download-word/', download_last_ai_word, name='download_word'),
]



