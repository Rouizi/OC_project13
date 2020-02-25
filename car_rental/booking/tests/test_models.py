from django.test import TestCase
from booking.models import CreateDeal, ReservationDeal


class CreateDealTest(TestCase):
    def setUp(self):
        self.deal = CreateDeal.objects.create(name='deal1')

    def test_category_name(self):
        deal = CreateDeal.objects.get(name='category1')
        print(deal)
        expected_deal_name = f'{self.deal.name}'
        print(expected_deal_name)
        self.assertAlmostEqual(expected_deal_name, str(deal))