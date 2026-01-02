from django.urls import path
from .views import (
    options_view,
    NewChatAPIView,
    chat_view,
    ChatHistoryAPIView,
    ChatAPIView,
    ConversationMessagesAPIView,
    UpdateConversationTitleAPIView,
    download_invention_zip
)
from django.urls import path
from . import views

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

    # Update conversation title
    path('api/conversation/<int:conversation_id>/title/', UpdateConversationTitleAPIView.as_view(), name='conversation_update_title'),

    path('conversation/<int:conversation_id>/download-word/',  download_invention_zip, name='download_word'),

path("set-creativity/", views.set_creativity, name="set_creativity"),


]



