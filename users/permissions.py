from rest_framework.permissions import BasePermission
from django.core.exceptions import PermissionDenied
from user_payments.models import *
from construction.models import *


class subscription(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        try:
            payment = Payments.objects.filter(user=user).order_by('-current_date').first()
            subscription_status = payment.subscription_status if payment else "inactive"
            match subscription_status:
                case 'active'| "trial":
                    return True
                case 'inactive':
                    return False
                case _:
                    return False
        except Payments.DoesNotExist:
            return False