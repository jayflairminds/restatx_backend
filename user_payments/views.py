from rest_framework.views import APIView,View
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import stripe
from django.conf import settings
from rest_framework import status
import os
from core import *

# from user_payments.helper_functions import payment_status

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        input_json = request.data
        tier = input_json.get('tier')
        price_id = input_json.get('price_id')
        
        # Creating Stripe Checkout session
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=f'https://glasdex.com/success/',
                cancel_url='https://glasdex.com/cancel'
            )
            return Response({'sessionId': session.id,'status':'session_created'})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        
class StripeWebhook(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.WEBHOOK_SIGNING_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=400)
        except stripe.error.SignatureVerificationError as e:
            return Response({'error': str(e)}, status=400)
        event_type = event['type']
        if event_type == 'checkout.session.completed':
            session = event['data']['object']
            print('Payment succeeded!')            
        elif event_type == 'customer.subscription.trial_will_end':
            print('Subscription trial will end')
        elif event_type == 'customer.subscription.created':
            print('Subscription created %s', event.id)
        elif event_type == 'customer.subscription.updated':
            print('Subscription created %s', event.id)
        elif event_type == 'customer.subscription.deleted':
            print('Subscription canceled: %s', event.id)
        return Response({'status': 'success'}, status=200)

class CreatePaymentIntent(APIView):
    permission_classes = [IsAuthenticated]

    # Probable payload : {
    # "payment_method_id": "pm_card_visa"  // This ID is obtained from Stripe.js
    # }

    def post(self,request):
        try:
            input_json = request.data
            payment_method_id = input_json.get('payment_method_id')
        
            payment_intent = stripe.PaymentIntent.create(
                amount=1000,
                currency='usd',
                # payment_method=payment_method_id,
                payment_method='pm_card_visa',
                # confirmation_method='manual',
                confirm=True,
                automatic_payment_methods={
                    'enabled': True,
                    'allow_redirects': 'never'  # This will disable redirects
                }
            )
            return Response(payment_intent)
        except Exception as e:
            return Response({'error': str(e)}, status=400)
    
class ProductList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        response = stripe.Product.list()
        return Response(response,status=status.HTTP_200_OK)

class PricesList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        input_params = request.query_params
        limit = input_params.get('limit')
        product = input_params.get('product')
        response = stripe.Price.list(limit=limit,product=product)
        return Response(response,status=status.HTTP_200_OK)