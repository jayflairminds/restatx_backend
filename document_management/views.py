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
from .serializers import *
import datetime
import json
from django.db.models import Max,Sum,Q
from django.http import HttpResponse, JsonResponse
import gridfs
from pymongo import MongoClient
from django.conf import settings
from bson import ObjectId
from django.http import FileResponse
from io import BytesIO
import base64
from doc_summary_qna.doc_processing import *
from doc_summary_qna.prompts import *

client = MongoClient(settings.MONGODB['URI'],ssl=True)
db = client[settings.MONGODB['DATABASE_NAME']]
fs = gridfs.GridFS(db)


class DocumentManagement(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = DocumentSerializer(data=request.data)
        input_json = request.data

        if serializer.is_valid():
            pdf_file = request.FILES['pdf_file']
            file_id = fs.put(pdf_file, filename=pdf_file.name)
            
            document_detail= DocumentDetail.objects.get(
                name=input_json['document_name'],
                type=input_json['document_type']
            )
            print(document_detail)
            existing_instance = Document.objects.filter(
                Q(document_detail=document_detail) & Q(loan_id=request.data['loan'])
            ).first()

            if existing_instance:
                existing_file_id = ObjectId(existing_instance.file_id)
                fs.delete(existing_file_id)
                existing_instance.file_id = str(file_id)
                existing_instance.status = 'Pending'
                existing_instance.save()
                serializer = DocumentSerializer(existing_instance)
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            else:
                
                serializer.save(file_id=str(file_id), status='Pending', document_detail=document_detail)
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
        document.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
class ListOfDocument(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        try:
            input_param = request.query_params
            loan_id = input_param.get('loan_id')
            queryset = Document.objects.filter(loan_id =loan_id).order_by('-uploaded_at')
            serializer = DocumentSerializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(f"Error: {str(e)}",status=500)
        
class DocSummaryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        try:
            file_id = request.data.get("file_id")
            file_id = ObjectId(file_id)
            file = fs.get(file_id)
            # text extraction
            text = get_pdf_text(file) 
            # creating text chunks
            chunks = get_text_chunks(text)
            # creating vector store and storing it 
            get_vector_store(chunks)
            user_question = predefined_prompts()
            response = user_input(user_question)
            return Response({"response":response})
        except Exception as e:
            return Response({"Error":str(e)},status=500)