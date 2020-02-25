from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta
from django.utils import timezone


class CreateDeal(models.Model):
    name = models.CharField(max_length=100)
    fuel = models.CharField(max_length=15)
    mileage = models.PositiveIntegerField()
    phone_number = models.CharField(max_length=17) 
    location = models.CharField(max_length=100)
    car_picture = models.ImageField(upload_to='car_picture')
    description = models.TextField()
    price = models.PositiveSmallIntegerField()
    available = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return self.name

class ReservationDeal(models.Model):
    check_in = models.DateField()
    check_out = models.DateField()
    reserved_on = models.DateField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    deal = models.OneToOneField(CreateDeal, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str(self):
        return self.id

    def is_exipre(self):
        """return True if a deal was booked 3 days or more ago and not accepted"""
        if (date.today() - self.reserved_on) >= timedelta(days=3) and self.accepted == False:
            return True
        return False
