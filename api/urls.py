from django.urls import path
from .views import ProductListAPI, OrderCreateAPI

urlpatterns = [
    path('products/', ProductListAPI.as_view(), name='api-products'),
    path('orders/create/', OrderCreateAPI.as_view(), name='api-order-create'),
]