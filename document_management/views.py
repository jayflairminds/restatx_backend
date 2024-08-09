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
from django.db.models import Max,Sum
from django.http import HttpResponse
import gridfs
from pymongo import MongoClient
from django.conf import settings
from bson import ObjectId

client = MongoClient(settings.MONGODB['HOST'], settings.MONGODB['PORT'])
db = client[settings.MONGODB['NAME']]
fs = gridfs.GridFS(db)


class DocumentManagement(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = DocumentSerializer(data=request.data)
        input_params = request.query_params
        input_params
        if serializer.is_valid():
            pdf_file = request.FILES['pdf_file']
            file_id = fs.put(pdf_file, filename=pdf_file.name)
            serializer.save(file_id=str(file_id))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self,request):
        try:
            input_param = request.query_params
            file_id = input_param.get('file_id')
            file_id = ObjectId(file_id)
            file = fs.get(file_id)
            response = HttpResponse(file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{file.filename}"'
            return response
        except gridfs.errors.NoFile:
            raise Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)
        
    def delete(self,request,id):
        document = Document.objects.get(pk=id)
        Document.objects.filter(id = id).delete()
        file_id = document.file_id
        file_id = ObjectId(file_id)
        fs.delete(file_id)
        return Response({'message': 'File Deleted'},status=status.HTTP_204_NO_CONTENT)
        
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