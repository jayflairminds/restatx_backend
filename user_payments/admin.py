from django.contrib import admin
from user_payments.models import *
# Register your models here.

@admin.register(SubscriptionPlan)
class SubscriptionPlan(admin.ModelAdmin):
    list_display = ('id','tier', 'loan_count','risk_metrics','created_at','updated_at')
    list_editable = ("tier","loan_count",'risk_metrics')
    search_fields = ("tier", "loan_count")

@admin.register(Payments)
class Payments(admin.ModelAdmin):
    list_display = [field.name for field in Payments._meta.fields]