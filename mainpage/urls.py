from django.contrib import admin
from django.urls import path
from . import views

app_name = "mainpage"

urlpatterns = [
    path('', views.mainpage, name="mainpage")
]