from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLL_CHOICE=(
        ("admin","Admin"),
        ("user","User"),
                 )
    username = models.CharField(max_length=150, unique=False)
    role=models.CharField(max_length=10,choices=ROLL_CHOICE,default='user')
    email=models.EmailField(unique=True)
    phone_number=models.CharField(max_length=15,blank=True,null=True)
    
    def __str__(self):
        return self.username


class Address(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='addresses')
    full_name=models.CharField(max_length=100)
    phone_number=models.CharField(max_length=15)
    address_line_1=models.TextField()
    address_line_2=models.TextField(blank=True,null=True)
    city=models.CharField(max_length=50)
    state=models.CharField(max_length=50)
    country=models.CharField(max_length=50)
    postal_code=models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.full_name} - {self.city} "
    
    