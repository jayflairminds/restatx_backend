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
from document_management.models import *
from .serializers import *
import datetime
import json
import os
from django.db.models import Max,Sum
from django.utils import timezone
from alerts.views import create_notification
from construction.helper_functions import disbursement_schedule 
import pandas as pd

class LoanListView(generics.ListAPIView):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        profile = UserProfile.objects.get(user=user)
        match profile.role_type:
            case "lender":
                loans = Loan.objects.filter(lender_id=user).order_by('-loanid')
            case "inspector":
                loans = Loan.objects.filter(inspector_id=user).order_by('-loanid')
            case "borrower":
                loans = Loan.objects.filter(borrower_id=user).order_by('-loanid')

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
            "amount",
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
            details = LoanDisbursementSchedule.objects.filter(loan_id = user_loan_id).order_by('draw_request')
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

    def post(self, request):
        input_param = request.data
        loan_disbursment_id = input_param.get('loan_disbursment_id')
        status_action = input_param.get('status_action')
        user = request.user
        profile = UserProfile.objects.get(user=user)

        if profile.role_type == "borrower":
            if status_action == "Request For Disbursement":
                update_status = "Pending Inspection"
                my_instance = LoanDisbursementSchedule.objects.get(pk=loan_disbursment_id)
                my_instance.date_requested = timezone.now()
                my_instance.requested_disbursement_amount = LoanDisbursementSchedule.objects.get(pk=loan_disbursment_id).planned_disbursement_amount 
                my_instance.save(update_fields=['date_requested','requested_disbursement_amount'])
        elif profile.role_type == "inspector":
            if status_action == "Approve":
                update_status = "Pending Disbursement"
            if status_action == "Request More Information From Borrower":
                update_status = "Pending Borrower"
        elif profile.role_type == "lender":
            if status_action == "Request Information From Inspector":
                update_status = "Pending Inspection"
            if status_action == "Request Information From Borrower":
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
        

