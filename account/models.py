from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import models
	
from django.utils.translation import ugettext_lazy as _


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='user', on_delete=models.CASCADE)
    website = models.URLField(default='', blank=True)
    bio = models.TextField(default='', blank=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    city = models.CharField(max_length=100, default='', blank=True)
    country = models.CharField(max_length=100, default='', blank=True)
    organization = models.CharField(max_length=100, default='', blank=True)
    image = models.ImageField(upload_to='profile_picture', blank=True)
    
    def __str__(self):
        return self.user.username


def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        user_profile = UserProfile(user=user)
        user_profile.save()
post_save.connect(create_profile, sender=User)

# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     description = models.CharField(max_length=100, default='', blank=True)
#     city = models.CharField(max_length=100, default='')
#     website = models.URLField(default='', blank=True)
#     phone = models.PositiveIntegerField(default=0, blank=True)
#     image = models.ImageField(upload_to='media', blank=True)

#     def __str__(self):
#         return self.user.username

# def create_profile(sender, **kwargs):
#     if kwargs['created']:
#         user_profile = UserProfile.objects.create(user=kwargs['instance'])

# post_save.connect(create_profile, sender=User)
