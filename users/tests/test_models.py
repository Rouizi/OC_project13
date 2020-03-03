from django.test import TestCase
from django.contrib.auth.models import User
from users.models import Profile


class ProfilModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user1', email='user1@hotmail.com', password='top_secret'
        )
        self.user2 = User.objects.create_user(
            username='test_user2', email='user2@hotmail.com', password='top_secret'
        )
        self.profile = Profile.objects.create(
            phone_number=1672359756, location='paris', profile_image='image1', user=self.user
        )
        self.profile_without_image = Profile.objects.create(
            phone_number=1672359756, location='paris', user=self.user2
        )

    def test_fields_label(self):
        """Test label of all fields of the model"""

        deal = Profile.objects.get(user=self.user)
        fields = ['phone_number', 'location', 'profile_image', 'user']
        for field in fields:
            field_label = deal._meta.get_field(f'{field}').verbose_name
            if '_' in field:
                field = ' '.join(field.split('_'))
            self.assertEquals(field_label, field)

    def test_label_max_length(self):
        """Test the value of max_length of fields"""

        profile = Profile.objects.get(user=self.user)
        field_length = {
            'phone_number': 17, 'location': 100
        }
        for field, length in field_length.items():
            max_length = profile._meta.get_field(f'{field}').max_length
            self.assertEquals(max_length, length)

    def test_user_profile_name(self):
        profile = Profile.objects.get(user=self.user)
        expected_user_profile_name = f'{self.user.username}'
        self.assertEquals(expected_user_profile_name, str(profile))

    def test_avatar(self):
        self.assertEqual(
            self.profile_without_image.avatar(28),
            'https://www.gravatar.com/avatar/a58e83283ffe7a1fb46992e778502ec6?d=identicon&s=28'
        )