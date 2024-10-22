from django.db import models
from users.models import *

class Payments(models.Model):
    id = models.AutoField(primary_key=True)
    tier = models.CharField(max_length=20)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    currency = models.CharField(max_length=3, default='USD')
    description = models.TextField(null=True, blank=True)
    stripe_session_id = models.CharField(max_length=255, unique=True,null=True)
    transaction_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_status = models.CharField(max_length=10, default='pending')
    subscription_status = models.CharField(max_length=30,null=True)
    stripe_subscription_id = models.CharField(max_length=30,null=True, blank=True)
    account_creation_date = models.DateTimeField(null=True, blank=True)
    renew_date = models.DateTimeField(null=True, blank=True)
    current_date = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return f'Payment {self.id} for {self.user} - Status: {self.payment_status}' 


class SubscriptionPlan(models.Model):
    id = models.AutoField(primary_key=True)
    tier = models.CharField(max_length=20)
    loan_count = models.IntegerField()
    created_at = models.DateTimeField(null=True,blank=True)
    updated_at = models.DateTimeField(null=True,blank=True)
    is_active = models.BooleanField()
