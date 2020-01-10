from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='account', null=True)
    username = models.CharField(max_length=50,default="yanjia666",primary_key=True)
    email=models.EmailField(null=True)

class truck(models.Model):
    truck_id=models.IntegerField(primary_key=True)
    x=models.IntegerField()
    y=models.IntegerField()
    status=models.TextField()

class package(models.Model):
    package_id=models.IntegerField(primary_key=True)
    wh_id=models.IntegerField()
    w_x=models.IntegerField()
    w_y=models.IntegerField()
    d_x=models.IntegerField()
    d_y=models.IntegerField()
    truck=models.ForeignKey(truck, on_delete=models.SET_NULL, null=True)
    loaded=models.BooleanField()
    acc=models.ForeignKey(account, on_delete=models.SET_NULL, null=True)
    status=models.TextField(null=True)
    waiting=models.BooleanField(default=False)
    loading=models.BooleanField(default=False)
    delivering=models.BooleanField(default=False)
    delivered=models.BooleanField(default=False)
    waiting_t=models.TextField(null=True)
    loading_t=models.TextField(null=True)
    delivering_t=models.TextField(null=True)
    delivered_t=models.TextField(null=True)
    
