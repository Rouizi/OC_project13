from django.test import TestCase
from booking.models import CreateDeal, ReservationDeal
from django.contrib.auth.models import User
from django.utils import timezone
from unittest import mock
from datetime import date


class CreateDealTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            username='alfa', email='alfa@hotmail.com', password='top_secret'
        )
        self.deal = CreateDeal.objects.create(
            name='deal1', fuel='essence', mileage=100,
            phone_number=7667125630, location="paris", car_picture="",
            description="my_car", price=40, available=True, created_on="2020-02-25", user=user,

        )
  
    def test_fields_label(self):
        """Test label of all fields of the model"""

        deal = CreateDeal.objects.get(name='deal1')
        fields = [
            'name', 'fuel', 'mileage', 'phone_number',
            'location', 'car_picture', 'description',
            'price', 'available', 'created_on', 'user'
        ]
        for field in fields:
            field_label = deal._meta.get_field(f'{field}').verbose_name
            if '_' in field:
                field = ' '.join(field.split('_'))
            self.assertEquals(field_label, field)

    def test_label_max_length(self):
        """Test the value of max_length of fields"""

        deal = CreateDeal.objects.get(name='deal1')
        field_length = {
            'name': 100, 'fuel': 15, 'phone_number': 17, 'location': 100
        }
        for field, length in field_length.items():
            max_length = deal._meta.get_field(f'{field}').max_length
            self.assertEquals(max_length, length)

    def test_db_index(self):
        """Test fields that have db_index and those which have not"""

        deal = CreateDeal.objects.get(name='deal1')
        fields_index = {
            'name': False, 'fuel': False, 'mileage': True, 'phone_number': False,
            'location': True, 'car_picture': False, 'description': False,
            'price': True, 'available': False, 'created_on': False, 'user': True
        }
        for field, index in fields_index.items():
            db_index = deal._meta.get_field(f'{field}').db_index
            self.assertEquals(db_index, index)

    def test_default_value_of_fields(self):
        deal = CreateDeal.objects.get(name='deal1')
        fields_default = {
            'available': True, 'created_on': timezone.now
        }
        for field, d in fields_default.items():
            default = deal._meta.get_field(f'{field}').default
            self.assertEquals(default, d)

    def test_deal_name(self):
        deal = CreateDeal.objects.get(name='deal1')
        expected_deal_name = f'{self.deal.name}'
        self.assertEquals(expected_deal_name, str(deal))


class ReservationDealTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='alfa', email='alfa@hotmail.com', password='top_secret'
        )
        self.deal = CreateDeal.objects.create(
            name='deal1', mileage=100, price=40, user=self.user,
        )
        self.reservation = ReservationDeal.objects.create(
            check_in='2020-02-24', check_out='2020-02-28', reserved_on='2020-02-20',
            accepted=False, deal=self.deal, user=self.user
        )

    def test_fields_label(self):
        reservation = ReservationDeal.objects.get(check_in='2020-02-24')
        fields = [
            'check_in', 'check_out', 'reserved_on',
            'accepted', 'deal', 'user'
        ]
        for field in fields:
            field_label = reservation._meta.get_field(f'{field}').verbose_name
            if '_' in field:
                field = ' '.join(field.split('_'))
            self.assertEquals(field_label, field)

    def test_db_index(self):
        reservation = ReservationDeal.objects.get(check_in='2020-02-24')
        fields_index = {
            'check_in': False, 'check_out': False, 'reserved_on': False, 
            'accepted': False, 'deal': True, 'user': True
        }
        for field, index in fields_index.items():
            db_index = reservation._meta.get_field(f'{field}').db_index
            self.assertEquals(db_index, index)

    def test_default_value_of_fields(self):
        reservation = ReservationDeal.objects.get(check_in='2020-02-24')
        fields_default = {
            'reserved_on': timezone.now, 'accepted': False
        }
        for field, d in fields_default.items():
            default = reservation._meta.get_field(f'{field}').default
            self.assertEquals(default, d)

    def test_object_is_id(self):
        reservation = ReservationDeal.objects.get(check_in='2020-02-24')
        expected_object_id = f'{reservation.id}'
        self.assertEquals(expected_object_id, str(reservation))

    @mock.patch('booking.models.date')
    def test_is_expired(self, mocked_date):
        # Should return False
        mocked_date.today.return_value = date(2020, 2, 22)
        reservation = ReservationDeal.objects.get(check_in='2020-02-24')
        expired = reservation.is_expired()
        self.assertEquals(expired, False)
        # Should return True
        mocked_date.today.return_value = date(2020, 2, 27)
        reservation = ReservationDeal.objects.get(check_in='2020-02-24')
        expired = reservation.is_expired()
        self.assertEquals(expired, True)
