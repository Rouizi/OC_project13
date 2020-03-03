from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from users.models import Profile


class SignUpViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob', email='jacob@hotmail.com', password='top_secret'
        )

    def test_signup_returns_200(self):
        response = self.client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, 200)
        # Check we used correct template
        self.assertTemplateUsed(response, 'users/signup.html')

    def test_redirect_if_user_is_authenticated(self):
        login = self.client.login(username='jacob', password='top_secret')
        response = self.client.get(reverse('users:signup'))
        self.assertRedirects(response, reverse('index'))

    def test_new_user_is_registred(self):
        # We can check that a user has been registred by trying to find it in the database but I prefer the method with count()
        nb_users_old = User.objects.count()  # count users before a request
        self.client.post(reverse('users:signup'), {
            'username': 'test',
            'email': 'test@hotmail.com',
            'password1': 'test12345',
            'password2': 'test12345'
        })
        nb_users_new = User.objects.count()  # count users after
        self.assertEqual(nb_users_new, nb_users_old + 1)  # make sure 1 user was added


class LoginViewTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='jacob', email='jacob@hotmail.com', password='top_secret'
        )

    def test_login_returns_200(self):
        response = self.client.get(reverse('users:log_in'))
        self.assertEqual(response.status_code, 200)
        # Check we used correct template
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_user(self):
        response = self.client.post(reverse('users:log_in'), {
            'username': 'jacob', 'password': 'top_secret'
        },
            follow=True
        )
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'jacob')
        # Check that the user is redirected if the connection is successful
        self.assertRedirects(response, reverse('index'))
        response = self.client.get(reverse('users:log_in'))
        # Check if the user is already logged in he will be redirected to the home page
        self.assertRedirects(response, reverse('index'))

    def test_user_redirected_to_url_contained_in_next_parameter(self):
        response = self.client.post(
            'http://127.0.0.1:8000/users/log_in/?next=/users/profile/' + self.user.username, {
            'username': 'jacob', 'password': 'top_secret'
        })
        # Check our user is redirected to the profile view
        self.assertRedirects(response, reverse('users:profile', args=(self.user.username,)))


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob', email='jacob@hotmail.com', password='top_secret'
        )

    def test_logout_user(self):
        response = self.client.get(reverse('users:log_out'), follow=True)
        # Check our user is logged out
        self.assertEqual(str(response.context['user']), 'AnonymousUser')
        # Check that the user is redirected to the log_in view if the logout is successful
        self.assertRedirects(response, reverse('users:log_in'))


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='test_user1', email='user1@hotmail.com', password='top_secret'
        )
        self.user2 = User.objects.create_user(
            username='test_user2', email='user2@hotmail.com', password='top_secret'
        )
        self.profile = Profile.objects.create(
            phone_number=1672359756, location='paris', profile_image='image1', user=self.user1
        )

    def test_profile_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('users:profile', args=(self.user1.username,)))
        # Check that the user is redirected to the log_in view
        # with a 'next' parameter if he is not logged in
        self.assertRedirects(response, '/users/log_in/?next=/users/profile/' + self.user1.username)

    def test_view_uses_correct_template(self):
        login = self.client.login(username='test_user1', password='top_secret')
        response = self.client.get(reverse('users:profile', args=(self.user1.username,)))
        # Check that we got a response 'success'
        self.assertEqual(response.status_code, 200)
        # Check we used the correct template
        self.assertTemplateUsed(response, 'users/profile.html')

    def test_user_has_profile_image(self):
        login = self.client.login(username='test_user1', password='top_secret')
        response = self.client.get(reverse('users:profile', args=(self.user1.username,)))
        self.assertTrue(response.context['user_has_profile_image'] == True)
        
        response = self.client.get(reverse('users:profile', args=(self.user2.username,)))
        self.assertTrue(response.context['user_has_profile_image'] == False)

    def test_view_returns_404(self):
        login = self.client.login(username='test_user1', password='top_secret')
        response = self.client.get(reverse('users:profile', args=('nonexistent_username',)))
        # Check that we got a page not found error
        self.assertEqual(response.status_code, 404)


class EditProfileViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='test_user1', email='user1@hotmail.com', password='top_secret'
        )
        self.user2 = User.objects.create_user(
            username='test_user2', email='user2@hotmail.com', password='top_secret'
        )
        self.profile = Profile.objects.create(
            phone_number=1672359756, location='paris', profile_image='image1', user=self.user1
        )

    def test_edit_profile_returns_200(self):
        login = self.client.login(username='test_user1', password='top_secret')
        response = self.client.get(reverse('users:edit_profile'))
        self.assertEqual(response.status_code, 200)
        # Check title is 'Edit profile'
        self.assertTrue(response.context['title'] == 'Edit profile')

    def test_edit_profile_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('users:edit_profile'))
        self.assertRedirects(response, '/users/log_in/?next=/users/edit_profile/')

    def test_profile_is_created(self):
        login = self.client.login(username='test_user2', password='top_secret')
        response = self.client.post(
            reverse('users:edit_profile'),
            {
                'username': 'another_username',
                'phone_number': 1623458565,
                'location': 'paris',
            },
            follow=True
        )
        # Check title is 'Profile'
        user2 = User.objects.filter(email='user2@hotmail.com')[0]
        self.assertTrue(response.context['title'] == 'Profile')
        # Check username is changed
        self.assertEqual(user2.username, 'another_username')
        # Check that user got the message 'Your changes have been saved.'
        message = list(response.context['messages'])
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Your changes have been saved.')
        self.assertRedirects(response, '/users/profile/' + user2.username)