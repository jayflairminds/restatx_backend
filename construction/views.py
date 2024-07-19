from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import UserProfile
from .serializers import *
from .models import *
from rest_framework.views import APIView,View
from rest_framework.response import Response
from rest_framework import status
from .models import Loan
from .serializers import LoanSerializer
import datetime
import json



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

class UpdateDisbursementStatus(APIView):
    serializer_class = LoanDisbursementScheduleSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request):
        input_param = request.data
        loan_disbursment_id = input_param.get('loan_disbursment_id')
        status_action = input_param.get('status_action')
        user = request.user
        profile = UserProfile.objects.get(user=user)

        if profile.role_type == "borrower":
            if status_action == "Request for Disbursement":
                update_status = "Pending Inspection"
                my_instance = LoanDisbursementSchedule.objects.get(pk=loan_disbursment_id)
                my_instance.date_requested = datetime.datetime.now()
                my_instance.save(update_fields=['date_requested'])
        elif profile.role_type == "inspector":
            if status_action == "Approve":
                update_status = "Pending Disbursement"
            if status_action == "Request More Information from Borrower":
                update_status = "Pending Borrower"
        elif profile.role_type == "lender":
            if status_action == "Request Information from Inspector":
                update_status = "Pending Inspection"
            if status_action == "Request Information from Borrower":
                update_status = "Pending Borrower"
            if status_action == "Approve":
                update_status = "Approved"
            if status_action == "Complete":
                update_status = "Completed"
        try:
            my_instance = LoanDisbursementSchedule.objects.get(pk=loan_disbursment_id)
            my_instance.disbursement_status = update_status
            my_instance.save(update_fields=['disbursement_status'])
            return Response(status=status.HTTP_200_OK)
        except:
            return Response({'error': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)
        

class ReturnDisbursementStatusMapping(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        user = request.user
        profile = UserProfile.objects.get(user=user)
        role_type = profile.role_type
        print(role_type)
        with open(r'construction\disbursement_status_mapping.json','r') as file:
            status_dictionary = json.load(file)
        status_dictionary
        match role_type:
            case 'borrower':
                output = status_dictionary['borrower']
                return Response(output)
            case 'inspector':
                output = status_dictionary['inspector']
                return Response(output)
            case 'lender':
                output = status_dictionary['lender']
                return Response(output)
