from django.test import TestCase
from booking.forms import CreateDealForm, ReservationDealForm
from booking.models import CreateDeal
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
from PIL import Image


class IndexViewTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            username='user1', email='user1@hotmail.com', password='top_secret'
        )
        self.deal1 = CreateDeal.objects.create(
            name='deal1', mileage=9500, price=40, car_picture='car1', user=user, available=True
        )
        self.deal2 = CreateDeal.objects.create(
            name='deal2', mileage=1100, price=50, car_picture='car2', user=user, available=True
        )
        self.deal2 = CreateDeal.objects.create(
            name='deal3', mileage=1100, price=50, car_picture='car2', user=user, available=False
        )

    def test_view_returns_200(self):
        response = self.client.get('http://127.0.0.1:8000/')
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')

    def test_lists_all_deals_available(self):
        response = self.client.get(reverse('index'))
        self.assertTrue(len(response.context['all_deals']) == 2)

    def test_order_by(self):
        # Order by mileage
        response = self.client.get('http://127.0.0.1:8000/?order_by=mileage')
        # Check that the first deal has 'mileage' less than the second deal
        self.assertTrue(response.context['all_deals'][0].mileage < response.context['all_deals'][1].mileage)
        # Order by price
        response = self.client.get('http://127.0.0.1:8000/?order_by=price')
        # Check that the first deal has 'price' less than the second deal
        self.assertTrue(response.context['all_deals'][0].price < response.context['all_deals'][1].price)


class CreateDealViewTest(TestCase):
    def tearDown(self):
        self.car_picture.close()

    def setUp(self):
        self.car_picture = self._create_image()

        self.user1 = User.objects.create_user(username='user1', email='user1@hotmail.com', password='top_secret')
        self.user2 = User.objects.create_user(username='user2', email='user2@hotmail.com', password='top_secret')
    
        self.deal = CreateDeal.objects.create(
            name='deal1', fuel='essence', mileage=100,
            phone_number=7667125630, location="paris", car_picture="car1",
            description="my car", price=40, available=True, created_on="2020-02-25", user=self.user1,
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('booking:create_deal', args=(0,)))
        self.assertRedirects(response, '/users/log_in/?next=/booking/create_deal/0/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='user1', password='top_secret')
        response = self.client.get(reverse('booking:create_deal', args=(0,)))

        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'user1')
        # Check that we got a response "seccess"
        self.assertEqual(response.status_code, 200)
        # Check title is 'Create Deal'
        self.assertEqual(response.context['title'], 'Create Deal')
       
        # Check we used correct template
        self.assertTemplateUsed(response, 'booking/create_deal.html')

    def _create_image(self):
        """This function create a temporary image to test with it"""

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            image = Image.new('RGB', (200, 200), 'white')
            image.save(f, 'PNG')

        return open(f.name, mode='rb')

    def test_new_deal_is_created(self):
        nb_deals_old = CreateDeal.objects.count()  # count deals before user create one
        login = self.client.login(username='user1', password='top_secret')
        response = self.client.post(
            reverse('booking:create_deal', args=(0,)),
            {
                'Name': 'deal2',
                'Fuel': 'essence',
                'mileage': 9500,
                'phone_number': 7667125777,
                'Location': 'paris',
                'price': 40,
                'car_picture': self.car_picture,
                'Description': 'my_car',

            },
            follow=True
        )
        nb_deals_now = CreateDeal.objects.count()  # count deals after
        self.assertTrue(nb_deals_now == nb_deals_old + 1)

        # Check user is redirected to index page after he create a deal
        self.assertRedirects(response, reverse('index'))
        # Check that we got the message 'Your deal has been created.'
        message = list(response.context['messages'])
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Your deal has been created.')

    def test_deal_is_updated(self):
        nb_deals_old = CreateDeal.objects.count()  # count deals before user create one
        login = self.client.login(username='user1', password='top_secret')
        response = self.client.post(
            reverse('booking:create_deal', args=(self.deal.id,)),
            {
                'Name': 'another name deal',
                'Fuel': 'essence',
                'mileage': 100,
                'phone_number': 7667125630,
                'Location': 'paris',
                'car_picture': self.car_picture,
                'Description': 'my_car',
                'price': 40,
            },
            follow=True
        )

        nb_deals_now = CreateDeal.objects.count()  # count deals after
        # Check that the number of deal didn't increase
        self.assertTrue(nb_deals_now == nb_deals_old)
        # Check that the name of the deal has been updated
        self.assertEqual(CreateDeal.objects.filter(id=self.deal.id)[0].name, 'another name deal')

        # Check user is redirected to index page after he updated her deal
        self.assertRedirects(response, reverse('index'))
        # Check that we got the message 'Your deal has been created.'
        message = list(response.context['messages'])
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Your deal has been updated.')

    def test_user_can_not_update_deal_of_other_users(self):
        login = self.client.login(username='user2', password='top_secret')
        response = self.client.post(
            reverse('booking:create_deal', args=(self.deal.id,)),
            {
                'Name': 'deal2',
                'Fuel': 'essence',
                'mileage': 9500,
                'phone_number': 7667125777,
                'Location': 'paris',
                'price': 40,
                'car_picture': self.car_picture,
                'Description': 'my_car',

            },
            follow=True
        )
        # Check user is redirected to index page
        self.assertRedirects(response, reverse('index'))
        # Check that user got the message 'Deal not found.'
        message = list(response.context['messages'])
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Deal not found.')


class UserCarsViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@hotmail.com', password='top_secret')
        self.user2 = User.objects.create_user(username='user2', email='user2@hotmail.com', password='top_secret')
        self.deal1 = CreateDeal.objects.create(
            name='deal1', mileage=9500, price=40, car_picture='car1', user=self.user1
        )
        self.deal1 = CreateDeal.objects.create(
            name='deal2', mileage=9500, price=40, car_picture='car2', user=self.user2
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('booking:user_cars'))
        self.assertRedirects(response, '/users/log_in/?next=/booking/user_cars/')

    def test_view_returns_all_deals_of_user(self):
        login = self.client.login(username='user1', password='top_secret')
        response = self.client.get(reverse('booking:user_cars'))
        # Check that we got a response success
        self.assertEqual(response.status_code, 200)
        # Check title is 'My cars'
        self.assertEqual(response.context['title'], 'My cars')
        # Check that we used correct template
        self.assertTemplateUsed(response, 'booking/user_cars.html')
        # Check that we return to a user only her deals
        deal1 = CreateDeal.objects.filter(user=self.user1)
        self.assertEqual(response.context['user_cars'][0], deal1[0])


class UpdateDealViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@hotmail.com', password='top_secret')
        self.user2 = User.objects.create_user(username='user2', email='user2@hotmail.com', password='top_secret')

        self.deal1 = CreateDeal.objects.create(
            name='deal1', mileage=9500, price=40, car_picture="car1", user=self.user1
        )
        self.deal2 = CreateDeal.objects.create(
            name='deal2', mileage=9500, price=40, car_picture='car2', user=self.user2
        )

    def test_redirect_if_not_logged_in(self):
        id_deal = CreateDeal.objects.filter(name='deal1')[0].id
        response = self.client.get(reverse('booking:update_deal', args=(id_deal,)))
        self.assertRedirects(response, '/users/log_in/?next=/booking/update_deal/' + str(id_deal) + '/')

    def test_view_redirect_if_deal_not_found(self):
        login = self.client.login(username='user1', password='top_secret')
        # deal2 belongs to user2 so user1 can't access to it and is redirected
        id_deal = CreateDeal.objects.filter(name='deal2')[0].id
        response = self.client.get(reverse('booking:update_deal', args=(id_deal,)), follow=True)
        # Check user is redirected to index page
        self.assertRedirects(response, reverse('index'))
        # check that the user receives the message 'No deal found.'
        message = list(response.context['messages'])
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'No deal found.')

    def test_view_redirect_to_ceate_deal_view(self):
        login = self.client.login(username='user1', password='top_secret')
        id_deal = CreateDeal.objects.filter(name='deal1')[0].id
        response = self.client.get(reverse('booking:update_deal', args=(id_deal,)), follow=True)
        # Check that the user is redirected to the view 'create_deal'
        self.assertRedirects(response, reverse('booking:create_deal', args=(id_deal,)))


class DeleteDealViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@hotmail.com', password='top_secret')
        self.user2 = User.objects.create_user(username='user2', email='user2@hotmail.com', password='top_secret')
    
        self.deal = CreateDeal.objects.create(
            name='deal1', mileage=100, car_picture="car1", price=40, user=self.user1
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('booking:delete_deal', args=(self.deal.id,)))
        self.assertRedirects(
            response, '/users/log_in/?next=/booking/delete_deal/' + str(self.deal.id) + '/'
        )

    def test_view_redirect_to_confirmation_delete_view(self):
        login = self.client.login(username='user1', password='top_secret')
        response = self.client.get(reverse('booking:delete_deal', args=(self.deal.id,)), follow=True)
        # Check that the user is redirected to the view 'confirmation_delete'
        self.assertRedirects(response, reverse('booking:confirmation_delete', args=(self.deal.id,)))

    def test_user_can_not_delete_deal_of_other_users(self):
        login = self.client.login(username='user2', password='top_secret')
        # We first check that if a user try to delete a deal who does not exist, he is redirected 
        # to 'index' with message
        response = self.client.get(reverse('booking:delete_deal', args=(0,)), follow=True)
        # Check user is redirected to index page
        self.assertRedirects(response, reverse('index'))
        # check that the user receives the message 'Deal not found.'
        message = list(response.context['messages'])
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Deal not found.')

        # Now we check that 'user2' can't delete deal of 'user1'
        response = self.client.get(reverse('booking:delete_deal', args=(self.deal.id,)), follow=True)
        # Check user is redirected to index page
        self.assertRedirects(response, reverse('index'))
        # check that the user receives the message 'Deal not found.'
        message = list(response.context['messages'])
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Deal not found.')


class ConfirmationDeleteViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', email='user1@hotmail.com', password='top_secret'
        )
        self.user2 = User.objects.create_user(
            username='user2', email='user2@hotmail.com', password='top_secret'
        )
    
        self.deal = CreateDeal.objects.create(
            name='deal1', mileage=100, car_picture="car1", price=40, user=self.user1
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('booking:confirmation_delete', args=(self.deal.id,)))
        self.assertRedirects(
            response, '/users/log_in/?next=/booking/confirmation_delete/' + str(self.deal.id) + '/'
        )

    def test_user_can_not_confirm_deletion_inexisting_deal(self):
        nb_deals_before = CreateDeal.objects.count()  # number of deals before deletion
        login = self.client.login(username='user2', password='top_secret')
        # Check that if a user try to delete a deal who does not exist, he is 
        # redirected to 'index' with message
        response = self.client.get(reverse('booking:confirmation_delete', args=(0,)), follow=True)
        # Check user is redirected to index page
        self.assertRedirects(response, reverse('index'))
        # check that the user receives the message 'Deal not found.'
        message = list(response.context['messages'])
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Deal not found.')
        nb_deals_after = CreateDeal.objects.count()  # nulber of deals after a failed deletion
        # Check that the number of deals didn't change
        self.assertTrue(nb_deals_before == nb_deals_after)

    def test_user_can_not_confirm_deletion_deal__of_other_users(self):
        nb_deals_before = CreateDeal.objects.count()  # number of deals before deletion
        # Check that 'user2' can't delete deal of 'user1'
        login = self.client.login(username='user2', password='top_secret')
        response = self.client.get(
            reverse('booking:confirmation_delete', args=(self.deal.id,)), follow=True
        )
        # Check user is redirected to index page
        self.assertRedirects(response, reverse('index'))
        # check that the user receives the message 'Deal not found.'
        message = list(response.context['messages'])
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Deal not found.')
        nb_deals_after = CreateDeal.objects.count()  # nulber of deals after a failed deletion
        # Check that the number of deals didn't change
        self.assertTrue(nb_deals_before == nb_deals_after)

    def test_deal_is_deleted(self):
        nb_deals_before = CreateDeal.objects.count()  # number of deals before deletion
        # Check that 'user1' can delete here deal
        login = self.client.login(username='user1', password='top_secret')
        response = self.client.get(
            reverse('booking:confirmation_delete', args=(self.deal.id,)),
            {
                'delete': 'True'
            },
            follow=True
        )
        # Check user is redirected to index page
        self.assertRedirects(response, reverse('index'))
        # check that the user receives the message 'Your deal has been deleted.'
        message = list(response.context['messages'])
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Your deal has been deleted.')
        
        nb_deals_after = CreateDeal.objects.count()  # number of deals after a failed deletion
        # Check that the number of deals has decreased
        self.assertTrue(nb_deals_before == nb_deals_after + 1)


class DetailDealViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1', email='user1@hotmail.com', password='top_secret'
        )
        
        self.deal_available = CreateDeal.objects.create(
            name='deal1', mileage=100, car_picture="car1", price=40,
            user=self.user1, available=True
        )
        self.deal_not_available = CreateDeal.objects.create(
            name='deal1', mileage=100, car_picture="car1", price=40,
            user=self.user1, available=False
        )

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('booking:detail_deal'), {'id_deal': self.deal_available.id})
        # Check that we got a response success
        self.assertEqual(response.status_code, 200)
        # Check title is 'Detail deal'
        self.assertEqual(response.context['title'], 'Detail deal')
        # Check that we used correct template
        self.assertTemplateUsed(response, 'booking/detail_deal.html')
     
    def test_view_returns_only_available_deal(self):
        response = self.client.get(
            reverse('booking:detail_deal'),
            {
                'id_deal': self.deal_not_available.id
            },
            follow=True
        )
        # Check user is redirected to index page
        self.assertRedirects(response, reverse('index'))
        # check that the user receives the message 'Your deal has been deleted.'
        message = list(response.context['messages'])
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Deal not found, it has been deleted.')
