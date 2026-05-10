from django.contrib.auth.models import AbstractUser
from django.db import models
from common.utils import get_product

def profile_route(instance, filename):
    ext = filename.split('.')[-1]
    return f"profiles/{instance.username}.{ext}"

class Account(AbstractUser):
    # username, password 이미 존재
    nickname = models.CharField(max_length=12)
    profile_picture = models.ImageField(upload_to=profile_route, blank=True, null=True)

class UserFavorite(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    product_code = models.CharField(max_length=10)

    def get_model(self):
        return get_product(self.product_code)