from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    path('history/', views.order_history, name='order_history'),
    path('wallet/', views.wallet_view, name='wallet'),
    path('wallet/add-funds/', views.add_funds, name='add_funds'),
    path('manager/', views.manager_orders, name='manager_orders'),
    path('update-status/<int:order_id>/', views.update_status, name='update_status'),
]