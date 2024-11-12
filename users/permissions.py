from rest_framework.permissions import BasePermission
from django.core.exceptions import PermissionDenied
from user_payments.models import *
from construction.models import *
from users.custom_exception import CustomAPIException



class subscription(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        try:
            payment = Payments.objects.filter(user=user).order_by('-current_date').first()
            subscription_status = payment.subscription_status if payment else "inactive"
            match subscription_status:
                case 'active'| "trialing":
                    return True
                case 'inactive':
                    return False
                case _:
                    return False
        except Payments.DoesNotExist:
            return False
        
class subscriptionlimit(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            raise CustomAPIException('User is not authenticated.')
        try:
            if request.method == 'POST':
                role_type = UserProfile.objects.get(user=user).role_type
                payment = Payments.objects.filter(user=user).order_by('-current_date').first()
                subscription_plan = SubscriptionPlan.objects.get(tier=payment.tier)
                
                loan_count = 0
                if role_type.lower() == 'borrower':
                    loan_count = Loan.objects.filter(borrower_id=user).count()
                elif role_type.lower() == 'lender':
                    loan_count = Loan.objects.filter(lender_id=user).count()

                if subscription_plan.loan_count > loan_count:
                    return True
                else:
                    raise CustomAPIException('Subscription plan limit exceeded.')

        except Payments.DoesNotExist:
            raise CustomAPIException('No payment information found for the user.')
        except SubscriptionPlan.DoesNotExist:
            raise CustomAPIException('No subscription plan found for the user.')
