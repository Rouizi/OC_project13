from django.db import models
from django.contrib.auth.models import User
from hashlib import md5



class Profile(models.Model):
    phone_number = models.CharField(max_length=17, null=True) 
    location = models.CharField(max_length=100, null=True)
    profile_image = models.ImageField(upload_to='user_profile_image', null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # If the user does not have a profile image we provid to him an avatar from gravatar.com
    def avatar(self, size):
        digest = md5(self.user.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size) 

    def __str__(self):
        return self.user.username
