from django.contrib.auth.models import AbstractUser
from django.db import models
from chats.models import Chatroom

def profile_route(instance, filename):
    ext = filename.split('.')[-1]
    return f"profiles/{instance.username}.{ext}"

class Account(AbstractUser):
    # username, password 이미 존재
    nickname = models.CharField(max_length=12)
    profile_picture = models.ImageField(upload_to=profile_route, blank=True, null=True)

    def add_favorite(self, product_code):
        return UserFavorite.objects.create(
            account=self,
            product_code=product_code
        )

    def remove_favorite(self, product_code):
        self.favorites.filter(product_code=product_code).delete()
    
    def add_chatroom(self, name):
        return Chatroom.objects.create(
            account=self,
            name=name
        )
    
    def view_chatrooms(self):
        return self.chatrooms.all().order_by('-timestamp')

    def remove_chatroom(self, id):
        self.chatrooms.filter(id=id).delete()
    
    def __str__(self):
        return f"{self.username:20}:{self.nickname}"

class UserFavorite(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="favorites")
    product_code = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.account.username:20}:{self.product_code}"
