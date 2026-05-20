from django.contrib import admin
from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path('', views.searchpage, name="searchpage"),
    path('<str:product_code>/', views.productpage, name="productpage")
]