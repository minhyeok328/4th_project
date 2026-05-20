from django.contrib import admin
from django.urls import path
from . import views

app_name = "api"

urlpatterns = [
    path('check_favorite/<str:product_code>/', views.check_favorite, name="check_favorite"),
    path('favorite/<str:product_code>/', views.favorite, name="favorite"),
    path('send_chat/', views.send_chat, name="send_chat")
]