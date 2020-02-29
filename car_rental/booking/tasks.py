from celery import shared_task
from .models import ReservationDeal


@shared_task()
def reservation_date():
     print('ETAPE 1111111')
     reservations = ReservationDeal.objects.all()
     print('ETAPE 2222222222')
     for reservation in reservations:
          print('ETAPE 3333333')
          if reservation.is_expired():
               print('JE VAIS SUPPRIMER LA RESERVATION .....')
               reservation.delete()
               print('RESERVATION SUPPRIMER    !!!!!')
