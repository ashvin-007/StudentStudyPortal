from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Notes(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    title=models.CharField(max_length=20)
    description=models.TextField(max_length=50)
    
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = 'Notes'
        verbose_name_plural = 'Notes'
class Homework(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    subject=models.CharField(max_length=50)
    title=models.CharField(max_length=50)
    description=models.TextField(max_length=50)
    due=models.DateTimeField()
    is_finished=models.BooleanField()
    
    def __str__(self):
       return self.title
class Todo(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    title=models.CharField(max_length=100)
    is_finished=models.BooleanField()

    def __str__(self):
        return self.title