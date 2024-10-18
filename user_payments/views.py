from rest_framework.views import APIView,View
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import stripe
from django.conf import settings
from rest_framework import status
import os
from core import *
from .serializers import *
from django.utils import timezone
import datetime
from users.permissions import subscription
# from user_payments.helper_functions import payment_status

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateCheckoutSession(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        input_json = request.data
        tier = input_json.get('tier')
        price_id = input_json.get('price_id')
        price_dict = stripe.Price.retrieve(price_id)
        product_id = price_dict.get('product')
        product_dict = stripe.Product.retrieve(product_id)
        tier = product_dict.get('name')
        #localhost = http://localhost:5173
        #localhost = https://glasdex.com
        # Creating Stripe Checkout session
        try:
            subscription_data = {}            
            # Customize for Trial tier
            if tier == 'Trial':
                subscription_data={
                    "trial_settings": {"end_behavior": {"missing_payment_method": "cancel"}},
                    "trial_period_days": 30,
                }
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                subscription_data = subscription_data,
                payment_method_collection="if_required" if tier == 'Trial' else "always",
                success_url='https://glasdex.com/success?sessionid={CHECKOUT_SESSION_ID}',
                cancel_url='https://glasdex.com/cancel?sessionid={CHECKOUT_SESSION_ID}'
            )
            return Response({'sessionId': session.id,'status':'session_created',"session":session})
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

    def post(self,request):
        try:
            input_json = request.data
            payment_method_id = input_json.get('payment_method_id')
            session_id = input_json.get('session_id')
            session = stripe.checkout.Session.retrieve(session_id)
            amount = session.amount_total
            currency = session.currency
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                payment_method=payment_method_id,
                # payment_method='pm_card_visa',
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
        product_list = stripe.Product.list()
        price_list = stripe.Price.list()
        print(request.user, list(Payments.objects.values_list('user_id',flat=True)))
        if request.user.id in list(Payments.objects.values_list('user_id',flat=True)) :
            for product in product_list:
                for price in price_list:
                    if product['id'] == price['product']:
                        product["unit_amount"] = price['unit_amount']
                        product['currency'] = price['currency']
            updated_product_list = [i for i in product_list['data'] if i.name != 'Trial']
            product_list['data'] = updated_product_list
            return Response(product_list,status=status.HTTP_200_OK)
        
        else:
            for product in product_list:
                for price in price_list:
                    if product['id'] == price['product']:
                        product["unit_amount"] = price['unit_amount']
                        product['currency'] = price['currency']
            return Response(product_list,status=status.HTTP_200_OK)

class PricesList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        input_params = request.query_params
        limit = input_params.get('limit')
        product = input_params.get('product')
        response = stripe.Price.list(limit=limit,product=product)
        return Response(response,status=status.HTTP_200_OK) 
    
class SavePaymentDetails(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self,request):

        data = request.data
        data["stripe_session_id"] = data.get('session_id')
        
        try:
            # Retrieve the checkout session using the session ID
            stripe_session = stripe.checkout.Session.retrieve(data['stripe_session_id']) 

            # Retrieve the subscription ID from the checkout session
            subscription_id = stripe_session.get('subscription') 

             # Now retrieve the subscription details
            subscription = stripe.Subscription.retrieve(subscription_id)

            # Retrieve the product details to get the tier (product name)
            product_id = subscription.plan.product
            product = stripe.Product.retrieve(product_id) 
            # Extract the tier name (product name)
            tier = product.name 

            # Prepare the data to store in the database
            payment_data = {
                'stripe_session_id': data['stripe_session_id'],
                'stripe_subscription_id': subscription.id,  # Subscription ID
                'subscription_status': subscription.status,  # Status (active, canceled, etc.)
                'tier': tier,
                'account_creation_date': datetime.datetime.fromtimestamp(subscription.created),  # Account creation date (timestamp)
                'renew_date': datetime.datetime.fromtimestamp(subscription.current_period_end),  # Renewal date (timestamp)
                'transaction_fee': subscription.application_fee_percent if subscription.application_fee_percent else 0,  # Transaction fee (if applicable)
                'description': subscription.description if subscription.description else '',  # Subscription description
                'currency': stripe_session.currency,  # Currency
                'amount': stripe_session.amount_total,  # Total amount
                'payment_status': stripe_session.payment_status,  # Payment status,
                'user': request.user.id,
                'current_date':timezone.now()
            }
  
            serializer = PaymentSerializer(data=payment_data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"Payment data saved successfully","Payment":serializer.data},status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except stripe.error.StripeError as e:
             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)