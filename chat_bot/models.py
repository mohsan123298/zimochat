from django.db import models
from django.conf import settings

class chat_history(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.TextField()
    history=models.JSONField()    
    created_at = models.DateTimeField(auto_now_add=True)