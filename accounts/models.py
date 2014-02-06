from django.db import models
from django.contrib.auth.models import User
from userena.models import UserenaBaseProfile


class MyProfile(UserenaBaseProfile):
    user = models.OneToOneField(User, unique=True,
                                verbose_name='user', related_name='profile')


