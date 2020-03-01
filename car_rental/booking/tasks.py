from celery import shared_task
from .models import ReservationDeal, CreateDeal
from django.db import transaction


@shared_task()
def reservation_date():
    reservations = ReservationDeal.objects.all()
    for reservation in reservations:
        if reservation.cancel():
            with transaction.atomic():
                reservation.canceled = True
                reservation.accepted = False
                reservation.requested = False
                reservation.save()
                id_deal = reservation.deal.id
                deal = CreateDeal.objects.filter(id=id_deal).update(available=True)
            
        if reservation.is_expired():
            id_deal = reservation.deal.id
            CreateDeal.objects.filter(id=id_deal).update(available=True)
