from django.urls import path
from .views import *

urlpatterns = [
    path('create-checkout-session/', CreateCheckoutSession.as_view(), name='create-checkout-session'),
    path('stripe-webhook/', StripeWebhook.as_view(), name='stripe-webhook'),
    path('product-list/', ProductList.as_view(), name='product-list'),
]