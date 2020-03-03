from django.test import TestCase
from users.forms import SignUpForm, ConnexionForm, EditProfileForm
from django.contrib.auth.models import User


class SignUpFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user1', email='user1@hotmail.com', password='top_secret'
        )

    def test_fields_label(self):
        form = SignUpForm()
        self.assertTrue(
            form.fields['username'].label is None or form.fields['username'].label == 'Username'
        )
        self.assertTrue(
            form.fields['email'].label is None or form.fields['email'].label == 'Email address'
        )
        self.assertTrue(
            form.fields['password1'].label is None or form.fields['password1'].label == 'Password'
        )
        self.assertTrue(
            form.fields['password2'].label is None or form.fields['password2'].label == 'Password confirmation'
        )

    def test_email_already_taken(self):
        data = {
            'username': 'test_user',
            'email': 'user1@hotmail.com',
            'password1': 'alfa_1234',
            'password2': 'alfa_1234'
        }
        form = SignUpForm(data)
        self.assertFalse(form.is_valid())
        # Check that the user got the message 'This Email has already been taken.'
        for field in form:
            for error in field.errors:
                self.assertEqual(error, 'This Email has already been taken')


class ConnexionFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user1', email='user1@hotmail.com', password='top_secret'
        )

    def test_fields_label(self):
        form = ConnexionForm()
        self.assertTrue(
            form.fields['username'].label is None or form.fields['username'].label == 'Username'
        )
        self.assertTrue(
            form.fields['password'].label is None or form.fields['password'].label == 'Password'
        )


class EditProfileFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user1', email='user1@hotmail.com', password='top_secret'
        )

    def test_fields_label(self):
        form = EditProfileForm(original_username='test_user')
        self.assertTrue(
            form.fields['username'].label is None or form.fields['username'].label == 'Username*'
        )
        self.assertTrue(
            form.fields['phone_number'].label is None or form.fields['phone_number'].label == 'Phone'
        )
        self.assertTrue(
            form.fields['location'].label is None or form.fields['location'].label == 'Location'
        )
        self.assertTrue(
            form.fields['profile_image'].label is None or form.fields['profile_image'].label == 'Image'
        )

    def test_username_already_taken(self):
        form = EditProfileForm(
            data={
                'username': 'test_user1',
            },
            original_username='user'
        )
        self.assertFalse(form.is_valid())
        # Check that the user got the message 'This username is already taken'
        for field in form:
            for error in field.errors:
                self.assertEqual(error, 'This username is already taken.')
