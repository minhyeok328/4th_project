from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.
class Chatroom(models.Model):
    account = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chatrooms"
    )
    
    name = models.CharField(max_length=30)
    timestamp = models.DateTimeField(default=timezone.now)

    def add_chat(self, is_userchat, content):
        ind = self.chats.count()

        _ = SingleChat.objects.create(
            chatroom=self,
            index=ind,
            is_userchat=is_userchat,
            content=content
        )

        self.updated()

    def view_chats(self):
        return self.chats.order_by("index")

    def updated(self):
        self.timestamp = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.name:<30}:{self.timestamp}"

class SingleChat(models.Model):
    chatroom = models.ForeignKey(
        Chatroom,
        on_delete=models.CASCADE,
        related_name="chats"
    )
    index = models.IntegerField()
    is_userchat = models.BooleanField()
    content = models.TextField()

    def __str__(self):
        role = "user" if self.is_userchat else "agent"
        return f"{self.index:>5}\t{role}\t{self.content}"