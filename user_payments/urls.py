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
    path('insert-subscription/', InsertDeleteRetrieveUpdateSubscription.as_view(), name='insert-subscription'),
    path('retrieve-subscription/',InsertDeleteRetrieveUpdateSubscription.as_view(),name='retrieve-subscription'),
    path('delete-subscription/<int:id>', InsertDeleteRetrieveUpdateSubscription.as_view(),name='delete-subscription'),
    path('update-subscription/<int:id>',InsertDeleteRetrieveUpdateSubscription.as_view(),name='update-subscription'),
    path('upgrade-subscription/',UpgradeSubscriptionView.as_view(),name='upgrade-subscription')
,
    path('create-promo-code/',PromoCode.as_view(),name='create-promo-code'),
    path('delete-promo-code/<str:id>',PromoCode.as_view(),name='delete-promo-code')
]