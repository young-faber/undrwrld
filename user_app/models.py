from django.db import models
from django.contrib.auth.models import AbstractUser

class MyUser(AbstractUser):
    img = models.ImageField(upload_to='img_user', default='img_user/default.png')
    
