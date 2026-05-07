from django.contrib.auth.models import AbstractUser
from django.db import models


class Account(AbstractUser):
    # username, password 이미 존재
    nickname = models.CharField(max_length=12)

class UserFavorite(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    product_code = models.CharField()