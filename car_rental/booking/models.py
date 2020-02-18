from django.db import models
from django.contrib.auth.models import User
import datetime


class CreateDeal(models.Model):
    name = models.CharField(max_length=100)
    energie = models.CharField(max_length=15)
    mileage = models.PositiveIntegerField()
    phone_number = models.CharField(max_length=17) 
    location = models.CharField(max_length=100)
    car_picture = models.ImageField(upload_to='car_picture')
    description = models.TextField()
    price = models.PositiveSmallIntegerField()
    available = models.DateField(default=datetime.date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return self.name