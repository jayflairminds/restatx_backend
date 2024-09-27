from django.urls import path
from user_payments.views import *

urlpatterns = [
    path('create-checkout-session/', CreateCheckoutSession.as_view(), name='create-checkout-session'),
    path('stripe-webhook/', StripeWebhook.as_view(), name='stripe-webhook'),
    path('create-payment-intent/',CreatePaymentIntent.as_view(),name='create-payment-intent'),
    path('product-list/', ProductList.as_view(), name='product-list'),
    path('prices-list/',PricesList.as_view(),name="subscription-list")
]