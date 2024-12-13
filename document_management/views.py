import gridfs.errors
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
from .helper_function import document_detail_list_json,generate_summary_and_store
import datetime
import json
from django.db.models import Max,Sum,Q
from django.http import HttpResponse, JsonResponse
import gridfs
from pymongo import MongoClient
from django.conf import settings
from bson import ObjectId
from django.http import FileResponse,StreamingHttpResponse
from io import BytesIO
import base64
from doc_summary_qna.doc_processing import *
from doc_summary_qna.prompts import *
from alerts.views import create_notification
from users.permissions import subscription
from django.utils import timezone
import mimetypes
from django.shortcuts import get_object_or_404
from django.db import transaction

# local
# client = MongoClient(settings.MONGODB['HOST'], settings.MONGODB['PORT'])
# Mongo Atlas
client = MongoClient(settings.MONGODB['URI'])
db = client[settings.MONGODB['NAME']]
fs = gridfs.GridFS(db)


class DocumentManagement(APIView):
    permission_classes = [IsAuthenticated,subscription]

    def post(self,request):
        serializer = DocumentSerializer(data=request.data)
        input_json = request.data

        if serializer.is_valid():
            pdf_file = request.FILES['pdf_file']
            pdf_file_data = pdf_file.read()
            file_id = fs.put(pdf_file_data, filename=pdf_file.name)
            file_name = pdf_file.name
            
            document_detail= DocumentDetail.objects.get(
                id=input_json['document_detail_id']
            )
            
            existing_instance = Document.objects.filter(
                Q(document_detail=document_detail) & Q(loan_id=request.data['loan'])
            ).first()

            if existing_instance:
                loan_obj = Loan.objects.get(pk=existing_instance.loan_id)
                existing_file_id = ObjectId(existing_instance.file_id)
                fs.delete(existing_file_id)
                existing_instance.file_id = str(file_id)
                existing_instance.status = 'In Review'
                existing_instance.file_name = file_name
                existing_instance.uploaded_at = datetime.datetime.now()
                create_notification(loan_obj.inspector, request.user,"Document Management", f"{request.user.username} has submitted a {document_detail.name} document.",loan=loan_obj,notification_type= 'AL')
                create_notification(loan_obj.lender, request.user,"Document Management", f"{request.user.username} has submitted a {document_detail.name} document.",loan=loan_obj,notification_type= 'AL')  
                if pdf_file.name.endswith('.pdf'):
                    summary_response = generate_summary_and_store(pdf_file_data, existing_instance)
                    existing_instance.summary = summary_response
                else:
                    existing_instance.summary = {"response": "Summary can only be generated for pdf file"}
                existing_instance.save()
                serializer = DocumentSerializer(existing_instance)
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            else:
                
                document_instance = serializer.save(file_id=str(file_id),status='In Review',file_name=file_name, document_detail=document_detail,uploaded_at = datetime.datetime.now())
                if pdf_file.name.endswith('.pdf'):
                    summary_response = generate_summary_and_store(pdf_file, document_instance)
                    document_instance.summary = summary_response  # Save summary to the new instance
                else:
                    document_instance.summary = {"response": "Summary can only be generated for pdf file"}
                document_instance.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self,request):
        try:
            input_param = request.query_params
            file_id = input_param.get('file_id')
            file_id = ObjectId(file_id)
            file = fs.get(file_id)
            pdf_data = base64.b64encode(file.read()).decode('utf-8')
            return JsonResponse({'pdf_base64': pdf_data})
        except gridfs.errors.NoFile:
            raise Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)
        
    def delete(self, request, id):
        document = Document.objects.get(pk=id)
        
        file_id = document.file_id
        if file_id:
            file_id = ObjectId(file_id)
            fs.delete(file_id)
        
        document.status = 'Not Uploaded'
        document.file_id = None
        document.uploaded_at = None
        document.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
