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
from .serializers import *
import datetime
import json
import os
from django.db.models import Max,Sum



class LoanListView(generics.ListAPIView):
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        profile = UserProfile.objects.get(user=user)
        match profile.role_type:
            case "lender":
                loans = Loan.objects.filter(lender_id=user).order_by('loanid')
            case "inspector":
                loans = Loan.objects.filter(inspector_id=user).order_by('loanid')
            case "borrower":
                loans = Loan.objects.filter(borrower_id=user).order_by('loanid')

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
                my_instance.date_requested = datetime.datetime.now()
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
        

class ReturnDisbursementStatusMapping(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        user = request.user
        profile = UserProfile.objects.get(user=user)
        role_type = profile.role_type
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
                queryset = DisbursementSchedule.objects.filter(loan_id =loan_id).order_by('review_months')
                serializer = DisbursementScheduleSerializer(queryset, many=True)
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
        print(data)
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
        
        serializer = BudgetMasterSerializer(budget, data=request.data, partial=True)
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
                    'id', 'loan_id', 'project_total', 'loan_budget',
                    'acquisition_loan', 'building_loan', 'project_loan',
                    'mezzanine_loan', 'uses'
                ).order_by('uses')
                
                
                totals = BudgetMaster.objects.filter(
                    loan_id=loan_id,
                    uses_type=uses_type
                ).aggregate(
                    project_total_sum=Sum('project_total'),
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
                    "project_total": totals['project_total_sum'] or 0,
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
        input_param = request.query_params
        loan_id = input_param.get('loan_id')
        queryset = BudgetMaster.objects.filter(loan_id = loan_id).values('uses_type').annotate(total_project_total=Sum('project_total'),
                                                                     total_loan_budget= Sum('loan_budget'),
                                                                     total_acquisition_loan= Sum('acquisition_loan'),
                                                                     total_building_loan= Sum('building_loan'),
                                                                     total_mezzanine_loan= Sum('mezzanine_loan')).order_by('uses_type')
        return Response(queryset)

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
        project = Project.objects.filter(user = id).order_by('id')
        return project
    
class CreateRetrieveUpdateLoan(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        input_json = request.data
        project_id = request.data.get('project')        
        project_type = Project.objects.get(pk=project_id).project_type
        input_json['loantype'] = project_type
        input_json['status'] = 'Pending'
        input_json['borrower'] = self.request.user.id
        serializer = LoanSerializer(data = input_json)

        if serializer.is_valid():
            serializer.save()
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
                        project_total = 0,
                        loan_budget = 0,
                        acquisition_loan = 0,
                        building_loan=0,
                        project_loan = 0,
                        mezzanine_loan = 0
                    )
                )

        BudgetMaster.objects.bulk_create(budget_master_instances)

        return Response({"Response": "Data Inserted"}, status=201)
