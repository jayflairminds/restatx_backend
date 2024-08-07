from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from PyPDF2 import PdfReader
from .doc_processing import *
from .prompts import *


class UploadView(APIView):
    def post(self, request):
        try:
            uploaded_file = request.FILES.get('uploaded_file')
            print("uploaded_file",uploaded_file)
            text = get_pdf_text(uploaded_file) 
            chunks = get_text_chunks(text)
            get_vector_store(chunks)
            return Response({"Output": "File uploaded successfully"}, status=200)
        except Exception as e:
            return Response({"error":str(e)},status=500)

class ResponseView(APIView):
    def post(self,request):
        try:
            user_question = request.data.get("user_question")
            predefined_question = request.data.get("predefined_question")
            if predefined_question:
                user_question = predefined_prompts()
            response = user_input(user_question)
            return Response({"response":response},status=200)
        except Exception as e:
            return Response({"error":str(e)},status=500)
        
        


        




