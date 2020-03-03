from django.db import models
from django.contrib.auth.models import User
from hashlib import md5
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime


class Profile(models.Model):
    phone_number = models.CharField(max_length=17, null=True)
    location = models.CharField(max_length=100, null=True)
    profile_image = models.ImageField(upload_to='user_profile_image', null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # If the user does not have a profile image we provide to him an avatar from gravatar.com
    def avatar(self, size):
        digest = md5(self.user.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def __str__(self):
        return self.user.username


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipient')
    body = models.CharField(max_length=140)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'<Message {self.body}>'

    class Meta:
        permissions = [
            ("send_private_message", "Send Private Message"),
        ]
            

class LastMessageRead(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_message_read_time = models.DateTimeField()

    def __str__(self):
        return self.user.username


def new_messages(self):
    """Helper method which returns how many unread message the user has"""
    last_message_read_time = LastMessageRead.objects.filter(user=self)[0].last_message_read_time
    last_read_time = last_message_read_time or datetime(1900, 1, 1)
    return Message.objects.filter(recipient=self).filter(
        timestamp__gte=last_read_time).count()


User.add_to_class('new_messages', new_messages)