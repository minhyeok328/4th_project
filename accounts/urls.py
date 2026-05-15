from django.contrib import admin
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path('', views.loginpage, name="loginpage"),
    path('mypage/', views.mypage, name="mypage"),
    path('register/', views.registerpage, name="registerpage")
]