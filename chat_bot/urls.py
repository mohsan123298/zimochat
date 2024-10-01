from django.urls import path
from .views import get_response, dashboard, save_history, find_one

app_name = 'chat_bot'

urlpatterns = [
    path('dashboard', dashboard, name='dashboard'),
    path('get_response', get_response, name='get_response'),
    path('chat_history', save_history, name='chat_history'),
    path('find_one/<int:id>', find_one, name='find_one'),
]

