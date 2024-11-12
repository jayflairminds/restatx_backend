from django.contrib import admin
from user_payments.models import *
# Register your models here.

@admin.register(SubscriptionPlan)
class SubscriptionPlan(admin.ModelAdmin):
    list_display = ('id','tier', 'loan_count','created_at','updated_at')
    # list_editable = ("tier","loan_count")
    search_fields = ("tier", "loan_count")
