from django.contrib import admin
from .models import chat_history

@admin.register(chat_history)
class chat_historyAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at')
