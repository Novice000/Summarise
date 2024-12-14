from pyexpat import model
from django.db import models
from django.contrib.auth import User
from datetime import datetime

# Create your models here.
class User(User):
    pass

class Chat(models.Model):
    user = models.ForeignKey(User, related_name="chatter", on_delete=models.CASCADE, required = True)
    chat = models.JSONField()
    
class Summary(models.Model):
    user = models.ForeignKey(User, related_name="summariser", on_delete=models.CASCADE, required=True)
    to_summarise = models.TextField()
    summary = models.TextField()
    
    