class ReturnStatusMapping(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        input_params = request.query_params
        user = request.user
        profile = UserProfile.objects.get(user=user)
        role_type = profile.role_type
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(BASE_DIR, 'construction', 'status_mapping.json')
        with open(file_path,'r') as file:
            status_dictionary = json.load(file)
        status_dictionary = status_dictionary[input_params['application_status']]
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

class DashboardGraph(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        input_json = request.query_params
        loan_id = input_json.get('loan_id')
        graph_name = input_json.get('graph_name')

        match graph_name:
            case 'contingency_status_graph':
                queryset = ContingencyStatus.objects.filter(loan_id =loan_id).order_by('review_months')
                serializer = ContingencyStatusSerializer(queryset, many=True)
            case 'schedule_status_graph':
                queryset = ScheduleStatus.objects.filter(loan_id =loan_id).order_by('review_months')
                serializer = ScheduleStatusSerializer(queryset, many=True)
            case 'disbursement_schedule_graph':
                print(disbursement_schedule(loan_id))
                queryset = DisbursementSchedule.objects.filter(loan_id =loan_id).order_by('review_months')
                serializer = DisbursementScheduleSerializer(queryset, many=True)
                return Response(disbursement_schedule(loan_id))
            case 'construction_status_graph':
                queryset = ConstructionStatus.objects.filter(loan_id =loan_id).order_by('review_months')
                serializer = ConstructionStatusSerializer(queryset, many=True)
            case 'construction_expenditure_graph':
                max_review_month = ConstructionStatus.objects.filter(loan_id=loan_id).aggregate(Max('review_months'))['review_months__max']
                queryset = ConstructionStatus.objects.filter(loan_id=loan_id,review_months=max_review_month) 
                serializer = ConstructionStatusSerializer(queryset, many=True)
        return Response(serializer.data)
    
class Budget(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        data = request.data
        
        data['loan'] = data['loan_id'] 
        serializer = BudgetMasterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request,id):
        try:
            budget = BudgetMaster.objects.get(pk=id)
        except BudgetMaster.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        input_json = request.data
        if 'original_loan_budget' in input_json.keys():
            input_json['revised_budget'] =  int(input_json['original_loan_budget']) + budget.adjustments   
            input_json['loan_budget'] = int(input_json['revised_budget']) - budget.equity_budget
        
        if 'adjustments' in input_json.keys():
            input_json['revised_budget'] =  budget.original_loan_budget  + int(input_json['adjustments']) 
            input_json['loan_budget'] = int(input_json['revised_budget']) - budget.equity_budget     

        if 'equity_budget' in input_json.keys():
            input_json['loan_budget'] = budget.revised_budget - int(input_json['equity_budget'])        

        serializer = BudgetMasterSerializer(budget, data=input_json, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, *args, **kwargs):
            try:
                # Extract query parameters
                input_param = request.query_params
                loan_id = int(input_param.get('loan_id'))
                uses_type = input_param.get('uses_type')
                
                # Query and calculate totals at the database level
                queryset = BudgetMaster.objects.filter(
                    loan_id=loan_id,
                    uses_type=uses_type
                ).values(
                    'id', 'loan_id', 'original_loan_budget','adjustments','revised_budget', 
                    'equity_budget','loan_budget',
                    'acquisition_loan', 'building_loan', 'project_loan',
                    'mezzanine_loan', 'uses'
                ).order_by('uses')
                
                
                totals = BudgetMaster.objects.filter(
                    loan_id=loan_id,
                    uses_type=uses_type
                ).aggregate(
                    original_loan_budget_sum=Sum('original_loan_budget'),
                    adjustments_sum=Sum('adjustments'),
                    revised_budget_sum=Sum('revised_budget'),
                    equity_budget_sum=Sum('equity_budget'),
                    loan_budget_sum=Sum('loan_budget'),
                    acquisition_loan_sum=Sum('acquisition_loan'),
                    building_loan_sum=Sum('building_loan'),
                    project_loan_sum=Sum('project_loan'),
                    mezzanine_loan_sum=Sum('mezzanine_loan')
                )
                
                output_list = list(queryset)
                
                total_of_table = {
                    "uses": "Total",
                    "loan_id": loan_id,
                    "original_loan_budget": totals['original_loan_budget_sum'] or 0,
                    "adjustments": totals['adjustments_sum'] or 0,
                    "revised_budget": totals['revised_budget_sum'] or 0,
                    "equity_budget": totals['equity_budget_sum'] or 0,
                    "loan_budget": totals['loan_budget_sum'] or 0,
                    "acquisition_loan": totals['acquisition_loan_sum'] or 0,
                    "building_loan": totals['building_loan_sum'] or 0,
                    "project_loan": totals['project_loan_sum'] or 0,
                    "mezzanine_loan": totals['mezzanine_loan_sum'] or 0,
                }
                output_list.append(total_of_table)
                
                return Response(output_list, status=status.HTTP_200_OK)
            
            except ValueError as e:
                return Response({"error": "Invalid loan_id"}, status=status.HTTP_400_BAD_REQUEST)
            
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)     
    
    def delete(self,request,id):       
        try:
            BudgetMaster.objects.get(id=id) 
            BudgetMaster.objects.filter(id=id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except BudgetMaster.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
class BudgetSummary(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try: 
            input_param = request.query_params
            loan_id = input_param.get('loan_id')
            queryset = BudgetMaster.objects.filter(loan_id = loan_id).values('uses_type','total_funded_percentage').annotate(total_original_loan_budget=Sum('original_loan_budget'),
                                                                        total_adjustments= Sum('adjustments'),
                                                                        total_revised_budget= Sum('revised_budget'),
                                                                        total_equity_budget= Sum('equity_budget'),                           
                                                                        total_loan_budget= Sum('loan_budget'),
                                                                        total_acquisition_loan= Sum('acquisition_loan'),
                                                                        total_building_loan= Sum('building_loan'),
                                                                        total_mezzanine_loan= Sum('mezzanine_loan'),
                                                                        total_project_loan = Sum('project_loan'),
                                                                        total_remaining_to_fund = Sum('remaining_to_fund')).order_by('uses_type')
                                                                        
            
            totals = queryset.aggregate(
                        original_loan_budget_sum=Sum('total_original_loan_budget'),
                        adjustments_sum=Sum('total_adjustments'),
                        revised_budget_sum=Sum('total_revised_budget'),
                        equity_budget_sum=Sum('total_equity_budget'),
                        loan_budget_sum=Sum('total_loan_budget'),
                        acquisition_loan_sum=Sum('total_acquisition_loan'),
                        building_loan_sum=Sum('total_building_loan'),
                        mezzanine_loan_sum=Sum('total_mezzanine_loan'),
                        remaining_to_fund_sum=Sum('total_remaining_to_fund'))
                        
            total_output = {
                "uses_type" : 'Total',
                "total_original_loan_budget" : totals['original_loan_budget_sum'] or 0,
                "total_adjustments" : totals['adjustments_sum'] or 0,
                "total_revised_budget" : totals['revised_budget_sum'] or 0,
                "total_equity_budget" : totals['equity_budget_sum'] or 0,
                "total_loan_budget" : totals['loan_budget_sum'] or 0,
                "total_acquisition_loan" : totals['acquisition_loan_sum'] or 0,
                "total_building_loan" : totals['building_loan_sum'] or 0,
                "mezzanine_loan_sum" : totals['mezzanine_loan_sum'] or 0,
                "total_remaining_fund": totals['remaining_to_fund_sum'] or 0
                
           }
            result = list(queryset)
            result.append(total_output)
            return Response(result,status=status.HTTP_200_OK)
        except BudgetMaster.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class ProjectCreateUpdateDelete(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = ProjectSerializer(data = request.data)
        user_id = self.request.user.id
        if serializer.is_valid():
            serializer.save(user_id = user_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        input_params = request.query_params
        id = input_params.get('id')
        
        if id:
            try:
                project = Project.objects.get(pk=id)
                project_serializer = ProjectSerializer(project)
                return Response(project_serializer.data, status=status.HTTP_200_OK)
            except Project.DoesNotExist:
                return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "ID parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    
    def put(self, request,id):
        try:
            project = Project.objects.get(pk=id)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        try:
            document = Project.objects.get(pk=id)
            Project.objects.filter(id=id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class ProjectList(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_queryset(self):
        user = self.request.user
        id = user.id
        project = Project.objects.filter(user = id).order_by('-id')
        return project
    
class CreateRetrieveUpdateLoan(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        input_json = request.data
        project_id = request.data.get('project')   
        try:
            project_type = Project.objects.get(pk=project_id).project_type
            if Loan.objects.filter(project_id=project_id).exists():
                return Response({"detail": "This project is already associated with a loan."}, status=status.HTTP_409_CONFLICT)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        input_json['loantype'] = project_type
        input_json['status'] = 'Pending'
        input_json['start_date'] = input_json['start_date'] if input_json.get('start_date') is not None else timezone.now()
        input_json['end_date'] = input_json['end_date'] if input_json.get('end_date') is not None else None
        input_json['borrower'] = self.request.user.id
        serializer = LoanSerializer(data = input_json)
        document_type_obj = DocumentType.objects.filter(project_type = project_type).values_list('id', flat=True)
        
        if serializer.is_valid():
            loan = serializer.save()

            document_details = DocumentDetail.objects.filter(document_type_id__in = list(document_type_obj))
            document_details_list = list()
            for detail in document_details:
                document_details_list.append(Document(
                    loan=loan,
                    document_detail=detail,
                    status='Not Uploaded'
                ))
            
            Document.objects.bulk_create(document_details_list)
            user = request.user
            inspector = loan.inspector
            lender = loan.lender
            create_notification(inspector, user,"Loan Application", f"{user.username} has created a loan.", 'AL')
            create_notification(lender, user,"Loan Application", f"{user.username} has created a loan.", 'AL')            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        input_params = request.query_params
        id = input_params.get('id')
        
        if id:
            try:
                project = Loan.objects.get(pk=id)
                project_serializer = LoanSerializer(project)
                return Response(project_serializer.data, status=status.HTTP_200_OK)
            except Loan.DoesNotExist:
                return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "ID parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
    
    
    def put(self, request,id):
        try:
            budget = Loan.objects.get(pk=id)
        except Loan.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = LoanSerializer(budget, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, loanid):
        try:
            Loan.objects.get(pk=loanid)
            Loan.objects.filter(loanid=loanid).delete()
            BudgetMaster.objects.filter(loan_id= loanid).delete() 
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Loan.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
class UsesListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            input_params = request.query_params
            loan_id = input_params.get('loan_id')
            project_id = Loan.objects.get(pk=loan_id).project_id
            project_type = Project.objects.get(pk=project_id).project_type
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            file_path = os.path.join(BASE_DIR, 'construction', 'uses_mapping.json')

            with open(file_path,'r') as file:
                uses_dictionary = json.load(file)
                response = uses_dictionary.get(project_type)
            return Response(response)
        except Loan.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND) 
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND) 
        
class InsertUsesforBudgetMaster(APIView):
    
    def post(self, request):
        input_json = request.data
        loan_id = input_json.get('loan_id')
        try:
            loan = Loan.objects.get(loanid=loan_id)
        except Loan.DoesNotExist:
            return Response({"error": "Loan with provided loan_id does not exist"}, status=400)
        budget_master_instances = []

        for i, j in input_json.get('Uses').items():
            uses = "_".join(i.split(" ")).lower()  
            for sub_uses in j:
                budget_master_instances.append(
                    BudgetMaster(
                        uses=sub_uses,
                        uses_type=uses,
                        loan=loan,
                        original_loan_budget = 0,
                        loan_budget = 0,
                        acquisition_loan = 0,
                        building_loan=0,
                        project_loan = 0,
                        mezzanine_loan = 0
                    )
                )

        BudgetMaster.objects.bulk_create(budget_master_instances)

        return Response({"Response": "Data Inserted"}, status=201)


class ListUsesType(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            input_params = request.query_params
            loan_id = input_params.get('loan_id')
            Loan.objects.get(pk=loan_id)
            query_set = BudgetMaster.objects.filter(loan_id = loan_id).order_by('uses_type').values_list('uses_type',flat=True).distinct()
            return Response({
                "uses_type":query_set
                },status=status.HTTP_200_OK)
        except Loan.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND) 
        except BudgetMaster.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND) 

class LoanApprovalStatus(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        input_json = request.data
        loan_id = input_json.get('loan_id')
        loan_obj = Loan.objects.get(pk=loan_id)
        if loan_obj.status == 'Pending' or loan_obj.status == 'Rejected':
            loan_obj.status = 'In Review'
            loan_obj.save()
            create_notification(loan_obj.inspector, request.user,"Loan Application", f"{request.user.username} has applied for a loan.", 'AL')
            create_notification(loan_obj.lender, request.user,"Loan Application", f"{request.user.username} has applied for a loan.", 'AL')  
            return Response(status=status.HTTP_200_OK)
        else:
            return Response({'error':'loan can only be submitted when status is Pending or Rejected'},status=status.HTTP_403_FORBIDDEN)

    def put(self, request):
        input_json = request.data
        status_action = input_json.get('status_action')
        loan_id = input_json.get('loan_id')

        try:
            my_instance = Loan.objects.get(pk=loan_id)
        except Loan.DoesNotExist:
            return Response({'error': 'Loan not found'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        profile = UserProfile.objects.get(user=user)

        update_status = None
        if profile.role_type == "inspector" and my_instance.status == "In Review":
            if status_action == "Approve":
                update_status = "In Approval"
                create_notification(my_instance.borrower, request.user,"Loan Application", f"{request.user.username} has submitted the loan for approval to the lender.", 'IN')
                create_notification(my_instance.lender, request.user,"Loan Application", f"{request.user.username} has done the inspection and sent for approval to you.", 'AL')  
            elif status_action == "Reject":
                update_status = "Rejected"
                create_notification(my_instance.borrower, request.user,"Loan Application", f"Your Loan with Loan ID :{my_instance.loanid} has been rejected during inspection.", 'WA')

        elif profile.role_type == "lender" and my_instance.status == "In Approval":
            if status_action == "Approve":
                update_status = "Approved"
                create_notification(my_instance.borrower, request.user,"Loan Application", f"Your Loan with Loan ID: {my_instance.loanid} has been Approved.", 'SU')

            elif status_action == "Reject":
                update_status = "Rejected"
                create_notification(my_instance.borrower, request.user,"Loan Application", f"Your Loan with Loan ID :{my_instance.loanid} has been rejected by the Lender", 'WA')

        if update_status:
            my_instance.status = update_status
            my_instance.save()
            return Response({"Response":"Status Updated"},status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid action or role'}, status=status.HTTP_400_BAD_REQUEST)



class CreateUpdateDrawRequest(APIView):
    permission_classes = [IsAuthenticated]  
 
    def post(self, request, *args, **kwargs):
        try:
            input_json = request.data
            loan_id = input_json.get("loan_id")
            budget_master_obj = BudgetMaster.objects.filter(loan_id=loan_id).order_by('uses_type','uses').values_list('id','loan_budget')
            created_data = []
            lis_budget_ids = [i[0] for i in budget_master_obj ]
            draw_req_obj = DrawRequest.objects.filter(budget_master_id__in = list(lis_budget_ids))
            if len(draw_req_obj) == 0:
                draw_request = 0                
                for obj in budget_master_obj:
                    budget_amount = obj[1]
                    released_amount = 0                    
                    new_instance = DrawRequest(
                        budget_master_id=obj[0],
                        draw_request= 0,                    
                        released_amount=released_amount,
                        budget_amount=budget_amount,
                        funded_amount=0,
                        balance_amount = budget_amount-released_amount,
                        draw_amount = 0,
                        description = None,
                        requested_date=timezone.now(),
                    )
                    created_data.append(new_instance)
            else:
                val = draw_req_obj.order_by('-draw_request').values_list('draw_request',flat=True)
                draw_request = val[0] +1
                # # Check the status of the previous draw from the DrawTracking table
                # last_draw = DrawTracking.objects.get(loan_id=loan_id,draw_request=val[0])
                # # If the last draw exists and its status is "Pending" or "In Review", prevent new draw creation
                # if last_draw and last_draw.draw_status in ["Pending", "In Review"]:
                #     return Response(
                #          {"error":"The previous draw is still 'Pending' or 'In Review'. Cannot create a new draw."},
                #          status=status.HTTP_400_BAD_REQUEST
                #     )
                
                for obj in budget_master_obj:
                    budget_amount = obj[1]  
                    released_amount_previous = DrawRequest.objects.filter(budget_master_id=obj).values_list('released_amount',flat=True)        
                    released_amount_list = list(released_amount_previous)
                    if released_amount_list:
                        released_amount=released_amount_list[0]
                    else:
                        released_amount = 0
                    
                    new_instance = DrawRequest(
                        budget_master_id=obj[0],
                        draw_request = draw_request,                    
                        released_amount = released_amount,
                        budget_amount = budget_amount,
                        funded_amount = 0,
                        balance_amount = budget_amount-released_amount,
                        draw_amount = 0,
                        description = None,
                        requested_date=timezone.now(),
                    )
                    created_data.append(new_instance)
            DrawRequest.objects.bulk_create(created_data)
            
            totals = DrawRequest.objects.filter(budget_master_id__in = list(lis_budget_ids),
                    draw_request=draw_request
                ).aggregate(
                    total_released_amount=Sum('released_amount'),
                    total_budget_amount=Sum('budget_amount'),
                    total_funded_amount=Sum('funded_amount'),
                    total_balance_amount=Sum('balance_amount'),
                    total_draw_amount=Sum('draw_amount')
                )
            totals['requested_date']=timezone.now()
            totals['loan'] = Loan.objects.get(pk = loan_id)
            totals['draw_request'] = draw_request
            totals['draw_status'] = "Pending"
            DrawTracking.objects.create(**totals)
            serializers = DrawRequestSerializer(created_data,many=True)
            return Response(serializers.data,status=status.HTTP_201_CREATED) 
        except DrawRequest.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        
    def put(self, request):
            try:
                input_json = request.data
                id = input_json.get('id')
                try:
                    my_instance = DrawRequest.objects.get(pk=id)
                except DrawRequest.DoesNotExist:
                    return Response({'error': 'DrawRequest not found'}, status=status.HTTP_404_NOT_FOUND)        
                user = request.user
                profile = UserProfile.objects.get(user=user)
                draw_request = my_instance.draw_request
                budget_master_id = my_instance.budget_master_id
                try:
                    loan_id = BudgetMaster.objects.get(pk=budget_master_id).loan_id
                except BudgetMaster.DoesNotExist:
                    return Response({'error': 'BudgetMaster not found'}, status=status.HTTP_404_NOT_FOUND)

                lis_budget_ids = BudgetMaster.objects.filter(loan_id=loan_id).values_list('id',flat=True)
                try:
                    draw_tracking_obj = DrawTracking.objects.get(draw_request=draw_request, loan_id=loan_id)
                except DrawTracking.DoesNotExist:
                    return Response({'error': 'DrawTracking not found'}, status=status.HTTP_404_NOT_FOUND)

         
                totals = DrawRequest.objects.filter(budget_master_id__in = list(lis_budget_ids),
                draw_request=draw_request
                ).aggregate(
                    total_funded_amount=Sum('funded_amount'),
                    total_draw_amount=Sum('draw_amount')
                )

                if profile.role_type == "borrower":
                    my_instance.draw_amount=input_json.get('draw_amount')
                    my_instance.description=input_json.get('description')
                    my_instance.save()
                    totals = DrawRequest.objects.filter(budget_master_id__in = list(lis_budget_ids),
                    draw_request=draw_request
                    ).aggregate(
                        total_funded_amount=Sum('funded_amount'),
                        total_draw_amount=Sum('draw_amount')
                    )
                    draw_tracking_obj.total_draw_amount = totals['total_draw_amount']
                    draw_tracking_obj.save()
                    return Response({"Response":"Fields Updated"},status=status.HTTP_200_OK)

                elif profile.role_type == "lender":
                    my_instance.funded_amount = input_json.get('funded_amount')
                    my_instance.save()
                    return Response({"Response":"Funded Amount Updated"},status=status.HTTP_200_OK)

                else:
                    return Response({'error': 'Invalid action or role'}, status=status.HTTP_400_BAD_REQUEST)
                
            except DrawRequest.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST) 
        
    
    def get(self,request):
        input_params = request.query_params
        loan_id = input_params.get('loan_id')
        draw_request = input_params.get('draw_request')
        if not loan_id:
            return Response({"error":"loan_id is required"},status=status.HTTP_400_BAD_REQUEST)
        

        budget_master_id = BudgetMaster.objects.filter(loan_id = loan_id).values_list('id',flat=True)

        if draw_request:
            draw_request_obj = DrawRequest.objects.filter(
                budget_master_id__in= budget_master_id,
                draw_request = draw_request
            ).order_by('budget_master__uses_type','budget_master__uses')
            
        else:
            draw_request_obj = DrawRequest.objects.filter(
                budget_master_id__in= budget_master_id
            ).order_by('budget_master__uses_type','budget_master__uses')
        serializers = DrawRequestSerializer(draw_request_obj,many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
    

class DrawTrackingListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DrawTrackingSerializer

    def get_queryset(self):
        input_params = self.request.query_params
        loan_id = input_params.get("loan_id")
        return DrawTracking.objects.filter(loan_id=loan_id)
    
class RetrieveDeleteUpdateDrawTracking(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        try:
            draw_tracking_obj = DrawTracking.objects.get(pk=id)
            if draw_tracking_obj.draw_status in ['Pending','In Review']: 
                draw_request = draw_tracking_obj.draw_request
                loan_id = draw_tracking_obj.loan
                draw_tracking_obj.delete()
                budget_master_ids = BudgetMaster.objects.filter(loan_id=loan_id).values_list('id',flat=True)
                DrawRequest.objects.filter(draw_request=draw_request, budget_master_id__in = budget_master_ids).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error":"Only draw requests with 'Pending' or 'In Review' status can be deleted."},status=status.HTTP_403_FORBIDDEN)
        except DrawTracking.DoesNotExist:
            return Response({"error": "DrawTracking object not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class DrawTrackingStatus(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        input_json = request.data
        loan_id = input_json.get('loan_id')
        draw_request = input_json.get('draw_request')
        try:
            loan_obj = Loan.objects.get(pk=loan_id)
        except Loan.DoesNotExist:
            return Response({'Response':'Loan does not exist'})
        
        try:
            draw_tracking_obj = DrawTracking.objects.get(loan_id=loan_id, draw_request=draw_request)
        except DrawTracking.DoesNotExist:
            return Response({'error': 'Draw tracking object not found'})

        
        if draw_tracking_obj.draw_status in ['Pending', 'Rejected']:
            draw_tracking_obj.draw_status = 'In Review'
            draw_tracking_obj.save()
            create_notification(loan_obj.inspector, request.user,"Draw Application", f"{request.user.username} has submitted a Draw Request.", 'AL')
            create_notification(loan_obj.lender, request.user,"Draw Application", f"{request.user.username} has submitted a Draw Request.", 'AL')  

            return Response({"Response":"Draw successfully submitted"},status=status.HTTP_200_OK)
        else:
            return Response({'error':'draw can only be submitted when status is Pending or Rejected'},status=status.HTTP_403_FORBIDDEN)

    def put(self, request):
        input_json = request.data
        status_action = input_json.get('status_action')
        draw_tracking_id = input_json.get('draw_tracking_id')

        try:
            my_instance = DrawTracking.objects.get(pk=draw_tracking_id)
        except DrawTracking.DoesNotExist:
            return Response({'error': 'DrawTracking not found'}, status=status.HTTP_404_NOT_FOUND)
        loan_obj = Loan.objects.get(pk=my_instance.loan_id)

        user = request.user
        profile = UserProfile.objects.get(user=user)
        update_status = None
        if profile.role_type == "inspector" and my_instance.draw_status == "In Review":
            if status_action == "Approve":
                update_status = "In Approval"
                create_notification(loan_obj.borrower, request.user,"Draw Application", f"{request.user.username} has submitted the draw for approval to the lender.", 'IN')
                create_notification(loan_obj.lender, request.user,"Draw Application", f"{request.user.username} has done the inspection and sent for approval to you.", 'AL')  

            elif status_action == "Reject":
                update_status = "Rejected"
                create_notification(loan_obj.borrower, request.user,"Draw Application", f"Draw request no. : {my_instance.draw_request} for Loan ID :{loan_obj.loanid} has been rejected during inspection.", 'WA')

        elif profile.role_type == "lender" and my_instance.draw_status == "In Approval":
            if status_action == "Approve":
                update_status = "Approved"
                budget_master_id_lis = BudgetMaster.objects.filter(loan_id=my_instance.loan_id).values_list('id',flat=True)
                draw_request_instance = DrawRequest.objects.filter(draw_request = my_instance.draw_request, budget_master_id__in = list(budget_master_id_lis))
                
                total_funded = draw_request_instance.aggregate(total_funded=Sum('funded_amount'))['total_funded'] or 0
                
                my_instance.total_funded_amount = total_funded

                # Loop through each line item and calculate released amount per line item
                for line_item in draw_request_instance:
                    # Fetch previous draws for the same line item using lte
                    previous_draws = DrawRequest.objects.filter(
                        draw_request__lte=my_instance.draw_request,  # Fetch previous draws less than or equal to the current one
                        budget_master_id=line_item.budget_master_id  # For the same budget line item
                    )
                    
                    line_item.released_amount = previous_draws.aggregate(total_funded=Sum('funded_amount'))['total_funded'] or 0
                    line_item.save()
            

                previous_and_current_draws = DrawRequest.objects.filter(
                     draw_request__lte=my_instance.draw_request,  # Fetch draw requests less than or equal to the current one
                     budget_master_id__in=list(budget_master_id_lis)  # Filter by the budget masters related to this loan
                )
                
                # Calculate the total funded amount for previous and current draws
                previous_and_current_funded_total = previous_and_current_draws.aggregate(
                    total_funded=Sum('funded_amount')
                )['total_funded'] or 0 

                # Assign the total released amount (which includes previous draws)
                my_instance.total_released_amount = previous_and_current_funded_total
               
                create_notification(loan_obj.borrower, request.user,"Draw Application", f"Draw request no. : {my_instance.draw_request} for Loan ID: {loan_obj.loanid} has been Approved.", 'SU')

            elif status_action == "Reject":
                update_status = "Rejected"
                create_notification(loan_obj.borrower, request.user,"Draw Application", f"Draw request : {my_instance.draw_request} with Loan ID :{loan_obj.loanid} has been rejected by lender.", 'WA')

        if update_status:
            my_instance.draw_status = update_status
            my_instance.save()
            return Response({"Response":"Status Updated"},status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid action or role'}, status=status.HTTP_400_BAD_REQUEST)

class UploadBudget(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self,request):
        serializer = BudgetMasterSerializer(data=request.data)
        loan_id = request.data.get('loan_id')
        file = request.FILES.get('file')

        if not loan_id:
            return Response({'error': 'Loan ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        
        if not file:
             return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            loan = Loan.objects.get(loanid=loan_id)
        except Loan.DoesNotExist:
            return Response({'error': 'Loan with this ID does not exist'}, status=status.HTTP_400_BAD_REQUEST) 
        
        try:
            df = pd.read_excel(file)
        except Exception as e:
            return Response({'error': f'Failed to read Excel file: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST) 
        
        for column in ['original loan budget','adjustments','equity budget']:
            if column not in df.columns:
                return Response({'response':f"{column} not present"},status=status.HTTP_404_NOT_FOUND)
       
        if 'revised budget' not in df.columns:
            df['revised budget'] = df['original loan budget'] + df['adjustments']  
        if 'loan budget' not in df.columns:
            df['loan budget'] = df['original loan budget'] + df['adjustments']- df['equity budget'] 
        
        budget_instances = []

        for index, row in df.iterrows():
            budget_instance = BudgetMaster(
                loan=loan, 
                uses=row.get('uses'),
                uses_type=row.get('uses type'),
                original_loan_budget=row.get('original loan budget'),
                adjustments=row.get('adjustments'),
                equity_budget=row.get('equity budget'),
                revised_budget=row.get('revised budget'),
                loan_budget = row.get('loan budget')
            )
            budget_instances.append(budget_instance)
        try:
            BudgetMaster.objects.bulk_create(budget_instances)
            
        except Exception as e:
            return Response({'error': f'Failed to save data: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)  
        
        return Response({'message': 'Data uploaded and saved successfully'}, status=status.HTTP_201_CREATED)
    
class RetrieveSpentToDate(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self,request):
        input_params = request.query_params

        loan_id = input_params.get('loan_id')
        if not loan_id:
            return Response({'error':'loan id is required'},status=400)
        
        if not Loan.objects.filter(loanid=loan_id).exists():
            return Response({"error":"loanid does not exist"},status=400)
        
        try:
            draws = DrawTracking.objects.filter(loan_id=loan_id) 
            if draws:
                spent_to_date = draws.aggregate(total_spent=Sum('total_funded_amount'))['total_spent'] or 0
                return Response({"spent_to_date":spent_to_date, 'message': 'Success'},status=200)
            else:
                 return Response({ 'spent_to_date': 0,'message': f'No draws found for loan_id {loan_id}'}, status=404)
            
        except Exception as e:
            return Response({"error":str(e)},status=500)
                
        