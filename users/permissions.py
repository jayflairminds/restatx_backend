from rest_framework.permissions import BasePermission
from django.core.exceptions import PermissionDenied
from user_payments.models import *
from construction.models import *


class LoanCreationLimitExceeded(BasePermission):

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        loan_count = len(Loan.objects.filter(borrower=user.id).all())
        # permission_obj = permissions_master.objects.get(Payment.tier)
        permission_obj = 0
        if Payments.tier == permission_obj  and loan_count <= permission_obj.count:
            return True
        
