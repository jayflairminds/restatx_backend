from apscheduler.schedulers.background import BackgroundScheduler
from user_payments.models import Payments
import stripe
from django.conf import settings


stripe.api_key = settings.STRIPE_SECRET_KEY

def update_subscription_status():
    users_to_update = []
    print("Payments.objects.all()",Payments.objects.all())
    for users in Payments.objects.all():
        subscription = stripe.Subscription.retrieve(users.stripe_subscription_id)
        users.subscription_status = subscription.status
        users_to_update.append(users)
    
    Payments.objects.bulk_update(users_to_update, ['subscription_status'])


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_subscription_status, 'cron', hour=0, minute=0)
    scheduler.start()