from django.db import models
from user_app.models import MyUser

class Message(models.Model):
    text = models.TextField()
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    

