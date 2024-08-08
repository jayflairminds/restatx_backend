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

import gridfs
from pymongo import MongoClient
from django.conf import settings
client = MongoClient(settings.MONGODB['HOST'], settings.MONGODB['PORT'])
db = client[settings.MONGODB['NAME']]
fs = gridfs.GridFS(db)


class DocumentManagement(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            pdf_file = request.FILES['pdf_file']
            file_id = fs.put(pdf_file, filename=pdf_file.name)
            serializer.save(file_id=str(file_id))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)