class ListOfDocument(APIView):
    permission_classes = [IsAuthenticated,subscription]
    
    def get(self,request):
        try:
            input_param = request.query_params
            loan_id = input_param.get('loan_id')
            document_type_id = input_param.get('document_type_id')
            document_status = input_param.get("document_status")
            queryset = Document.objects.filter(loan_id =loan_id).select_related('document_detail').order_by('document_detail__type', 'document_detail__name')

            if document_type_id:
                queryset = queryset.filter(document_detail__document_type_id=document_type_id)                
            
            if document_status:
                queryset = queryset.filter(status=document_status)
            queryset = queryset.select_related('document_detail').order_by('document_detail__type', 'document_detail__name')
            
            serializer = DocumentSerializer(queryset, many=True)
            organized_data = document_detail_list_json(serializer)
            return Response(organized_data)
        except Exception as e:
            return Response(f"Error: {str(e)}",status=500)
        
class DocSummaryView(APIView):
    permission_classes = [IsAuthenticated,subscription]
    
    def post(self,request):
        try:
            file_id = request.data.get("file_id")
            file_id = ObjectId(file_id)
            file = fs.get(file_id)
            # text extraction
            text = get_pdf_text_doc_manager(file) 
            # creating text chunks
            chunks = get_text_chunks(text)
            # creating vector store and storing it 
            get_vector_store(chunks)
            user_question = predefined_prompts()
            response = user_input(user_question)
            return Response({"response":response})
        except Exception as e:
            return Response({"Error":str(e)},status=500)

