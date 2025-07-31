from django.db import models
from user_app.models import MyUser

class Victorina(models.Model):
    topic = models.CharField(max_length=255)
    num_of_que = models.IntegerField()
    author = models.ForeignKey(MyUser, default=0, on_delete=models.CASCADE)
    users = models.ManyToManyField(MyUser, related_name='victorins', through='Stata')

class Question(models.Model):
    text = models.TextField()
    victorina = models.ForeignKey(Victorina, on_delete=models.CASCADE)

class Answer(models.Model):
    correctable = models.BooleanField(default=False)
    text = models.CharField(max_length=255)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id}. {self.text}/n | {self.question.id} {self.question.text[:20]}'   
    
    def __repr__(self):
        return f'{self.id}. {self.text}'
    
class Stata(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    victorina = models.ForeignKey(Victorina, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    result = models.IntegerField()
    
    def __str__(self):
        return f'{self.id}. {self.user.username} | {self.victorina.topic} {self.result} '
