from django.urls import path
from . import views

urlpatterns = [
  path('cart', views.show_cart, name='cart'),
  path('add_to_cart', views.add_to_cart, name='add_to_cart'),
  path('remove/<pk>', views.remove_item_from_cart, name='remove'),
  path('checkout', views.checkout_cart, name='checkout'),
  path('orders', views.view_orders, name='view_orders'),
  path('process_payment', views.process_payment, name='process_payment'),
  path('payment_success', views.payment_success, name='payment_success'),

]