class DocumentStatus(APIView):
    permission_classes = [IsAuthenticated,subscription]

    def post(self, request):
        input_json = request.data
        status_action = input_json.get('status_action')
        document_id = input_json.get('document_id')
        comment = input_json.get('document_comment')

        try:
            my_instance = Document.objects.get(pk=document_id)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

        loan_obj = Loan.objects.get(pk=my_instance.loan_id)
        document_detail_obj = DocumentDetail.objects.get(pk=my_instance.document_detail_id)
        user = request.user
        profile = UserProfile.objects.get(user=user)

        update_status = None
        if profile.role_type == "inspector" and my_instance.status == "In Review":
            if status_action == "Approve":
                update_status = "Pending Lender"
                my_instance.document_comment = comment
                create_notification(loan_obj.borrower, request.user,"Document Management", f"{request.user.username} has submitted the {document_detail_obj.name} document for approval to the lender.",loan=loan_obj,notification_type= 'IN')
                create_notification(loan_obj.lender, request.user,"Document Management", f"{request.user.username} has done the verified the {document_detail_obj.name} document and sent for approval to you.",loan=loan_obj,notification_type= 'AL')  

            elif status_action == "Reject":
                update_status = "Rejected"
                my_instance.document_comment = comment
                create_notification(loan_obj.borrower, request.user,"Document Management", f"{document_detail_obj.name} document  for Loan ID :{loan_obj.loanid} has been rejected.",loan=loan_obj,notification_type= 'WA')

        elif profile.role_type == "lender" and my_instance.status == "Pending Lender":
            if status_action == "Approve":
                update_status = "Approved"
                my_instance.document_comment = comment
                create_notification(loan_obj.borrower, request.user,"Document Management", f"{document_detail_obj.name} document  for Loan ID :{loan_obj.loanid} has been Approved.",loan=loan_obj,notification_type= 'SU')

            elif status_action == "Reject":
                update_status = "Rejected"
                my_instance.document_comment = comment
                create_notification(loan_obj.borrower, request.user,"Document Management", f"{document_detail_obj.name} document  for Loan ID :{loan_obj.loanid} has been rejected by lender.",loan=loan_obj,notification_type= 'WA')

        if update_status:
            my_instance.status = update_status
            my_instance.save(update_fields=['status', 'document_comment'] if 'document_comment' in input_json else ['status'])
            return Response({"Response":"Status Updated"},status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid action or role'}, status=status.HTTP_400_BAD_REQUEST)

        
class CreateRetrieveUpdateDocumentType(APIView):
    permission_classes = [IsAuthenticated,subscription]
 
    def post(self,request):
        try:
            input_json = request.data
            project_type = input_json.get('project_type')  
            document_type = input_json.get('document_type')
            serializer = DocumentTypeSerializer(data = input_json)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except DocumentType.DoesNotExist:
            return Response(serializer.errors,status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self,request):
        try:    
            input_params = request.query_params
            document_type_id= input_params.get('document_type_id')
            if document_type_id:
                document_type = DocumentType.objects.get(pk=document_type_id)
                serializer = DocumentTypeSerializer(document_type)                
            else:
                document_types = DocumentType.objects.all()
                serializer = DocumentTypeSerializer(document_types,many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except DocumentType.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request,id):
        try:
            DocumentType.objects.get(pk=id)
        except DocumentType.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = DocumentTypeSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def delete(self, request, id):
        try:
            DocumentType.objects.get(pk=id)
            DocumentType.objects.filter(id=id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except DocumentType.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        

class CreateRetrieveUpdateDocumentDetail(APIView):
    permission_classes = [IsAuthenticated,subscription]

    def post(self, request):
        input_json = request.data
        document_type_ids = {doc.get("document_type_id") for doc in input_json}
        document_types = DocumentType.objects.in_bulk(document_type_ids)
        
        document_details = []
        for document in input_json:
            document_type = document_types.get(document.get("document_type_id"))
            if document_type:
                for name in document.get('name'):
                    document_details.append(
                        DocumentDetail(
                            document_type=document_type,
                            name=name,
                            type=document.get('type')
                        )
                    )
        
        DocumentDetail.objects.bulk_create(document_details)
        return Response(status=status.HTTP_200_OK)

class ListDocumentTypeForLoan(generics.ListAPIView):
    permission_classes = [IsAuthenticated,subscription]
    serializer_class = DocumentTypeSerializer
    
    def get_queryset(self):
        input_params = self.request.query_params
        loan_id = input_params.get('loan_id')
        try:
            loantype = Loan.objects.get(loanid=loan_id).loantype
            queryset = DocumentType.objects.filter(project_type=loantype)
            return queryset
        except Loan.DoesNotExist:
            return Response({"error": "Loan not found"}, status=status.HTTP_404_NOT_FOUND)
        
class RetrieveDocuments(APIView):

    permission_classes = [IsAuthenticated]
    
    def get(self,request):

        try:
            input_param = request.query_params
            loan_id = input_param.get('loan_id')
            document_type_id = input_param.get('document_type_id')
            document_status = input_param.get("document_status") 

            loan = Loan.objects.get(loanid=loan_id)

            document_type_details = DocumentType.objects.filter(project_type=loan.loantype).values_list('id','document_type')
            print('doc',document_type_details)
            document_type_id = [i[0] for i in document_type_details]
            print(document_type_id)
            output_dict = dict()
            print(list(document_type_details))
            for id,document_type in list(document_type_details):
                print(id,document_type)
                queryset = Document.objects.filter(loan_id=loan_id, document_detail__document_type_id=id).select_related('document_detail').order_by('document_detail__type', 'document_detail__name')
                print(queryset)
                output_dict[document_type] = document_detail_list_json(DocumentSerializer(queryset, many=True))

            return Response({'output': output_dict})

        except Loan.DoesNotExist:
            return Response({'error': 'Loan not found'}, status=404)
        
        except DocumentType.DoesNotExist:
            return Response({'error': 'No matching document type found'}, status=404)
        
        except Exception as e:
            return Response(f"Error: {str(e)}", status=500) 
        
class FeedbackView(APIView):

    permission_classes = [IsAuthenticated] 

    def post(self,request):

        data = request.data 
        document_id = data.get('document_id')
        comment = data.get('comment') 
        user = request.user 

        if not document_id:
            return Response({'message':f'{document_id} is required'},status=status.HTTP_404_NOT_FOUND) 
        
        try:
            document = Document.objects.get(pk=document_id)
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND) 
        
        feedback = {
        'user': user.id,  # assuming you want to save the user's ID
        'document': document.id,
        'comment': comment,
        'created_at': timezone.now()
    }
        
        serializer = FeedbackSerializer(data=feedback)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self,request):

        input_params = request.query_params 
        document_id = input_params.get('document_id') 

        if not document_id:
            return Response({"message":"document id required"},status=status.HTTP_404_NOT_FOUND) 

        try:
             feedbacks = Feedback.objects.filter(document_id=document_id).select_related('user__user_profile').order_by('-created_at')
        except Feedback.DoesNotExist:
             return Response({"error": "Document id not found"}, status=status.HTTP_404_NOT_FOUND) 
        response_data = []
        for feedback in feedbacks:
            response_data.append({
                'id': feedback.id,
                'user': feedback.user.id,
                'document': feedback.document.id,
                'created_at': feedback.created_at,
                'comment': feedback.comment,
                'role_type': feedback.user.user_profile.role_type if hasattr(feedback.user, 'user_profile') else None,
            })
        return Response(response_data, status=status.HTTP_200_OK) 



    
