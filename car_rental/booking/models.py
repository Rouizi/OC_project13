from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta
from django.utils import timezone


class CreateDeal(models.Model):
    name = models.CharField(max_length=100)
    fuel = models.CharField(max_length=15)
    mileage = models.PositiveIntegerField(db_index=True)
    phone_number = models.CharField(max_length=17) 
    location = models.CharField(max_length=100, db_index=True)
    car_picture = models.ImageField(upload_to='car_picture')
    description = models.TextField()
    price = models.PositiveSmallIntegerField(db_index=True)
    available = models.BooleanField(default=True)
    created_on = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ReservationDeal(models.Model):
    check_in = models.DateField()
    check_out = models.DateField()
    reserved_on = models.DateField(default=timezone.now)
    accepted = models.BooleanField(default=False)
    deal = models.OneToOneField(CreateDeal, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id}'

    def is_expired(self):
        """return True if a deal was booked 3 days or more ago and not accepted"""
        if (date.today() - self.reserved_on) >= timedelta(days=3) and self.accepted == False:
            return True
        return False
