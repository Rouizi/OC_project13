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
    car_picture = models.ImageField()
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
    requested = models.BooleanField(default=True)
    canceled = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    # Logically we should have an 'OnetoOneField' since a deal can only be booked once at a
    # time but I want to display the deals that have been canceled or refused for example
    deal = models.ForeignKey(CreateDeal, on_delete=models.CASCADE)
    user_owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="owner")
    user_reserve = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id}'

    def cancel(self):
        """return True if a deal was booked 1 day ago and still requested but not accepted"""
        
        if (date.today() - self.reserved_on) >= timedelta(days=1) and self.accepted is False and self.requested is True:
            return True
        return False

    def is_expired(self):
        """return True if the reservation expired"""

        if (date.today() - self.check_out) >= timedelta(days=0) and self.accepted is True and self.requested is False:
            return True
        return False