class RetrieveSummary(APIView):

    permission_classes = [IsAuthenticated,subscription] 

    def get(self,request):
        input_params = request.query_params 
        id = input_params.get('id') 

        my_instance = Document.objects.get(pk=id)
        my_instance.summary
        return Response({"summary":my_instance.summary}, status=status.HTTP_200_OK)
    

class DrawRequestDocuments(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        input_json = request.data
        # Use the serializer to validate the incoming data
        serializer = DrawDocumentsSerializer(data=input_json)
        if serializer.is_valid():
            # Extract validated data
            doc_name = serializer.validated_data['doc_name']
            loan_id = input_json.get('loan_id')
            draw_request = input_json.get('draw_request')
            if not loan_id or not draw_request:
                return Response({'response':'loan_id and draw_request are required params'},status=status.HTTP_404_NOT_FOUND)
            # Get draw_tracking object or return 404 if not found
            draw_tracking = get_object_or_404(DrawTracking, loan_id=loan_id, draw_request=draw_request)

            # Handle file upload with GridFS
            pdf_file = request.FILES['pdf_file']
            file_id = fs.put(pdf_file, filename=pdf_file.name)
            file_name = pdf_file.name

            # Create DrawDocument instance
            queryset = DrawDocuments.objects.create(
                user=user,
                doc_name = doc_name,
                file_name= file_name,
                uploaded_at =  timezone.now(),
                draw_tracking = draw_tracking,
                file_id = file_id,
                status = 'In Review'
            )
            serializer = DrawDocumentsSerializer(queryset)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
    
    def get(self, request):
        try:
            input_param = request.query_params
            file_id = input_param.get('file_id')
            output_type = input_param.get('output_type')

            file_id = ObjectId(file_id)
            file = fs.get(file_id)  # Assuming 'fs' is your GridFS instance

            # Guess the MIME type from the file's filename
            mime_type, _ = mimetypes.guess_type(file.filename)
            if not mime_type:
                mime_type = 'application/octet-stream'  # Default MIME type if unknown
            print(output_type)
            if output_type and output_type.lower() == "file":
                # Directly return the file as a response
                response = FileResponse(file, content_type=mime_type)
                response['Content-Disposition'] = f'attachment; filename="{file.filename}"'
                return response
            elif output_type and output_type.lower() == "json":
                # Base64 encode the file for returning as JSON
                pdf_data = base64.b64encode(file.read()).decode('utf-8')
                return JsonResponse({'pdf_base64': pdf_data})
            else:
                pdf_data = base64.b64encode(file.read()).decode('utf-8')
                return JsonResponse({'pdf_base64': pdf_data})
            
        except gridfs.errors.NoFile:
            raise Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)
        
    def delete(self, request, id):
        # Get the document or return 404 if not found
        document = get_object_or_404(DrawDocuments, pk=id)

        # Wrap in a transaction to ensure atomicity (both will be deleted or none)
        with transaction.atomic():
            # If the document has an associated file_id in GridFS
            file_id = document.file_id
            if file_id:
                try:
                    # Convert file_id to ObjectId if it's not already
                    fs.delete(ObjectId(file_id))
                except gridfs.errors.NoFile:
                    raise Response(status=status.HTTP_404_NOT_FOUND)
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            document.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    
class ListDrawDocuments(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request):
        try:
            input_params = request.query_params
            loan_id = input_params.get('loan_id')
            draw_request = input_params.get('draw_request')
            document_status = input_params.get('status')
            if not draw_request:
                return Response({'response':'draw request is a mandatory params'},status=status.HTTP_400_BAD_REQUEST)
            if not loan_id:
                return Response({'response':'loan_id is a mandatory params'},status=status.HTTP_400_BAD_REQUEST)
            draw_tracking = DrawTracking.objects.get(loan_id= loan_id,draw_request=draw_request)
            queryset = DrawDocuments.objects.filter(draw_tracking_id=draw_tracking.id)
            if document_status:
                queryset = queryset.filter(status=document_status)
            serializers = DrawDocumentsSerializer(queryset,many=True)
            return Response(serializers.data,status=status.HTTP_200_OK)
        except DrawTracking.DoesNotExist:
            return Response({"response":"No Draws Available for this Loan"},status=status.HTTP_404_NOT_FOUND)
        
        
