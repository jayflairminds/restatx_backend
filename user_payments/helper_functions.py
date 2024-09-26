# from user_payments.models import *

# def payment_status(session):
#         # Retrieve customer details from the session object
#     customer_email = session.get('customer_details', {}).get('email')
#     subscription_id = session.get('subscription')  # If it's a subscription-based payment

#     # Example: Update the user or subscription model based on the session details
#     # Let's assume you have a Django model for storing subscriptions/payments

#     # Find the user by email (or however you track them)
#     user = UserSubscription.objects.get(email=customer_email)

#     # Mark the user as subscribed (or update the subscription status)
#     user.subscription_status = 'active'
#     user.stripe_subscription_id = subscription_id  # Store the Stripe subscription ID
#     user.save()

#     # You could also send a confirmation email to the user
#     send_confirmation_email(user.email)