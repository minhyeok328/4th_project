from django.contrib import admin
from django.urls import path
from . import views

app_name = "chats"

urlpatterns = [
    path('', views.chatpage, name="chatpage")
]