class DrawDocumentStatus(APIView):
    permission_classes = [IsAuthenticated,subscription]

    def post(self, request):
        input_json = request.data
        status_action = input_json.get('status_action')
        draw_document_id = input_json.get('draw_document_id')

        try:
            my_instance = DrawDocuments.objects.get(pk=draw_document_id)
        except Document.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)

        # loan_obj = Loan.objects.get(pk=my_instance.loan_id)
        # document_detail_obj = DocumentDetail.objects.get(pk=my_instance.document_detail_id)
        user = request.user
        profile = UserProfile.objects.get(user=user)

        update_status = None
        print(profile.role_type, my_instance.status)
        if profile.role_type == "inspector" and my_instance.status == "In Review":
            if status_action == "Approve":
                update_status = "Pending Lender"
                # create_notification(loan_obj.borrower, request.user,"Document Management", f"{request.user.username} has submitted the {document_detail_obj.name} document for approval to the lender.",loan=loan_obj,notification_type= 'IN')
                # create_notification(loan_obj.lender, request.user,"Document Management", f"{request.user.username} has done the verified the {document_detail_obj.name} document and sent for approval to you.",loan=loan_obj,notification_type= 'AL')  

            elif status_action == "Reject":
                update_status = "Rejected"
                # create_notification(loan_obj.borrower, request.user,"Document Management", f"{document_detail_obj.name} document  for Loan ID :{loan_obj.loanid} has been rejected.",loan=loan_obj,notification_type= 'WA')

        elif profile.role_type == "lender" and my_instance.status == "Pending Lender":
            if status_action == "Approve":
                update_status = "Approved"
                # create_notification(loan_obj.borrower, request.user,"Document Management", f"{document_detail_obj.name} document  for Loan ID :{loan_obj.loanid} has been Approved.",loan=loan_obj,notification_type= 'SU')

            elif status_action == "Reject":
                update_status = "Rejected"
                # create_notification(loan_obj.borrower, request.user,"Document Management", f"{document_detail_obj.name} document  for Loan ID :{loan_obj.loanid} has been rejected by lender.",loan=loan_obj,notification_type= 'WA')

        if update_status:
            my_instance.status = update_status
            my_instance.save(update_fields=['status'])
            return Response({"Response":"Status Updated"},status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid action or role'}, status=status.HTTP_400_BAD_REQUEST)