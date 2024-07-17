from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import UserProfile
from .serializers import *
from .models import *

from .models import Loan
from .serializers import LoanSerializer


class LoanListView(generics.ListAPIView):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        profile = UserProfile.objects.get(user=user)
        match profile.role_type:
            case "lender":
                loans = Loan.objects.filter(lender_id=user)
            case "inspector":
                loans = Loan.objects.filter(inspector_id=user)
            case "borrower":
                loans = Loan.objects.filter(borrower_id=user)

        loans = loans.select_related("project","lender", "borrower","inspector")
        return loans

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        data = response.data

        # Might need to changes this if changes are made in the database structure.
        allowed_keys = {
            "loanid",
            "projectname",
            "address",
            "loandescription",
            "planned_disbursement_amount",
            "requested_disbursement_amount",
            "status",
            "loantype",
            "start_date",
            "end_date",
            "interestrate",
            "duration",
            "borrower_name",
            "lender_name",
            "inspector_name",
            "project",
        }

        filtered_data = [
            {key: value for key, value in item.items() if key in allowed_keys}
            for item in data
        ]

        return Response(filtered_data)


class LoanDisbursementScheduleDetail(generics.ListAPIView):
    serializer_class = LoanDisbursementScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user_loan_id = self.request.query_params.get("loan_id")
        if user_loan_id is not None:
            details = LoanDisbursementSchedule.objects.filter(loan_id = user_loan_id)
            return details
        else:
            return []
        
class BudgetDetail(generics.ListAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        input_json = self.request.query_params
        loan_id = input_json['loan_id']
        budget_type = input_json['budget_type']
        if loan_id is not None and budget_type is not None:
            details = Budget.objects.filter(loan_id=loan_id, type=budget_type)
            return details
        else:
            return [] 