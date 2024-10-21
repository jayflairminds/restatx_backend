from django.urls import path
from user_payments.views import *

urlpatterns = [
    path('create-checkout-session/', CreateCheckoutSession.as_view(), name='create-checkout-session'),
    path('stripe-webhook/', StripeWebhook.as_view(), name='stripe-webhook'),
    path('create-payment-intent/',CreatePaymentIntent.as_view(),name='create-payment-intent'),
    path('product-list/', ProductList.as_view(), name='product-list'),
    path('prices-list/',PricesList.as_view(),name="subscription-list"),
    path('save-payment-details/',SavePaymentDetails.as_view(),name='insert-data'),
    path('create-product/', CreateDeleteProduct.as_view(), name='create_product'),
    path('delete-product/<str:product_id>', CreateDeleteProduct.as_view(), name='delete-product'),
    path('insert-subscription/', InsertDeleteRetrieveSubscription.as_view(), name='insert-subscription'),
    path('retrieve-subscription/', InsertDeleteRetrieveSubscription.as_view(),name='retrieve-subscription'),
    path('delete-subscription/<int:id>', InsertDeleteRetrieveSubscription.as_view(),name='delete-subscription')
]